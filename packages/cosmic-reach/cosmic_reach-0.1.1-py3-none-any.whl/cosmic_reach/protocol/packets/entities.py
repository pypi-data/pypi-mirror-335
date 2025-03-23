from ... import types
from ...io.types import (
    Short,
)
from ..generic import GamePacket


class PlayerPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.entities.PlayerPacket"

    account_type: str
    account: (
        types.accounts.OfflineAccount
    )  # OneOfMapped(String, {"offline": types.accounts.OfflineAccount})
    player: types.json.entities.Player
    just_joined: bool


class PlayerPositionPacket(GamePacket):
    PACKET_NAME = (
        "finalforeach.cosmicreach.networking.packets.entities.PlayerPositionPacket"
    )

    player_unique_id: str
    position: types.bin.java.Vec3
    view_dir: types.bin.java.Vec3
    view_dir_off: types.bin.java.Vec3
    player_flags: int
    zone_id: str


class EntityPositionPacket(GamePacket):
    PACKET_NAME = (
        "finalforeach.cosmicreach.networking.packets.entities.EntityPositionPacket"
    )

    entity_unique_id: types.bin.entities.UniqueID
    position: types.bin.java.Vec3
    view_dir: types.bin.java.Vec3
    view_dir_off: types.bin.java.Vec3


class NoClipPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.entities.NoClipPacket"

    should_no_clip: bool


class SpawnEntityPacket(GamePacket):
    PACKET_NAME = (
        "finalforeach.cosmicreach.networking.packets.entities.SpawnEntityPacket"
    )

    entity_type_id: str
    # TODO


class DespawnEntityPacket(GamePacket):
    PACKET_NAME = (
        "finalforeach.cosmicreach.networking.packets.entities.DespawnEntityPacket"
    )

    unique_entity_id: types.bin.entities.UniqueID


class AttackEntityPacket(GamePacket):
    PACKET_NAME = (
        "finalforeach.cosmicreach.networking.packets.entities.AttackEntityPacket"
    )

    unique_entity_id: types.bin.entities.UniqueID


class InteractEntityPacket(GamePacket):
    PACKET_NAME = (
        "finalforeach.cosmicreach.networking.packets.entities.InteractEntityPacket"
    )

    unique_entity_id: types.bin.entities.UniqueID
    item_slot_num: Short


class HitEntityPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.entities.HitEntityPacket"

    unique_entity_id: types.bin.entities.UniqueID
    amount: float


class MaxHPEntityPacket(GamePacket):
    PACKET_NAME = (
        "finalforeach.cosmicreach.networking.packets.entities.MaxHPEntityPacket"
    )

    unique_entity_id: types.bin.entities.UniqueID
    amount: float


class RespawnPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.entities.RespawnPacket"


class PlayerSkinPacket(GamePacket):
    PACKET_NAME = (
        "finalforeach.cosmicreach.networking.packets.entities.PlayerSkinPacket"
    )

    player_unique_id: str
    texture_bytes: bytes
