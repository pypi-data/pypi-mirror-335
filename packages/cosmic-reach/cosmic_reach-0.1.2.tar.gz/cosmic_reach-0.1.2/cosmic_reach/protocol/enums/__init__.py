from enum import Enum, auto


class SlotInteractionType(Enum):
    CURSOR_SWAP = auto()
    CURSOR_RIGHT = auto()
    CURSOR_SPREAD = auto()
    CURSOR_TRASH = auto()

class SetMusicTagsType(Enum):
    ADD = auto()
    REMOVE = auto()
    SET = auto()
