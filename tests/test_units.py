from pca.packages.archunit import ArchUnit


class Foo(ArchUnit):
    bar: str
    baz: list


def test_repr() -> None:
    foo = Foo(None, bar="bar", baz=["baz1", "baz2"])
    assert repr(foo) == "Foo(target=None, bar='bar', baz=['baz1', 'baz2'])"
