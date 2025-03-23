import asyncio
import io
import socket
import traceback
from collections import defaultdict

from ..common.events import FilterableListenableEvent, ListenableEvent
from ..protocol import GamePacket, GamePacketRegistry, get_packet_registry


class SocketReadBuffer:
    def __init__(self, sock: socket.socket):
        self.sock = sock

    def read(self, length):
        read = self.sock.recv(length)
        while len(read) < length:
            read += self.sock.recv(length - len(read))

    def write(self, buf: io.BytesIO):
        return self.sock.send(buf)


class BaseClient:
    "A barebones client, just being able to send and receive packets, nothing more."

    sock: socket.socket
    buffer: SocketReadBuffer
    packet_registry: GamePacketRegistry

    class Events:
        packet: FilterableListenableEvent
        connect: ListenableEvent

        def __init__(self):
            super().__init__()
            for key, typ in self.__class__.__annotations__.items():
                setattr(self, key, typ())
            for base in self.__class__.__bases__:
                for key, typ in base.__annotations__.items():
                    setattr(self, key, typ())

    events: Events

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer = SocketReadBuffer(self.sock)
        self.rlock = asyncio.Lock()
        self.wlock = asyncio.Lock()
        self.event_handlers = defaultdict(list)
        self.packet_registry = get_packet_registry()

        self.events = self.Events()

    async def send_packet(self, packet: GamePacket):
        "Send a packet to the connected server"
        await self.wlock.acquire()
        self.buffer.write(self.packet_registry.serialize_packet(packet))
        self.wlock.release()

    async def receive_packet(self) -> GamePacket:
        """Receive on packet from the connected server

        If no packet is waiting in the buffer, this function will wait until one package is received.
        """
        await self.rlock.acquire()
        try:
            result = self.packet_registry.deserialize_packet(self.buffer)
        except ConnectionAbortedError:
            raise SystemExit
        finally:
            self.rlock.release()
        return result

    async def connect(self, host: str = "localhost", port: int = 47137):
        """Connect the client to a remote server

        :param host: The host of the remote server
        :param port: The port of the remote server
        """
        self.sock.connect((host, port))
        await self.events.connect.emit()

    async def receive_packets(self):
        "Infinitely receive and handle packets"
        while self.sock:
            try:
                packet = await self.receive_packet()
            except Exception as e:
                traceback.print_exception(e)
                print("-----------------")
            else:
                await self.events.packet.emit(type(packet), packet)

    def start(self):
        "Infinitely receive and handle packets"
        asyncio.get_event_loop().create_task(self.receive_packets())

    async def handle_infinitely(self):
        "Infinitely receive and handle packets"
        asyncio.get_event_loop().create_task(self.receive_packets())
