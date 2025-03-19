# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
"""Stage Model that use for getting stage data template from the Job Model.
The stage handle the minimize task that run in some thread (same thread at
its job owner) that mean it is the lowest executor of a workflow that can
tracking logs.

    The output of stage execution only return 0 status because I do not want to
handle stage error on this stage model. I think stage model should have a lot of
use-case, and it does not worry when I want to create a new one.

    Execution   --> Ok      --> Result with 0

                --> Error   ┬-> Result with 1 (if env var was set)
                            ╰-> Raise StageException(...)

    On the context I/O that pass to a stage object at execute process. The
execute method receives a `params={"params": {...}}` value for mapping to
template searching.
"""
from __future__ import annotations

import contextlib
import inspect
import subprocess
import sys
import time
import uuid
from abc import ABC, abstractmethod
from collections.abc import Iterator
from inspect import Parameter
from pathlib import Path
from subprocess import CompletedProcess
from textwrap import dedent
from typing import Optional, Union

from pydantic import BaseModel, Field
from pydantic.functional_validators import model_validator
from typing_extensions import Self

from .__types import DictData, DictStr, TupleStr
from .caller import TagFunc, extract_call
from .conf import config, get_logger
from .exceptions import StageException
from .result import Result, Status
from .templates import not_in_template, param2template
from .utils import (
    cut_id,
    gen_id,
    make_exec,
)

logger = get_logger("ddeutil.workflow")


__all__: TupleStr = (
    "EmptyStage",
    "BashStage",
    "PyStage",
    "CallStage",
    "TriggerStage",
    "Stage",
)


