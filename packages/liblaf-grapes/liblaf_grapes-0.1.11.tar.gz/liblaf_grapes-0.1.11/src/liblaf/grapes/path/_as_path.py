from os import PathLike
from pathlib import Path


def as_path(path: str | PathLike[str], *, expend_user: bool = True) -> Path:
    path = Path(path)
    if expend_user:
        path = path.expanduser()
    return path
