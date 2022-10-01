import typing as t

from .base import ArchUnit


class Tags(ArchUnit):
    """Tags marks any object with a bunch of arbitrary marker."""

    values: t.Tuple[str]

    def __init__(self, *tags) -> None:
        self.values = tuple(tags)

    def update(self, new: "Tags") -> "Tags":
        return self.__class__(*(self.values + new.values))

    def __repr__(self) -> str:
        values_str = ", ".join(f"'{v}'" for v in self.values)
        return f"{self.__class__.__name__}({values_str})"
