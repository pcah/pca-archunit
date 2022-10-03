import typing as t
from dataclasses import dataclass


class ArchUnit:
    def __init_subclass__(cls) -> None:
        dataclass(cls)

    def update(self, new: "ArchUnit") -> "ArchUnit":
        return new


ArchUnitDict = t.Dict[t.Type[ArchUnit], ArchUnit]


class ArchUnitTarget(t.Protocol):
    __archunit__: ArchUnitDict
