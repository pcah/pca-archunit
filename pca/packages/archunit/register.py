import typing as t
from collections import (
    ChainMap,
    defaultdict,
)
from functools import wraps

from immutabledict import immutabledict

from .base import (
    ArchUnit,
    ArchUnitDict,
    ArchUnitTarget,
)

T = t.TypeVar("T", bound=ArchUnitTarget)


class ArchUnitRegister:
    def __init__(self) -> None:
        self._contents: t.Dict[t.Type[ArchUnit], t.List[ArchUnit]] = defaultdict(list)

    def _register(self, unit: ArchUnit) -> None:
        self._contents[type(unit)].append(unit)

    def clear(self) -> None:
        self._contents.clear()

    def set_archunit(self, target: T, unit: ArchUnit) -> T:
        key = type(unit)
        if not hasattr(target, "__archunit__"):
            target.__archunit__ = immutabledict({key: unit})
        elif key not in target.__archunit__:
            target.__archunit__ = immutabledict(ChainMap({key: unit}, target.__archunit__))
        else:
            new_unit = target.__archunit__[key].update(unit)
            target.__archunit__ = immutabledict(ChainMap({key: new_unit}, target.__archunit__))
        self._register(unit)
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

    def mark(self, archunit_type: t.Type[ArchUnit]) -> t.Callable[..., t.Callable[[T], T]]:
        def constructor(*args, **kwargs) -> t.Callable[[T], T]:
            archunit = archunit_type(*args, **kwargs)

            @wraps(archunit_type)
            def setter(instance: T) -> T:
                return self.set_archunit(instance, archunit)

            return setter

        return constructor
