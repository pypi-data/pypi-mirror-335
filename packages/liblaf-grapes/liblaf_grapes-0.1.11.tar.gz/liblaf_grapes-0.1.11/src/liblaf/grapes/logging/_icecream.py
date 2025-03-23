from loguru import logger

from liblaf import grapes


def init_icecream() -> None:
    """Initializes the icecream debugging tool if the 'icecream' module is available.

    This function checks if the 'icecream' module is present in the 'grapes' package. If the module is available, it configures the output of the icecream debugger to use the custom logger with a specific log level "ICECREAM".
    """
    if not grapes.has_module("icecream"):
        return
    from icecream import ic

    ic.configureOutput(
        prefix="", outputFunction=lambda s: logger.opt(depth=2).log("ICECREAM", s)
    )
