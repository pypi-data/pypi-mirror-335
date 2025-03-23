from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin


@dataclass
class Vec3(DataClassJsonMixin):
    x: float = 0
    y: float = 0
    z: float = 0
