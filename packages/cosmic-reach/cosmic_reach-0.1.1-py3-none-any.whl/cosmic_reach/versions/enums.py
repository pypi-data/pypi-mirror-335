import enum


class ReleaseType(enum.Enum):
    RELEASE = "release"
    SNAPSHOT = "snapshot"


class Phase(enum.Enum):
    PRE_ALPHA = "pre_alpha"
    ALPHA = "alpha"
