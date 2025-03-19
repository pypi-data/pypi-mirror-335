import os
import tempfile
from pathlib import Path
from typing import Any

from liblaf import grapes


class AbstractSerializer:
    def load(self, fpath: str | os.PathLike[str], **kwargs) -> Any:
        if type(self).loads is not AbstractSerializer.loads:
            fpath: Path = grapes.as_path(fpath)
            return self.loads(fpath.read_text(), **kwargs)
        raise NotImplementedError

    def loads(self, data: str, **kwargs) -> Any:
        if type(self).load is not AbstractSerializer.load:
            with tempfile.NamedTemporaryFile("w") as fp:
                fp.write(data)
                return self.load(Path(fp.name), **kwargs)
        raise NotImplementedError

    def save(self, fpath: str | os.PathLike[str], data: Any, **kwargs) -> None:
        if type(self).saves is not AbstractSerializer.saves:
            fpath: Path = grapes.as_path(fpath)
            fpath.write_text(self.saves(data, **kwargs))
        raise NotImplementedError

    def saves(self, data: Any, **kwargs) -> str:
        if type(self).save is not AbstractSerializer.save:
            with tempfile.NamedTemporaryFile("w") as fp:
                self.save(Path(fp.name), data, **kwargs)
                return fp.read()
        raise NotImplementedError
