from dataclasses import dataclass
from pathlib import Path


class ImageHandoffError(ValueError):
    pass


@dataclass(frozen=True)
class ImageHandoff:
    path: str
    source: str
    distro_name: str = ""
    verified_sha256: str = ""

    @classmethod
    def from_download(cls, path, distro_name="", verified_sha256=""):
        p = Path(path).expanduser().resolve()
        if not p.is_file():
            raise ImageHandoffError(f"Downloaded image does not exist: {p}")
        if p.suffix.lower() not in (".iso", ".img"):
            raise ImageHandoffError("Downloaded file must be an ISO or IMG image.")
        return cls(str(p), "download", distro_name, (verified_sha256 or "").lower())
