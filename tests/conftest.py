import pytest

from pca.packages.archunit.base import ArchUnitRegister


class AnyObject:
    pass


@pytest.fixture
def instance():
    return AnyObject()


@pytest.fixture
def register():
    return ArchUnitRegister()