class BaseStage(BaseModel, ABC):
    """Base Stage Model that keep only id and name fields for the stage
    metadata. If you want to implement any custom stage, you can use this class
    to parent and implement ``self.execute()`` method only.

        This class is the abstraction class for any stage class.
    """

    id: Optional[str] = Field(
        default=None,
        description=(
            "A stage ID that use to keep execution output or getting by job "
            "owner."
        ),
    )
    name: str = Field(
        description="A stage name that want to logging when start execution.",
    )
    condition: Optional[str] = Field(
        default=None,
        description="A stage condition statement to allow stage executable.",
        alias="if",
    )

    @property
    def iden(self) -> str:
        """Return identity of this stage object that return the id field first.
        If the id does not set, it will use name field instead.

        :rtype: str
        """
        return self.id or self.name

    @model_validator(mode="after")
    def __prepare_running_id(self) -> Self:
        """Prepare stage running ID that use default value of field and this
        method will validate name and id fields should not contain any template
        parameter (exclude matrix template).

        :raise ValueError: When the ID and name fields include matrix parameter
            template with the 'matrix.' string value.

        :rtype: Self
        """

        # VALIDATE: Validate stage id and name should not dynamic with params
        #   template. (allow only matrix)
        if not_in_template(self.id) or not_in_template(self.name):
            raise ValueError(
                "Stage name and ID should only template with 'matrix.'"
            )

        return self

    @abstractmethod
    def execute(
        self, params: DictData, *, result: Result | None = None
    ) -> Result:
        """Execute abstraction method that action something by sub-model class.
        This is important method that make this class is able to be the stage.

        :param params: A parameter data that want to use in this execution.
        :param result: (Result) A result object for keeping context and status
            data.

        :rtype: Result
        """
        raise NotImplementedError("Stage should implement ``execute`` method.")

    def handler_execute(
        self,
        params: DictData,
        *,
        run_id: str | None = None,
        parent_run_id: str | None = None,
        result: Result | None = None,
    ) -> Result:
        """Handler execution result from the stage `execute` method.

            This stage exception handler still use ok-error concept, but it
        allows you force catching an output result with error message by
        specific environment variable,`WORKFLOW_CORE_STAGE_RAISE_ERROR`.

            Execution   --> Ok      --> Result
                                        |-status: Status.SUCCESS
                                        |-context:
                                            |-outputs: ...

                        --> Error   --> Result (if env var was set)
                                        |-status: Status.FAILED
                                        |-errors:
                                            |-class: ...
                                            |-name: ...
                                            |-message: ...

                        --> Error   --> Raise StageException(...)

            On the last step, it will set the running ID on a return result object
        from current stage ID before release the final result.

        :param params: A parameter data that want to use in this execution.
        :param run_id: (str) A running stage ID for this execution.
        :param parent_run_id: A parent workflow running ID for this release.
        :param result: (Result) A result object for keeping context and status
            data.

        :rtype: Result
        """
        result: Result = Result.construct_with_rs_or_id(
            result,
            run_id=run_id,
            parent_run_id=parent_run_id,
            id_logic=(self.name + (self.id or "")),
        )

        try:
            return self.execute(params, result=result)
        except Exception as err:
            result.trace.error(f"[STAGE]: {err.__class__.__name__}: {err}")

            if config.stage_raise_error:
                # NOTE: If error that raise from stage execution course by
                #   itself, it will return that error with previous
                #   dependency.
                if isinstance(err, StageException):
                    raise

                raise StageException(
                    f"{self.__class__.__name__}: \n\t"
                    f"{err.__class__.__name__}: {err}"
                ) from None

            # NOTE: Catching exception error object to result with
            #   error_message and error keys.
            return result.catch(
                status=Status.FAILED,
                context={
                    "errors": {
                        "class": err,
                        "name": err.__class__.__name__,
                        "message": f"{err.__class__.__name__}: {err}",
                    },
                },
            )

    def set_outputs(self, output: DictData, to: DictData) -> DictData:
        """Set an outputs from execution process to the received context. The
        result from execution will pass to value of ``outputs`` key.

            For example of setting output method, If you receive execute output
        and want to set on the `to` like;

            ... (i)   output: {'foo': bar}
            ... (ii)  to: {}

        The result of the `to` variable will be;

            ... (iii) to: {
                        'stages': {
                            '<stage-id>': {'outputs': {'foo': 'bar'}}
                        }
                    }

        :param output: An output data that want to extract to an output key.
        :param to: A context data that want to add output result.
        :rtype: DictData
        """
        if self.id is None and not config.stage_default_id:
            logger.warning(
                "Output does not set because this stage does not set ID or "
                "default stage ID config flag not be True."
            )
            return to

        # NOTE: Create stages key to receive an output from the stage execution.
        if "stages" not in to:
            to["stages"] = {}

        # NOTE: If the stage ID did not set, it will use its name instead.
        _id: str = (
            param2template(self.id, params=to)
            if self.id
            else gen_id(param2template(self.name, params=to))
        )

        errors: DictData = (
            {"errors": output.pop("errors", {})} if "errors" in output else {}
        )

        # NOTE: Set the output to that stage generated ID with ``outputs`` key.
        to["stages"][_id] = {"outputs": output, **errors}
        return to

    def is_skipped(self, params: DictData | None = None) -> bool:
        """Return true if condition of this stage do not correct. This process
        use build-in eval function to execute the if-condition.

        :raise StageException: When it has any error raise from the eval
            condition statement.
        :raise StageException: When return type of the eval condition statement
            does not return with boolean type.

        :param params: A parameters that want to pass to condition template.
        :rtype: bool
        """
        # NOTE: Return false result if condition does not set.
        if self.condition is None:
            return False

        params: DictData = {} if params is None else params

        try:
            # WARNING: The eval build-in function is very dangerous. So, it
            #   should use the `re` module to validate eval-string before
            #   running.
            rs: bool = eval(
                param2template(self.condition, params), globals() | params, {}
            )
            if not isinstance(rs, bool):
                raise TypeError("Return type of condition does not be boolean")
            return not rs
        except Exception as err:
            raise StageException(f"{err.__class__.__name__}: {err}") from err


class EmptyStage(BaseStage):
    """Empty stage that do nothing (context equal empty stage) and logging the
    name of stage only to stdout.

    Data Validate:
        >>> stage = {
        ...     "name": "Empty stage execution",
        ...     "echo": "Hello World",
        ... }
    """

    echo: Optional[str] = Field(
        default=None,
        description="A string statement that want to logging",
    )
    sleep: float = Field(
        default=0,
        description="A second value to sleep before finish execution",
        ge=0,
    )

    def execute(
        self, params: DictData, *, result: Result | None = None
    ) -> Result:
        """Execution method for the Empty stage that do only logging out to
        stdout. This method does not use the `handler_result` decorator because
        it does not get any error from logging function.

            The result context should be empty and do not process anything
        without calling logging function.

        :param params: A context data that want to add output result. But this
            stage does not pass any output.
        :param result: (Result) A result object for keeping context and status
            data.

        :rtype: Result
        """
        if result is None:  # pragma: no cov
            result: Result = Result(
                run_id=gen_id(self.name + (self.id or ""), unique=True)
            )

        result.trace.info(
            f"[STAGE]: Empty-Execute: {self.name!r}: "
            f"( {param2template(self.echo, params=params) or '...'} )"
        )
        if self.sleep > 0:
            if self.sleep > 30:
                result.trace.info(f"[STAGE]: ... sleep ({self.sleep} seconds)")
            time.sleep(self.sleep)

        return result.catch(status=Status.SUCCESS)


