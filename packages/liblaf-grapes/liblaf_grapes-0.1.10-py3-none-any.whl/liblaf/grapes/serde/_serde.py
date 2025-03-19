import os
from pathlib import Path
from typing import Any, override

import autoregistry
from typing_extensions import deprecated

from liblaf import grapes

from . import AbstractSerializer, json, toml, yaml

SERIALIZERS = autoregistry.Registry()
SERIALIZERS["json"] = json
SERIALIZERS["toml"] = toml
SERIALIZERS["yaml"] = yaml
SERIALIZERS["yml"] = yaml


class AutoSerializer(AbstractSerializer):
    @override
    def load(
        self, fpath: str | os.PathLike[str], *, ext: str | None = None, **kwargs
    ) -> Any:
        serializer: AbstractSerializer = self.get_serializer(fpath, ext=ext)
        return serializer.load(fpath, **kwargs)

    @override
    def loads(self, data: str, *, ext: str | None = None, **kwargs) -> Any:
        serializer: AbstractSerializer = self.get_serializer(fpath="", ext=ext)
        return serializer.loads(data, **kwargs)

    @override
    def save(
        self,
        fpath: str | os.PathLike[str],
        data: Any,
        *,
        ext: str | None = None,
        **kwargs,
    ) -> None:
        serializer: AbstractSerializer = self.get_serializer(fpath, ext=ext)
        serializer.save(fpath, data, **kwargs)

    @override
    def saves(self, data: Any, *, ext: str | None = None, **kwargs) -> str:
        serializer: AbstractSerializer = self.get_serializer(fpath="", ext=ext)
        return serializer.saves(data, **kwargs)

    def get_serializer(
        self, fpath: str | os.PathLike[str], *, ext: str | None = None
    ) -> AbstractSerializer:
        if ext is None:
            fpath: Path = grapes.as_path(fpath)
            ext = fpath.suffix.lstrip(".")
        return SERIALIZERS[ext]  # pyright: ignore[reportReturnType]


auto = AutoSerializer()
load = auto.load
loads = auto.loads
save = auto.save
saves = auto.saves


@deprecated("Use `save()` instead of `serialize()`")
def serialize(
    fpath: str | os.PathLike[str], data: Any, *, ext: str | None = None
) -> None:
    return save(fpath, data, ext=ext)


@deprecated("Use `load()` instead of `deserialize()`")
def deserialize(fpath: str | os.PathLike[str], *, ext: str | None = None) -> Any:
    return load(fpath, ext=ext)
