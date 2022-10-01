from immutabledict import immutabledict

from pca.packages.archunit.base import (
    ArchUnit,
    get_archunit,
    get_archunits,
)


def test_basic_archunit_does_replace_on_update() -> None:
    u1 = ArchUnit()
    u2 = ArchUnit()
    result = u1.update(u2)
    assert result is u2


def test_empty_get_archunit(instance) -> None:
    assert get_archunit(instance, ArchUnit) is None


def test_empty_get_archunits(instance) -> None:
    assert get_archunits(instance) == immutabledict()
