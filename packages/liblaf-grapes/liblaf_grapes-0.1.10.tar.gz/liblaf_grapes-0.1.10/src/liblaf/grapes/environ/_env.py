import functools

from environs import Env


@functools.lru_cache
def init_env(prefix: str | None = "LIBLAF_") -> Env:
    """Initialize and return an environment configuration.

    This function creates an instance of the Env class with the specified prefix, reads the environment variables, and returns the configured environment.

    Args:
        prefix: The prefix to use for environment variables.

    Returns:
        The initialized environment configuration.
    """
    env = Env(prefix=prefix)
    env.read_env()
    return env
