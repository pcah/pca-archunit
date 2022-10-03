import typing as t
from dataclasses import dataclass


@dataclass(frozen=True)
class ArchUnit:
    target: t.Any

    def __init_subclass__(cls) -> None:
        dataclass(cls, frozen=True)  # type: ignore
