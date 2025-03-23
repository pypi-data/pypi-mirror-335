import socketserver

from ..protocol import get_packet_registry
from .base import BaseClientConnection


class Server(socketserver.TCPServer):
    def __init__(self, handler: BaseClientConnection):
        self.packet_registry = get_packet_registry()
        super().__init__(("localhost", 47137), handler, bind_and_activate=False)

    def serve(self, host: str = "localhost", port: int = 47137):
        self.server_address = (host, port)
        self.server_bind()
        self.server_activate()
        self.serve_forever()
