import os
from pathlib import Path
from typing import Any, override

import tomlkit

from liblaf import grapes

from . import AbstractSerializer


class TOMLSerializer(AbstractSerializer):
    @override
    def load(self, fpath: str | os.PathLike[str], **kwargs) -> tomlkit.TOMLDocument:
        fpath: Path = grapes.as_path(fpath)
        with fpath.open() as fp:
            return tomlkit.load(fp, **kwargs)

    @override
    def loads(self, data: str, **kwargs) -> tomlkit.TOMLDocument:
        return tomlkit.loads(data, **kwargs)

    @override
    def save(self, fpath: str | os.PathLike[str], data: Any, **kwargs) -> None:
        fpath: Path = grapes.as_path(fpath)
        with fpath.open("w") as fp:
            tomlkit.dump(data, fp, **kwargs)

    @override
    def saves(self, data: Any, **kwargs) -> str:
        return tomlkit.dumps(data, **kwargs)


toml = TOMLSerializer()
load_toml = toml.load
loads_toml = toml.loads
save_toml = toml.save
saves_toml = toml.saves
