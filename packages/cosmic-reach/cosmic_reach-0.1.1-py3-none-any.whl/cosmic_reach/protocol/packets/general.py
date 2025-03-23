from ...io.types import Long, Repeat
from ..generic import GamePacket


class EndTickPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.EndTickPacket"

    world_tick: Long


class MessagePacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.MessagePacket"

    message: str
    player_unique_id: str


class ZonePacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.ZonePacket"

    set_default: bool
    zone: dict


class ChunkColumnPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.ChunkColumnPacket"

    zone_id: str
    chunk_cols: Repeat[bytes]
    x: int
    y: int
    z: int

    # TODO


class CommandPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.CommandPacket"

    command_args: Repeat[str]


class ParticleSystemPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.ParticleSystemPacket"

    id: str
    # TODO
