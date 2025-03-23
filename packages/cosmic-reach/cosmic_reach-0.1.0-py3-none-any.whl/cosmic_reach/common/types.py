from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..types.json.accounts import Account
    from ..types.json.entities import Player


@dataclass
class RememberedPlayer:
    account: Optional["Account"] = None
    player: Optional["Player"] = None
    skin: bytes | None = None

    def is_known(self) -> bool:
        return self.account is not None and self.player is not None

    def has_skin(self) -> bool:
        return self.skin is not None
