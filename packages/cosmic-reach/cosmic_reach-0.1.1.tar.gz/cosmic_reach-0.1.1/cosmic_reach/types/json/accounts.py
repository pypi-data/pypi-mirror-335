import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import requests
from dataclasses_json import DataClassJsonMixin, LetterCase, config

from cosmic_reach.io.types import Long
from cosmic_reach.protocol import packets

if TYPE_CHECKING:
    from ...client.client import Client


class Account(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.CAMEL)["dataclasses_json"]

    account_type: str
    username: str
    unique_id: str

    def get_display_name(self): ...

    def login_to(self, client: "Client"): ...


@dataclass
class OfflineAccount(Account):
    account_type: str = field(init=False, default="offline")

    username: str = field(default="offline:localPlayer")
    unique_id: str = field(
        default_factory=f"offline_id:{random.randint(0, 2147483647 + 1)}"
    )
    display_name: str = field(default="Player")

    def get_display_name(self):
        return self.display_name

    @classmethod
    def with_name(cls, name: str):
        acc = cls(
            f"offline:{name}", f"offline_id:{random.randint(0, 2147483647 + 1)}", name
        )
        return acc

    async def login_to(self, client: "Client"):
        await client.send_packet(packets.meta.LoginPacket(self))
        await client.events.login.emit()


@dataclass
class ItchAccount(Account):
    ITCH_AUTH_ROOT_URL_STR = "https://cosmicreach-auth.finalforeach.com"
    account_type: str = field(init=False, default="itch")

    username: str
    unique_id: str
    profile: "ItchProfile"
    _api_key: str = field(default=None, metadata=config(exclude=lambda x: True))

    def get_display_name(self):
        return self.profile.display_name

    @classmethod
    def from_api_key(cls, key: str):
        resp = requests.get(f"https://itch.io/api/1/{key}/me", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        assert "user" in data
        print(data["user"])
        profile = ItchProfile.from_dict(data["user"])
        acc = cls(
            f"itch:{profile.username}",
            f"itch_id:{profile.id}",
            profile,
            key,
        )
        return acc

    async def login_to(self, client: "Client"):
        @client.events.packet.only(packets.meta.ChallengeLoginPacket)
        async def on_challenge(packet: packets.meta.ChallengeLoginPacket):
            resp = requests.post(
                self.ITCH_AUTH_ROOT_URL_STR + "/verify-itch",
                json={
                    "itchApiKey": self._api_key,
                    "serverChallenge": packet.challenge,
                    "keyType": "itchApi",
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            assert "sessionToken" in data
            await client.send_packet(
                packets.meta.ItchSessionTokenPacket(data["sessionToken"])
            )
            await client.events.login.emit()

        await client.send_packet(packets.meta.LoginPacket(self))


@dataclass
class ItchProfile(DataClassJsonMixin):
    username: str
    url: str
    id: Long
    display_name: str = field(default=None)

    def __post_init__(self):
        if self.display_name is None:
            self.display_name = self.username
