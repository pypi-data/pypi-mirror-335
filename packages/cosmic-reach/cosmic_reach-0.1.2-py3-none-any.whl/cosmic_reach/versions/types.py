import hashlib
import pathlib
import re
from dataclasses import dataclass, field
from datetime import datetime

import requests
from dataclasses_json import DataClassJsonMixin, LetterCase, cfg, dataclass_json

from .enums import Phase, ReleaseType


@dataclass(order=True)
class VersionID:
    major: int
    minor: int
    patch: int
    _is_release: bool = field(init=False, repr=False)
    prerelease: str | None = field(default=None, compare=False)

    def __post_init__(self):
        self._is_release = self.prerelease is None

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}{self.prerelease or ""}"

    @classmethod
    def parse(cls, version: str):
        major, minor, patch, prerelease = re.match(
            r"^(\d+)\.(\d+)\.(\d+)(.*)$", version
        ).groups()
        return cls(int(major), int(minor), int(patch), prerelease or None)


cfg.global_config.decoders[VersionID] = VersionID.parse
cfg.global_config.encoders[VersionID] = str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ArchiveFile:
    url: str
    sha256: str
    size: int

    def save(self, path: pathlib.Path, verify_signature: bool = True):
        response = requests.get(self.url)
        response.raise_for_status()

        if verify_signature:
            if self.size != int(response.headers.get("Content-Length")):
                raise ValueError(
                    "The downloaded file's size does not match the expected value."
                )

            sha256_hash = hashlib.sha256(response.content)
            if sha256_hash.hexdigest() != self.sha256:
                raise ValueError(
                    "The downloaded file's SHA256 does not match the expected value."
                )

        path.write_bytes(response.content)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(order=True)
class ArchiveVersion:
    id: VersionID = field(compare=True)
    type: ReleaseType = field(compare=False)
    phase: Phase = field(compare=False)
    release_time: datetime = field(compare=False)
    client: ArchiveFile | None = field(compare=False, default=None)
    server: ArchiveFile | None = field(compare=False, default=None)


@dataclass
class ArchiveVersions(DataClassJsonMixin):
    versions: list[ArchiveVersion]
    latest: dict[Phase, VersionID]

    def get_version(self, version_id: VersionID) -> ArchiveVersion:
        for version in self.versions:
            if version.id == version_id:
                return version
        raise ValueError("Version not found")

    def get_latest_version(self, phase: Phase) -> ArchiveVersion:
        return self.get_version(self.latest[phase])
