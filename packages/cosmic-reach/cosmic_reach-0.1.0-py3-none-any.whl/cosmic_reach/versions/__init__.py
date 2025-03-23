import requests

from . import enums, types

ARCHIVE_URL = "https://raw.githubusercontent.com/CRModders/CosmicArchive/refs/heads/main/versions_v2.json"


def fetch(timeout=None) -> types.ArchiveVersions:
    response = requests.get(ARCHIVE_URL, timeout=timeout)
    response.raise_for_status()
    return types.ArchiveVersions.from_dict(response.json())


__all__ = ["fetch", "types", "enums"]
