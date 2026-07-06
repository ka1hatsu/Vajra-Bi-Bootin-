import hashlib
from pathlib import Path

def sha256_file(path,chunk_size=1024*1024):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        while True:
            chunk=f.read(chunk_size)
            if not chunk: break
            h.update(chunk)
    return h.hexdigest()

def inspect_record(record):
    path=Path(record.path)
    if not path.is_file(): return "missing",""
    if not record.expected_sha256: return "untrusted",""
    actual=sha256_file(path)
    if actual.lower()!=record.expected_sha256.lower(): return "modified",actual
    return "verified",actual
