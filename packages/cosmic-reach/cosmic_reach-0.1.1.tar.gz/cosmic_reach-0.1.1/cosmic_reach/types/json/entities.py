import enum
from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin, LetterCase, config

from .java import Vec3


class PlayerGamemode(enum.Enum):
    SURVIVAL = "survival"
    CREATIVE = "creative"


@dataclass
class UniqueID(DataClassJsonMixin):
    time: int
    rand: int
    number: int


@dataclass
class LocalBoundingBox(DataClassJsonMixin):
    min: Vec3
    max: Vec3
    cnt: Vec3
    dim: Vec3


@dataclass
class Entity(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.CAMEL)["dataclasses_json"]

    unique_id: UniqueID
    position: Vec3
    last_position: Vec3
    view_position_offset: Vec3
    local_bounding_box: dict
    acceleration: Vec3 | None = None
    age: float | None = None
    last_view_direction: Vec3 = None
    view_direction: Vec3 = None
    footstep_timer: float = None
    is_on_ground: bool = None
    collided_y: bool = None


@dataclass
class SlotContainer(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.CAMEL)["dataclasses_json"]

    slots: str
    number_of_slots: int


@dataclass
class Player(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.CAMEL)["dataclasses_json"]

    gamemode: PlayerGamemode
    zone_id: str
    is_prone: bool
    entity: Entity
    inventory: SlotContainer
