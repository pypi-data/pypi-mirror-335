from ..protocol.packets.meta import ProtocolSyncPacket
from .base import BaseClientConnection


class ClientConnection(BaseClientConnection):
    VERSION = "0.4.1"

    def setup(self):
        super().setup()
        self.on_packet(ProtocolSyncPacket, lambda s, p: self._packet_protocol_sync(p))

    def _packet_protocol_sync(self, packet: ProtocolSyncPacket):
        if self.VERSION != packet.game_version:
            raise ValueError("[Protocol Sync] Game version mismatch")

        for packet_name, packet_id in packet.packets:
            if (packet_id == 1) ^ (
                packet_name
                == "finalforeach.cosmicreach.networking.packets.meta.ProtocolSyncPacket"
            ):
                raise ValueError(
                    "[Protocol Sync] Packet with id 1 must be ProtocolSyncPacket"
                )

            if packet_name not in self.server.packet_registry._packet_ids:
                raise ValueError(f"[Protocol Sync] Unknown packet: {packet_name}")

    def handle(self):
        self.send_packet(
            ProtocolSyncPacket.create(self.server.packet_registry, self.VERSION)
        )
        super().handle()
