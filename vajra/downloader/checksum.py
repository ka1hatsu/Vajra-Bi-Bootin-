import hashlib
from pathlib import Path

def sha256_file(path, progress_callback=None, chunk_size=1024*1024):
    path=Path(path); total=path.stat().st_size; processed=0; digest=hashlib.sha256()
    with path.open("rb") as file:
        while True:
            chunk=file.read(chunk_size)
            if not chunk: break
            digest.update(chunk); processed += len(chunk)
            if progress_callback: progress_callback(processed,total)
    return digest.hexdigest()

def verify_sha256(path, expected):
    return sha256_file(path).lower() == expected.strip().lower()
