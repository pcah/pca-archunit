import pytest

from pca.packages.archunit.register import ArchUnitRegister


class AnyObject:
    pass


@pytest.fixture
def instance():
    return AnyObject()


@pytest.fixture
def register():
    return ArchUnitRegister()
