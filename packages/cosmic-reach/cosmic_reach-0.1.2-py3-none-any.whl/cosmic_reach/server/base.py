import io
import socketserver
import traceback
from typing import TYPE_CHECKING, Callable

from ..protocol.generic import GamePacket

if TYPE_CHECKING:
    from .general import Server


class ConnectionReadBuffer:
    def __init__(self, handler: socketserver.StreamRequestHandler):
        self.handler = handler

    def read(self, length):
        return self.handler.rfile.read(length)

    def write(self, buf: io.BytesIO):
        return self.handler.wfile.write(buf)


class BaseClientConnection(socketserver.StreamRequestHandler):
    server: "Server"

    def __init__(self, *args, **kwargs):
        self.packet_handlers = []
        super().__init__(*args, **kwargs)

    def on_packet(
        self, packet_class: type[GamePacket] | None, handler: Callable | None = None
    ):
        if handler is None:
            return lambda handler: self.on_packet(packet_class, handler)

        self.packet_handlers.append((packet_class, handler))

    def setup(self):
        super().setup()
        self.buffer = ConnectionReadBuffer(self)

    def receive_packet(self) -> tuple[int, GamePacket]:
        return self.server.packet_registry.deserialize_packet(self.buffer)

    def handle(self):
        while True:
            try:
                packet = self.receive_packet()
            except Exception as e:
                print("----- ERROR -----")
                traceback.print_exception(e)
                print("-----------------")
            else:
                for packet_class, handler in self.packet_handlers:
                    if packet_class is None or isinstance(packet, packet_class):
                        handler(self, packet)

    def send_packet(self, packet: GamePacket):
        self.buffer.write(self.server.packet_registry.serialize_packet(packet))
