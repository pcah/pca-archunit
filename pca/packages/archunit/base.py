import typing as t
from collections import (
    ChainMap,
    defaultdict,
)
from dataclasses import dataclass

from immutabledict import immutabledict

T = t.TypeVar("T", bound="ArchUnitTarget")
ArchUnitDict = t.Dict[t.Type["ArchUnit"], "ArchUnit"]


class ArchUnit:
    def __init_subclass__(cls) -> None:
        dataclass(cls)

    def update(self, new: "ArchUnit") -> "ArchUnit":
        return new


class ArchUnitTarget(t.Protocol):
    __archunit__: ArchUnitDict


class ArchUnitRegister:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._register = defaultdict(list)

    def register(self, unit: ArchUnit) -> None:
        self._register[type(unit)].append(unit)

    def clear(self) -> None:
        self._register.clear()

    def set_archunit(self, target: T, unit: ArchUnit) -> T:
        key = type(unit)
        if not hasattr(target, "__unit__"):
            target.__unit__ = immutabledict({key: unit})
        elif key not in target.__unit__:
            target.__unit__ = immutabledict(ChainMap({key: unit}, target.__unit__))
        else:
            new_unit = target.__unit__[key].update(unit)
            target.__unit__ = immutabledict(ChainMap({key: new_unit}, target.__unit__))
        self.register(unit)
        return target

    def get_archunits_for_target(self, target: ArchUnitTarget) -> ArchUnitDict:
        if not hasattr(target, "__archunit__"):
            return immutabledict()
        return target.__archunit__

    def get_archunit_of_type_for_target(
        self, target: ArchUnitTarget, archunit_type: t.Type[ArchUnit]
    ) -> t.Optional[ArchUnit]:
        if not hasattr(target, "__archunit__"):
            return None
        return target.__archunit__[archunit_type]
