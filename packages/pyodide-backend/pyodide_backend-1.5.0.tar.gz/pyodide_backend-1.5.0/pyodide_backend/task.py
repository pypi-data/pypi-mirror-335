from typing import Iterable, Optional
from .matplotlib_plots import FiguresManager

from contextlib import redirect_stdout, redirect_stderr, contextmanager
from traceback import format_exception_only

import io


def stdout_and_stderr_to_output(
    stdout: str, stderr: str, result: Optional[str], exception: Optional[Exception]
):
    output = []

    for figure in FiguresManager.getFigures():
        output.append(figure.getPayload())

    FiguresManager.clearFigures()

    if stdout != "":
        if stdout.endswith("\n"):
            stdout = stdout[:-1]
        output.append({"type": "output", "payload": stdout})

    if stderr != "":
        if stderr.endswith("\n"):
            stderr = stderr[:-1]
        output.append({"type": "error", "payload": stderr})

    if exception is not None:
        exception_lines = format_exception_only(type(exception), exception)
        payload = "".join(exception_lines)
        output.append({"type": "error", "payload": payload})

    if result is not None:
        output.append({"type": "result", "payload": result})

    return output


class TaskCaptureCodeExecutionOutput:
    def __init__(
        self, code_iterable: list[str], height: int = 320, width: int = 320, **kwargs
    ):
        self.code_iterable = code_iterable
        self.height = height
        self.width = width
        self.kwargs = kwargs

    def __call__(self, shell):
        stdout_stream = io.StringIO()
        stderr_stream = io.StringIO()

        exception = None

        if self.height is not None and self.width is not None:
            FiguresManager.setPlotSizes(self.height, self.width)

        with redirect_stdout(stdout_stream), redirect_stderr(stderr_stream):
            for code in self.code_iterable:
                run_cell_result = shell.run_cell(code, **self.kwargs)
                if run_cell_result.error_in_exec is not None:
                    exception = run_cell_result.error_in_exec

        result = None
        if shell.displayhook.has_result():
            result = shell.displayhook.fetch_result()

        stdout = stdout_stream.getvalue()
        stderr = stderr_stream.getvalue()
        error = (
            "".join(format_exception_only(type(exception), exception))
            if exception
            else None
        )
        raw_output = {"output_stream": stdout, "error": error}

        return (
            stdout_and_stderr_to_output(stdout, stderr, result, exception),
            raw_output,
        )


class TaskNoOutput:
    def __init__(self, code_iterable: Iterable[str], **kwargs):
        self.code_iterable = code_iterable
        self.kwargs = kwargs

    def __call__(self, shell):
        stdout_output = io.StringIO()
        stderr_output = io.StringIO()

        with redirect_stdout(stdout_output), redirect_stderr(stderr_output):
            for code in self.code_iterable:
                shell.run_cell(code, **self.kwargs)
