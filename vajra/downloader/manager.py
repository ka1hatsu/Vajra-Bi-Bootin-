import hashlib
import hmac
import os
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from vajra.sources.security import open_download_url


class DownloadError(RuntimeError):
    pass


class DownloadCancelled(DownloadError):
    pass


@dataclass(frozen=True)
class DownloadResult:
    path: str
    bytes_written: int
    sha256: str


def sha256_file(path, chunk_size=1024 * 1024):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _normalise_expected_sha256(value):
    if not value:
        return None
    digest = value.strip().lower()
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise DownloadError("Expected SHA-256 metadata is malformed.")
    return digest


def download_file(url, destination, expected_sha256=None, progress=None, cancelled=None, chunk_size=1024 * 1024, timeout=30):
    expected_sha256 = _normalise_expected_sha256(expected_sha256)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    part = Path(str(destination) + ".part")
    existing = part.stat().st_size if part.exists() else 0
    headers = {"User-Agent": "Vajra-Bi/8.0"}
    if existing:
        headers["Range"] = f"bytes={existing}-"

    try:
        request = urllib.request.Request(url, headers=headers)
        response = open_download_url(request, timeout=timeout)
    except Exception as exc:
        raise DownloadError(str(exc)) from exc

    status = getattr(response, "status", None)
    if existing and status != 206:
        existing = 0
        mode = "wb"
    else:
        mode = "ab" if existing else "wb"

    length = response.headers.get("Content-Length")
    try:
        response_length = int(length) if length else None
    except (TypeError, ValueError):
        response.close()
        raise DownloadError("Server returned an invalid Content-Length header.")

    total = (
        existing + response_length
        if response_length is not None and status == 206
        else response_length
    )
    written = existing
    started = time.monotonic()

    try:
        with open(part, mode) as stream:
            while True:
                if cancelled and cancelled():
                    raise DownloadCancelled("Download cancelled.")
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                stream.write(chunk)
                written += len(chunk)
                elapsed = max(time.monotonic() - started, 0.001)
                speed = max(written - existing, 0) / elapsed
                eta = (total - written) / speed if total and speed > 0 else None
                if progress:
                    progress(written, total, speed, eta)
    finally:
        response.close()

    digest = sha256_file(part)
    if expected_sha256 and not hmac.compare_digest(digest.lower(), expected_sha256):
        raise DownloadError(
            f"SHA-256 mismatch. Expected {expected_sha256}, got {digest}."
        )

    os.replace(part, destination)
    return DownloadResult(str(destination), written, digest)