class BashStage(BaseStage):
    """Bash execution stage that execute bash script on the current OS.
    If your current OS is Windows, it will run on the bash in the WSL.

        I get some limitation when I run shell statement with the built-in
    subprocess package. It does not good enough to use multiline statement.
    Thus, I add writing ``.sh`` file before execution process for fix this
    issue.

    Data Validate:
        >>> stage = {
        ...     "name": "The Shell stage execution",
        ...     "bash": 'echo "Hello $FOO"',
        ...     "env": {
        ...         "FOO": "BAR",
        ...     },
        ... }
    """

    bash: str = Field(description="A bash statement that want to execute.")
    env: DictStr = Field(
        default_factory=dict,
        description=(
            "An environment variable mapping that want to set before execute "
            "this shell statement."
        ),
    )

    @contextlib.contextmanager
    def create_sh_file(
        self, bash: str, env: DictStr, run_id: str | None = None
    ) -> Iterator[TupleStr]:
        """Return context of prepared bash statement that want to execute. This
        step will write the `.sh` file before giving this file name to context.
        After that, it will auto delete this file automatic.

        :param bash: A bash statement that want to execute.
        :param env: An environment variable that use on this bash statement.
        :param run_id: A running stage ID that use for writing sh file instead
            generate by UUID4.
        :rtype: Iterator[TupleStr]
        """
        run_id: str = run_id or uuid.uuid4()
        f_name: str = f"{run_id}.sh"
        f_shebang: str = "bash" if sys.platform.startswith("win") else "sh"

        logger.debug(
            f"({cut_id(run_id)}) [STAGE]: Start create `{f_name}` file."
        )

        with open(f"./{f_name}", mode="w", newline="\n") as f:
            # NOTE: write header of `.sh` file
            f.write(f"#!/bin/{f_shebang}\n\n")

            # NOTE: add setting environment variable before bash skip statement.
            f.writelines([f"{k}='{env[k]}';\n" for k in env])

            # NOTE: make sure that shell script file does not have `\r` char.
            f.write("\n" + bash.replace("\r\n", "\n"))

        # NOTE: Make this .sh file able to executable.
        make_exec(f"./{f_name}")

        yield [f_shebang, f_name]

        # Note: Remove .sh file that use to run bash.
        Path(f"./{f_name}").unlink()

    def execute(
        self, params: DictData, *, result: Result | None = None
    ) -> Result:
        """Execute the Bash statement with the Python build-in ``subprocess``
        package.

        :param params: A parameter data that want to use in this execution.
        :param result: (Result) A result object for keeping context and status
            data.

        :rtype: Result
        """
        if result is None:  # pragma: no cov
            result: Result = Result(
                run_id=gen_id(self.name + (self.id or ""), unique=True)
            )

        bash: str = param2template(dedent(self.bash), params)

        result.trace.info(f"[STAGE]: Shell-Execute: {self.name}")
        with self.create_sh_file(
            bash=bash,
            env=param2template(self.env, params),
            run_id=result.run_id,
        ) as sh:
            rs: CompletedProcess = subprocess.run(
                sh, shell=False, capture_output=True, text=True
            )
        if rs.returncode > 0:
            # NOTE: Prepare stderr message that returning from subprocess.
            err: str = (
                rs.stderr.encode("utf-8").decode("utf-16")
                if "\\x00" in rs.stderr
                else rs.stderr
            ).removesuffix("\n")
            raise StageException(
                f"Subprocess: {err}\nRunning Statement:\n---\n"
                f"```bash\n{bash}\n```"
            )
        return result.catch(
            status=Status.SUCCESS,
            context={
                "return_code": rs.returncode,
                "stdout": rs.stdout.rstrip("\n") or None,
                "stderr": rs.stderr.rstrip("\n") or None,
            },
        )


