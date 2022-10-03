from .base import ArchUnit


class Tag(ArchUnit):
    """Tag marks any object an arbitrary string marker."""

    value: str
