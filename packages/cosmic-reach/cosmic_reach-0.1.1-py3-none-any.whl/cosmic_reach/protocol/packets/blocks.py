from ... import types
from ...io.types import Byte
from ..generic import GamePacket


class PlaceBlockPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.blocks.PlaceBlockPacket"

    block_pos: types.bin.java.Vec3
    target_block_state: str
    item_slot_num: Byte


class BreakBlockPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.blocks.BreakBlockPacket"

    zone_id: str
    block_pos: types.bin.java.Vec3
    broken_block_state: str


class InteractBlockPacket(GamePacket):
    PACKET_NAME = (
        "finalforeach.cosmicreach.networking.packets.blocks.InteractBlockPacket"
    )

    block_id: str
    selected_slot_num: int
    interact_target: Byte
    block_pos: types.bin.java.Vec3


class BlockReplacePacket(GamePacket):
    PACKET_NAME = (
        "finalforeach.cosmicreach.networking.packets.blocks.BlockReplacePacket"
    )

    zone_id: str
    block_state_id: str
    block_pos: types.bin.java.Vec3
