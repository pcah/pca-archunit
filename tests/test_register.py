import typing as t

import pytest

from pca.packages.archunit import (
    ArchUnit,
    ArchUnitRegister,
)


class Foo(ArchUnit):
    pass


class Baz(Foo):
    pass


class Quax(ArchUnit):
    pass


@pytest.fixture
def example_units_by_id() -> t.Dict[int, ArchUnit]:
    return {
        0: Foo("1"),
        1: Baz("0"),
        2: Baz("1"),
        3: Quax("1"),
    }


@pytest.fixture
def example_units(example_units_by_id: t.Dict[int, ArchUnit]) -> t.List[ArchUnit]:
    return [example_units_by_id[i] for i in range(4)]


@pytest.fixture
def example_register(register: ArchUnitRegister, example_units: t.List[ArchUnit]) -> ArchUnitRegister:
    register.register_multiple(example_units)
    return register


def test_clear(register: ArchUnitRegister) -> None:
    unit = ArchUnit(None)
    register.register(unit)
    assert list(register.get_all_of_type(ArchUnit)) == [unit]
    register.clear()
    assert list(register.get_all_of_type(ArchUnit)) == []


def test_empty_register_as_collection(register: ArchUnitRegister) -> None:
    unit = ArchUnit(None)
    assert unit not in register
    assert len(register) == 0
    assert list(register) == []


def test_example_register_as_collection(example_register: ArchUnitRegister, example_units: t.List[ArchUnit]) -> None:
    assert len(example_register) == 4
    assert example_units[0] in example_register
    assert set(example_register) == set(example_units)
    assert "0" not in example_register


class TestGetAllOfType:
    def test_empty(self, register: ArchUnitRegister) -> None:
        assert set(register.get_all_of_type(ArchUnit)) == set()

    def test_all(self, example_register: ArchUnitRegister, example_units: t.List[ArchUnit]) -> None:
        assert set(example_register.get_all_of_type(ArchUnit)) == set(example_units)

    def test_quax(self, example_register: ArchUnitRegister, example_units_by_id: t.Dict[int, ArchUnit]) -> None:
        assert set(example_register.get_all_of_type(Quax)) == {example_units_by_id[3]}

    def test_foo(self, example_register: ArchUnitRegister, example_units_by_id: t.Dict[int, ArchUnit]) -> None:
        assert set(example_register.get_all_of_type(Foo)) == {
            example_units_by_id[0],
            example_units_by_id[1],
            example_units_by_id[2],
        }

    def test_baz(self, example_register: ArchUnitRegister, example_units_by_id: t.Dict[int, ArchUnit]) -> None:
        assert set(example_register.get_all_of_type(Baz)) == {
            example_units_by_id[1],
            example_units_by_id[2],
        }


class TestGetAllForTarget:
    def test_empty_register(self, register: ArchUnitRegister) -> None:
        assert set(register.get_all_for_target(ArchUnit)) == set()

    def test_example_register(
        self,
        example_register: ArchUnitRegister,
        example_units_by_id: t.Dict[int, ArchUnit],
    ) -> None:
        assert set(example_register.get_all_for_target("0")) == {example_units_by_id[1]}
        assert set(example_register.get_all_for_target("1")) == {
            example_units_by_id[0],
            example_units_by_id[2],
            example_units_by_id[3],
        }


class TestGetAllOfTypeForTarget:
    def test_empty_register(self, register: ArchUnitRegister) -> None:
        assert set(register.get_all_of_type_for_target("0", ArchUnit)) == set()

    def test_example_register_0_all(
        self,
        example_register: ArchUnitRegister,
        example_units_by_id: t.Dict[int, ArchUnit],
    ) -> None:
        assert set(example_register.get_all_of_type_for_target("0", ArchUnit)) == {example_units_by_id[1]}

    def test_example_register_0_quax(
        self,
        example_register: ArchUnitRegister,
    ) -> None:
        assert set(example_register.get_all_of_type_for_target("0", Quax)) == set()

    def test_example_register_1_foo(
        self,
        example_register: ArchUnitRegister,
        example_units_by_id: t.Dict[int, ArchUnit],
    ) -> None:
        assert set(example_register.get_all_of_type_for_target("1", Foo)) == {
            example_units_by_id[0],
            example_units_by_id[2],
        }

    def test_example_register_1_baz(
        self,
        example_register: ArchUnitRegister,
        example_units_by_id: t.Dict[int, ArchUnit],
    ) -> None:
        assert set(example_register.get_all_of_type_for_target("1", Baz)) == {
            example_units_by_id[2],
        }


# def test_empty_get_archunit(register, instance) -> None:
#     assert register.get_archunit_of_type_for_target(instance, ArchUnit) is None


# def test_empty_get_archunit(register, instance) -> None:
#     assert register.get_archunit_of_type_for_target(instance, ArchUnit) is None


# def test_empty_get_archunits(register, instance) -> None:
#     assert register.get_archunits_for_target(instance) == immutabledict()
