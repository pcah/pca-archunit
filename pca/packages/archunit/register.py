import typing as t
from collections import defaultdict

from .importing import maybe_dotted_name
from .introspection import get_all_subclasses
from .units.base import ArchUnit


class ArchUnitRegister(t.Collection[ArchUnit]):
    def __init__(self) -> None:
        self._index_per_unit: t.Dict[t.Type[ArchUnit], t.Set[ArchUnit]] = defaultdict(set)
        self._index_per_target: t.Dict[t.Type, t.Set[ArchUnit]] = defaultdict(set)

    def __iter__(self) -> t.Iterator[ArchUnit]:
        yield from self.get_all_of_type(ArchUnit)

    def __contains__(self, unit: object) -> bool:
        if not isinstance(unit, ArchUnit):
            return False
        return unit in self._index_per_unit[type(unit)]

    def __len__(self) -> int:
        return sum(len(units) for k, units in self._index_per_unit.items())

    def include(self, where: t.Union[str, t.Any]) -> t.Any:
        where = maybe_dotted_name(where)
        if hasattr(where, "archunit_includeme"):
            where.archunit_includeme(self)
        return where

    def autodiscover(where: t.Union[str, t.Any]):
        where = maybe_dotted_name(where)

    def register(self, unit: ArchUnit) -> None:
        self._index_per_unit[type(unit)].add(unit)
        self._index_per_target[type(unit.target)].add(unit)

    def register_multiple(self, units: t.Iterable[ArchUnit]) -> None:
        for unit in units:
            self.register(unit)

    def clear(self) -> None:
        self._index_per_unit.clear()
        self._index_per_target.clear()

    def get_all_of_type(self, unit_type: t.Type[ArchUnit]) -> t.Iterable[ArchUnit]:
        for unit_type in get_all_subclasses(unit_type):
            yield from self._index_per_unit[unit_type]

    def get_all_for_target(self, target: t.Any) -> t.Iterable[ArchUnit]:
        for unit in self._index_per_target[type(target)]:
            if unit.target is target:
                yield unit

    def get_all_of_type_for_target(self, target: t.Any, unit_type: t.Type[ArchUnit]) -> t.Iterable[ArchUnit]:
        for unit in self._index_per_target[type(target)]:
            if (unit.target is target) and isinstance(unit, unit_type):
                yield unit
