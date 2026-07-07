from dataclasses import dataclass
import hashlib
import hmac
from pathlib import Path


class WorkflowGuardError(RuntimeError):
    pass


@dataclass(frozen=True)
class VerifiedImage:
    path: str
    sha256: str
    size_bytes: int

    @classmethod
    def validate(cls, path, expected_sha256):
        p = Path(path).expanduser().resolve()
        expected = (expected_sha256 or "").strip().lower()

        if not p.is_file():
            raise WorkflowGuardError(f"Image does not exist: {p}")
        if p.suffix.lower() not in (".iso", ".img"):
            raise WorkflowGuardError("Image must be an ISO or IMG file.")
        if len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
            raise WorkflowGuardError("A valid verified SHA-256 digest is required.")

        before = p.stat()
        h = hashlib.sha256()
        with p.open("rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                h.update(chunk)
        after = p.stat()

        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise WorkflowGuardError(
                "Image changed while it was being verified; flashing was blocked."
            )

        actual = h.hexdigest()
        if not hmac.compare_digest(actual, expected):
            raise WorkflowGuardError(
                "Image changed after verification; verified handoff is no longer valid."
            )

        return cls(str(p), actual, after.st_size)


def require_flash_ready(path, verified_sha256):
    return VerifiedImage.validate(path, verified_sha256)
