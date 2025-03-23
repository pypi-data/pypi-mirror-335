from ...io.types import Repeat
from ..generic import GamePacket
from ..enums import SetMusicTagsType
from ... import types


class PlaySound2DPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.sounds.PlaySound2DPacket"

    sound_id: str
    volume: float
    pitch: float
    pan: float


class PlaySound3DPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.sounds.PlaySound3DPacket"

    sound_id: str
    position: types.bin.java.Vec3
    volume: float
    pitch: float


class SetMusicTagsPacket(GamePacket):
    PACKET_NAME = (
        "finalforeach.cosmicreach.networking.packets.sounds.SetMusicTagsPacket"
    )

    tags: Repeat[str]
    type: SetMusicTagsType


class ForceSongChangePacket(GamePacket):
    PACKET_NAME = (
        "finalforeach.cosmicreach.networking.packets.sounds.ForceSongChangePacket"
    )
