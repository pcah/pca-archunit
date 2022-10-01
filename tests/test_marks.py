from pca.packages.archunit import marks
from pca.packages.archunit.base import (
    get_archunit,
    get_archunits,
)
from pca.packages.archunit.common import Tags
from pca.packages.archunit.container import Application


def test_cross_setting_archunits(instance) -> None:
    tags = marks.tags("tag")
    application = marks.application("application")
    tags(instance)
    application(instance)
    assert dict(get_archunits(instance)) == {
        Tags: Tags("tag"),
        Application: Application("application"),
    }


def test_tag_mark() -> None:
    decorator = marks.tags("name for the tag")
    assert decorator.__name__ == Tags.__name__
    assert decorator.__doc__ == Tags.__doc__


def test_tag_mark_instance(instance) -> None:
    decorator = marks.tags("name for the tag")
    result = decorator(instance)
    assert result is instance
    assert dict(get_archunits(instance)) == {Tags: Tags("name for the tag")}


def test_application_mark() -> None:
    decorator = marks.application("my application")
    assert decorator.__name__ == Application.__name__
    assert decorator.__doc__ == Application.__doc__


def test_application_mark_instance(instance) -> None:
    decorator = marks.application("my application")
    result = decorator(instance)
    assert result is instance
    assert dict(get_archunits(instance)) == {Application: Application("my application")}


def test_double_mark_application_replaces_unit(instance) -> None:
    d1 = marks.application("application1")
    d2 = marks.application("application2")
    d1(instance)
    assert get_archunit(instance, Application) == Application("application1")
    # assigning Application unit for the second time
    d2(instance)
    assert get_archunit(instance, Application) == Application("application2")
