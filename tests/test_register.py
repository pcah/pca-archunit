from immutabledict import immutabledict

from pca.packages.archunit.base import ArchUnit


def test_basic_archunit_does_replace_on_update() -> None:
    u1 = ArchUnit()
    u2 = ArchUnit()
    result = u1.update(u2)
    assert result is u2


def test_empty_get_archunit(register, instance) -> None:
    assert register.get_archunit_of_type_for_target(instance, ArchUnit) is None


def test_empty_get_archunits(register, instance) -> None:
    assert register.get_archunits_for_target(instance) == immutabledict()
