import typing as t
from collections import ChainMap
from dataclasses import dataclass

from immutabledict import immutabledict

T = t.TypeVar("T", bound="ArchUnit")


class ArchUnit:
    def __init_subclass__(cls) -> None:
        dataclass(cls)

    def update(self, new: T) -> T:
        return new


T = t.TypeVar("T")
ArchUnitDict = t.Dict[t.Type[ArchUnit], ArchUnit]


def set_archunit(instance: T, archunit: ArchUnit) -> T:
    key = type(archunit)
    if not hasattr(instance, "__archunit__"):
        instance.__archunit__: ArchUnitDict = immutabledict({key: archunit})
    elif key not in instance.__archunit__:
        instance.__archunit__ = immutabledict(ChainMap({key: archunit}, instance.__archunit__))
    else:
        new_archunit = instance.__archunit__[key].update(archunit)
        instance.__archunit__ = immutabledict(ChainMap({key: new_archunit}, instance.__archunit__))
    return instance


def get_archunits(instance: T) -> ArchUnitDict:
    if not hasattr(instance, "__archunit__"):
        return immutabledict()
    return instance.__archunit__


def get_archunit(instance: T, archunit_type: t.Type[ArchUnit]) -> t.Optional[ArchUnitDict]:
    if not hasattr(instance, "__archunit__"):
        return None
    return instance.__archunit__[archunit_type]