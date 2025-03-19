import functools

import rich.pretty
import rich.traceback
from rich.console import Console
from rich.style import Style
from rich.theme import Theme


@functools.cache
def logging_theme() -> Theme:
    """Returns a Theme object that defines the styles for different logging levels.

    The styles are inspired by the loguru library and include the following levels:

    - notset: Dimmed style
    - trace: Cyan color, bold
    - debug: Blue color, bold
    - icecream: Magenta color, bold
    - info: Bold
    - success: Green color, bold
    - warning: Yellow color, bold
    - error: Red color, bold
    - critical: Red color, bold, reversed

    Returns:
        A Theme object with the specified styles for logging levels.
    """
    # [loguru/loguru/_defaults.py at c490ce0534c6e176306f339a92c221dc6f41a6a7 · Delgan/loguru](https://github.com/Delgan/loguru/blob/c490ce0534c6e176306f339a92c221dc6f41a6a7/loguru/_defaults.py)
    return Theme(
        {
            "logging.level.notset": Style(dim=True),
            "logging.level.trace": Style(color="cyan", bold=True),
            "logging.level.debug": Style(color="blue", bold=True),
            "logging.level.icecream": Style(color="magenta", bold=True),
            "logging.level.info": Style(bold=True),
            "logging.level.success": Style(color="green", bold=True),
            "logging.level.warning": Style(color="yellow", bold=True),
            "logging.level.error": Style(color="red", bold=True),
            "logging.level.critical": Style(color="red", bold=True, reverse=True),
        }
    )


@functools.cache
def logging_console() -> Console:
    """Create and return a rich Console object configured for logging.

    The console is set to use a custom logging theme and output to stderr.

    Returns:
        A rich Console object configured for logging.
    """
    return rich.console.Console(theme=logging_theme(), stderr=True)


def init_rich(*, show_locals: bool = True) -> None:
    """Initialize rich logging for pretty printing and tracebacks.

    This function sets up rich's pretty printing and traceback handling
    for the logging console.

    Args:
        show_locals: If True, local variables will be shown in tracebacks.
    """
    rich.pretty.install(console=logging_console())
    rich.traceback.install(console=logging_console(), show_locals=show_locals)