class PyStage(BaseStage):
    """Python executor stage that running the Python statement with receiving
    globals and additional variables.

        This stage allow you to use any Python object that exists on the globals
    such as import your installed package.

    Data Validate:
        >>> stage = {
        ...     "name": "Python stage execution",
        ...     "run": 'print("Hello {x}")',
        ...     "vars": {
        ...         "x": "BAR",
        ...     },
        ... }
    """

    run: str = Field(
        description="A Python string statement that want to run with exec.",
    )
    vars: DictData = Field(
        default_factory=dict,
        description=(
            "A mapping to variable that want to pass to globals in exec."
        ),
    )

    @staticmethod
    def filter_locals(values: DictData) -> Iterator[str]:
        """Filter a locals input values.

        :param values: (DictData) A locals values that want to filter.

        :rtype: Iterator[str]
        """
        from inspect import isclass, ismodule

        for value in values:

            if (
                value == "__annotations__"
                or ismodule(values[value])
                or isclass(values[value])
            ):
                continue

            yield value

    def set_outputs(self, output: DictData, to: DictData) -> DictData:
        """Override set an outputs method for the Python execution process that
        extract output from all the locals values.

        :param output: An output data that want to extract to an output key.
        :param to: A context data that want to add output result.

        :rtype: DictData
        """
        # NOTE: The output will fileter unnecessary keys from locals.
        lc: DictData = output.get("locals", {})
        super().set_outputs(
            (
                {k: lc[k] for k in self.filter_locals(lc)}
                | {k: output[k] for k in output if k.startswith("error")}
            ),
            to=to,
        )

        # NOTE: Override value that changing from the globals that pass via the
        #   exec function.
        gb: DictData = output.get("globals", {})
        to.update({k: gb[k] for k in to if k in gb})
        return to

    def execute(
        self, params: DictData, *, result: Result | None = None
    ) -> Result:
        """Execute the Python statement that pass all globals and input params
        to globals argument on ``exec`` build-in function.

        :param params: A parameter that want to pass before run any statement.
        :param result: (Result) A result object for keeping context and status
            data.

        :rtype: Result
        """
        if result is None:  # pragma: no cov
            result: Result = Result(
                run_id=gen_id(self.name + (self.id or ""), unique=True)
            )

        # NOTE: Replace the run statement that has templating value.
        run: str = param2template(dedent(self.run), params)

        # NOTE: create custom globals value that will pass to exec function.
        _globals: DictData = (
            globals() | params | param2template(self.vars, params)
        )
        lc: DictData = {}

        # NOTE: Start exec the run statement.
        result.trace.info(f"[STAGE]: Py-Execute: {self.name}")

        # WARNING: The exec build-in function is very dangerous. So, it
        #   should use the re module to validate exec-string before running.
        exec(run, _globals, lc)

        return result.catch(
            status=Status.SUCCESS, context={"locals": lc, "globals": _globals}
        )


class CallStage(BaseStage):
    """Call executor that call the Python function from registry with tag
    decorator function in ``utils`` module and run it with input arguments.

        This stage is different with PyStage because the PyStage is just calling
    a Python statement with the ``eval`` and pass that locale before eval that
    statement. So, you can create your function complexly that you can for your
    objective to invoked by this stage object.

    Data Validate:
        >>> stage = {
        ...     "name": "Task stage execution",
        ...     "uses": "tasks/function-name@tag-name",
        ...     "args": {"FOO": "BAR"},
        ... }
    """

    uses: str = Field(
        description=(
            "A pointer that want to load function from the call registry."
        ),
    )
    args: DictData = Field(
        default_factory=dict,
        description="An arguments that want to pass to the call function.",
        alias="with",
    )

    def execute(
        self, params: DictData, *, result: Result | None = None
    ) -> Result:
        """Execute the Call function that already in the call registry.

        :raise ValueError: When the necessary arguments of call function do not
            set from the input params argument.
        :raise TypeError: When the return type of call function does not be
            dict type.

        :param params: A parameter that want to pass before run any statement.
        :type params: DictData
        :param result: (Result) A result object for keeping context and status
            data.
        :type: str | None

        :rtype: Result
        """
        if result is None:  # pragma: no cov
            result: Result = Result(
                run_id=gen_id(self.name + (self.id or ""), unique=True)
            )

        t_func: TagFunc = extract_call(param2template(self.uses, params))()

        # VALIDATE: check input task caller parameters that exists before
        #   calling.
        args: DictData = {"result": result} | param2template(self.args, params)
        ips = inspect.signature(t_func)
        if any(
            (k.removeprefix("_") not in args and k not in args)
            for k in ips.parameters
            if ips.parameters[k].default == Parameter.empty
        ):
            raise ValueError(
                f"Necessary params, ({', '.join(ips.parameters.keys())}, ), "
                f"does not set to args"
            )
        # NOTE: add '_' prefix if it wants to use.
        for k in ips.parameters:
            if k.removeprefix("_") in args:
                args[k] = args.pop(k.removeprefix("_"))

        if "result" not in ips.parameters:
            args.pop("result")

        result.trace.info(f"[STAGE]: Call-Execute: {t_func.name}@{t_func.tag}")
        rs: DictData = t_func(**param2template(args, params))

        # VALIDATE:
        #   Check the result type from call function, it should be dict.
        if not isinstance(rs, dict):
            raise TypeError(
                f"Return type: '{t_func.name}@{t_func.tag}' does not serialize "
                f"to result model, you change return type to `dict`."
            )
        return result.catch(status=Status.SUCCESS, context=rs)


