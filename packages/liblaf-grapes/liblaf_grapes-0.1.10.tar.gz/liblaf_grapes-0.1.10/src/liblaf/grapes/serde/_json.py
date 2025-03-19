import json as json_
import os
from pathlib import Path
from typing import Any, override

from liblaf import grapes

from . import AbstractSerializer


class JSONSerializer(AbstractSerializer):
    @override
    def load(self, fpath: str | os.PathLike[str], **kwargs) -> Any:
        fpath: Path = grapes.as_path(fpath)
        with fpath.open() as fp:
            return json_.load(fp, **kwargs)

    @override
    def loads(self, data: str, **kwargs) -> Any:
        return json_.loads(data, **kwargs)

    @override
    def save(self, fpath: str | os.PathLike[str], data: Any, **kwargs) -> None:
        fpath: Path = grapes.as_path(fpath)
        with fpath.open("w") as fp:
            json_.dump(data, fp, **kwargs)

    @override
    def saves(self, data: Any, **kwargs) -> str:
        return json_.dumps(data, **kwargs)


json = JSONSerializer()
load_json = json.load
loads_json = json.loads
save_json = json.save
saves_json = json.saves
