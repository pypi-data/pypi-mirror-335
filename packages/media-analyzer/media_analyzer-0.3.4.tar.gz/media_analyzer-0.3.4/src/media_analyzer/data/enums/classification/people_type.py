from enum import StrEnum, auto


class PeopleType(StrEnum):
    """People types enum."""

    SELFIE = auto()
    GROUP = auto()
    PORTRAIT = auto()
    CROWD = auto()
