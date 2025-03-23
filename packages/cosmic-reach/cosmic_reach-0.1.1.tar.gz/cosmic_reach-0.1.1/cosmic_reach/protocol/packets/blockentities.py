from ...io.types import Repeat
from ..generic import GamePacket


class BlockEntityDataPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.blockentities.BlockEntityDataPacket"

    x: int
    y: int
    z: int

    # TODO


class BlockEntityScreenPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.blockentities.BlockEntityScreenPacket"

    block_entity_id: str
    x: int
    y: int
    z: int
    window_id: int


class SignsEntityPacket(GamePacket):
    PACKET_NAME = (
        "finalforeach.cosmicreach.networking.packets.blockentities.SignsEntityPacket"
    )

    x: int
    y: int
    z: int
    texts: Repeat[str]
    font_size: float
    color: int
