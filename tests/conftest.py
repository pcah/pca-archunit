import pytest


class AnyObject:
    pass


@pytest.fixture
def instance():
    return AnyObject()
