from collections import defaultdict

from ..common.events import FilterableListenableEvent, ListenableEvent
from ..common.types import RememberedPlayer
from ..protocol import GamePacketRegistry, packets
from ..types.json.accounts import Account
from .base import BaseClient


class Client(BaseClient):
    """A client implementing basic functionality,
    like reading chat messages
    """

    VERSION: str = "0.4.4"
    "The version the client is made for"
    account: Account = None
    "The account the client is or will be logged in with"
    in_world: bool = False
    "Whether the client has logged in yet"

    class Events(BaseClient.Events):
        login: ListenableEvent
        join: ListenableEvent
        player_join: FilterableListenableEvent
        chat: ListenableEvent

    events: Events

    def __init__(self, account: Account):
        super().__init__()

        self.account = account
        self.players: dict[str, RememberedPlayer] = defaultdict(RememberedPlayer)
        self.events.packet.add_handler(
            self._handle_protocol_sync, packets.meta.ProtocolSyncPacket
        )
        self.events.packet.add_handler(
            self._handle_player_packet, packets.entities.PlayerPacket
        )
        self.events.packet.add_handler(
            self._handle_player_skin_packet, packets.entities.PlayerSkinPacket
        )
        self.events.packet.add_handler(
            self._handle_zone_packet, packets.general.ZonePacket
        )
        self.events.packet.add_handler(
            lambda p: self.events.chat.emit(p.player_unique_id, p.message),
            packets.general.MessagePacket,
        )
        self.events.login.add_handler(self._handle_login_finished)

    async def _handle_login_finished(self):
        self.in_world = True

    async def _handle_zone_packet(self, packet: packets.general.ZonePacket):
        await self.send_packet(packets.meta.WorldRecievedGamePacket())
        self.in_world = True
        await self.events.join.emit()

    async def _handle_player_packet(self, packet: packets.entities.PlayerPacket):
        if packet.account.unique_id not in self.players:
            self.players[packet.account.unique_id] = RememberedPlayer(
                packet.account, packet.player, skin=None
            )
        if packet.just_joined:
            await self.events.player_join.emit(
                packet.account.unique_id,
                self.players[packet.account.unique_id],
            )

    async def _handle_player_skin_packet(
        self, packet: packets.entities.PlayerSkinPacket
    ):
        self.players[packet.player_unique_id].skin = packet.texture_bytes

    async def _handle_protocol_sync(self, packet: packets.meta.ProtocolSyncPacket):
        if self.VERSION != packet.game_version:
            raise ValueError(f"[Protocol Sync] Game version mismatch: Client is on {self.VERSION}, server on {packet.game_version}")

        new_packets = GamePacketRegistry()

        for packet_name, packet_id in packet.packets:
            if packet_name not in self.packet_registry._packet_ids:
                raise ValueError(f"[Protocol Sync] Unknown packet: {packet_name}")

            if (packet_id == 1) ^ (
                packet_name
                == "finalforeach.cosmicreach.networking.packets.meta.ProtocolSyncPacket"
            ):
                raise ValueError(
                    "[Protocol Sync] Packet with id 1 must be ProtocolSyncPacket"
                )

            new_packets.register(
                self.packet_registry.get_packet_by_id(
                    self.packet_registry._packet_ids[packet_name]
                ),
                packet_id,
            )

        self.packet_registry = new_packets

        await self.send_packet(
            packets.meta.ProtocolSyncPacket.create(self.packet_registry, self.VERSION)
        )
        await self.account.login_to(self)

    def get_player(self, unique_id: str):
        """Get a player by his :code:``uniqueId``

        :raises KeyError: If the player is not known to the client
        """
        player = self.players[unique_id]
        if not player.is_known():
            raise KeyError(f"Player with uniqueId {unique_id} is unknown")
        return player

    async def send_chat(self, message: str):
        """Send a chat message

        :param message: The message to send
        :param display_name_prefix: Whether to prefix the display name
        """
        await self.send_packet(
            packets.general.MessagePacket(
                ((self.account.display_name + "> ") if not self.in_world else "")
                + message,
                "",
            )
        )
