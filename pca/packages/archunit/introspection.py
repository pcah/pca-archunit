import typing as t


def _subclasses_recursive_search(cls) -> t.Generator[t.Type, None, None]:
    yield cls
    for subclass in cls.__subclasses__():
        yield from _subclasses_recursive_search(subclass)


def get_all_subclasses(cls) -> t.Tuple[t.Type, ...]:
    """
    Returns a set of all (direct or indirect) subclasses of the `cls` class.
    """
    return tuple(_subclasses_recursive_search(cls))
