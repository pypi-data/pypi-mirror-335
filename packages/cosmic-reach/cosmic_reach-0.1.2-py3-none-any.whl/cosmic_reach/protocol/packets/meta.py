from ...io.types import (
    KeyedUnion,
    Long,
    Repeat,
    Tuple,
)
from ...types.json.accounts import ItchAccount, OfflineAccount
from ..generic import GamePacket, GamePacketRegistry


class ProtocolSyncPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.meta.ProtocolSyncPacket"
    packets: Repeat[Tuple[str, int]]
    game_version: str

    @classmethod
    def create(cls, packet_registry: GamePacketRegistry, game_version: str):
        return cls(
            [
                (packet.PACKET_NAME, packet_id)
                for packet_id, packet in packet_registry._packets.items()
            ],
            game_version,
        )


class TransactionPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.meta.TransactionPacket"

    id: Long


class LoginPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.meta.LoginPacket"

    account: KeyedUnion(offline=OfflineAccount, itch=ItchAccount)


class RemovedPlayerPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.meta.RemovedPlayerPacket"

    account_id: str


class WorldRecievedGamePacket(GamePacket):
    PACKET_NAME = (
        "finalforeach.cosmicreach.networking.packets.meta.WorldRecievedGamePacket"
    )


class SetNetworkSetting(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.meta.SetNetworkSetting"

    key: str
    value: bool | int


class ChallengeLoginPacket(GamePacket):
    PACKET_NAME = (
        "finalforeach.cosmicreach.networking.packets.meta.ChallengeLoginPacket"
    )

    challenge: str


class ItchSessionTokenPacket(GamePacket):
    PACKET_NAME = (
        "finalforeach.cosmicreach.networking.packets.meta.ItchSessionTokenPacket"
    )

    session_token: str


class DisconnectPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.meta.DisconnectPacket"

    reason: str