class TriggerStage(BaseStage):
    """Trigger Workflow execution stage that execute another workflow. This
    the core stage that allow you to create the reusable workflow object or
    dynamic parameters workflow for common usecase.

    Data Validate:
        >>> stage = {
        ...     "name": "Trigger workflow stage execution",
        ...     "trigger": 'workflow-name-for-loader',
        ...     "params": {"run-date": "2024-08-01", "source": "src"},
        ... }
    """

    trigger: str = Field(
        description=(
            "A trigger workflow name that should already exist on the config."
        ),
    )
    params: DictData = Field(
        default_factory=dict,
        description="A parameter that want to pass to workflow execution.",
    )

    def execute(
        self, params: DictData, *, result: Result | None = None
    ) -> Result:
        """Trigger another workflow execution. It will wait the trigger
        workflow running complete before catching its result.

        :param params: A parameter data that want to use in this execution.
        :param result: (Result) A result object for keeping context and status
            data.

        :rtype: Result
        """
        # NOTE: Lazy import this workflow object.
        from . import Workflow

        if result is None:  # pragma: no cov
            result: Result = Result(
                run_id=gen_id(self.name + (self.id or ""), unique=True)
            )

        # NOTE: Loading workflow object from trigger name.
        _trigger: str = param2template(self.trigger, params=params)

        # NOTE: Set running workflow ID from running stage ID to external
        #   params on Loader object.
        workflow: Workflow = Workflow.from_loader(name=_trigger)
        result.trace.info(f"[STAGE]: Trigger-Execute: {_trigger!r}")
        return workflow.execute(
            params=param2template(self.params, params),
            result=result,
        )


# NOTE:
#   An order of parsing stage model on the Job model with ``stages`` field.
#   From the current build-in stages, they do not have stage that have the same
#   fields that because of parsing on the Job's stages key.
#
Stage = Union[
    PyStage,
    BashStage,
    CallStage,
    TriggerStage,
    EmptyStage,
]


# TODO: Not implement this stages yet
class ParallelStage(BaseStage):  # pragma: no cov
    """Parallel execution stage that execute child stages with parallel.

    Data Validate:
        >>> stage = {
        ...     "name": "Parallel stage execution.",
        ...     "parallel": [
        ...         {
        ...             "name": "Echo first stage",
        ...             "echo": "Start run with branch 1",
        ...             "sleep": 3,
        ...         },
        ...         {
        ...             "name": "Echo second stage",
        ...             "echo": "Start run with branch 2",
        ...             "sleep": 1,
        ...         },
        ...     ]
        ... }
    """

    parallel: list[Stage]
    max_parallel_core: int = Field(default=2)

    def execute(
        self, params: DictData, *, result: Result | None = None
    ) -> Result: ...


# TODO: Not implement this stages yet
class ForEachStage(BaseStage):  # pragma: no cov
    """For-Each execution stage that execute child stages with an item in list of
    item values.

    Data Validate:
        >>> stage = {
        ...     "name": "For-each stage execution",
        ...     "foreach": [1, 2, 3]
        ...     "stages": [
        ...         {
        ...             "name": "Echo stage",
        ...             "echo": "Start run with item {{ item }}"
        ...         },
        ...     ],
        ... }
    """

    foreach: list[str]
    stages: list[Stage]

    def execute(
        self, params: DictData, *, result: Result | None = None
    ) -> Result: ...


# TODO: Not implement this stages yet
class HookStage(BaseStage):  # pragma: no cov
    hook: str
    args: DictData
    callback: str

    def execute(
        self, params: DictData, *, result: Result | None = None
    ) -> Result: ...


# TODO: Not implement this stages yet
class DockerStage(BaseStage):  # pragma: no cov
    """Docker container stage execution."""

    image: str
    env: DictData = Field(default_factory=dict)
    volume: DictData = Field(default_factory=dict)
    auth: DictData = Field(default_factory=dict)

    def execute(
        self, params: DictData, *, result: Result | None = None
    ) -> Result: ...


# TODO: Not implement this stages yet
class VirtualPyStage(PyStage):  # pragma: no cov
    """Python Virtual Environment stage execution."""

    run: str
    vars: DictData

    def create_py_file(self, py: str, run_id: str | None): ...
