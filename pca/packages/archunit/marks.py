import typing as t
from functools import wraps

from .base import (
    ArchUnit,
    ArchUnitTarget,
    set_archunit,
)
from .common import Tags
from .container import Application

T = t.TypeVar("T", bound=ArchUnitTarget)


def mark(archunit_type: t.Type[ArchUnit]) -> t.Callable[..., t.Callable[[T], T]]:
    def constructor(*args, **kwargs) -> t.Callable[[T], T]:
        archunit = archunit_type(*args, **kwargs)

        @wraps(archunit_type)
        def setter(instance: T) -> T:
            return set_archunit(instance, archunit)

        return setter

    return constructor


application = mark(Application)
tags = mark(Tags)
