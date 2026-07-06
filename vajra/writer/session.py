from dataclasses import dataclass


@dataclass(frozen=True)
class TargetIdentity:
    path: str
    serial: str
    size_bytes: int

    @classmethod
    def from_device(cls, device):
        return cls(
            path=device["path"],
            serial=device.get("serial", ""),
            size_bytes=device["size_bytes"],
        )
