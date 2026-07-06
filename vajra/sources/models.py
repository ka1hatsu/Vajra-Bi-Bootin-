from dataclasses import dataclass

@dataclass(frozen=True)
class ReleaseImage:
    distro: str
    version: str
    architecture: str
    image_url: str
    filename: str
    sha256: str = ""
    checksum_url: str = ""
    source_page: str = ""
    channel: str = "stable"
