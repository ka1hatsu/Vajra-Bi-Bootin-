import hashlib, os, time, urllib.request
from dataclasses import dataclass
from pathlib import Path

class DownloadError(RuntimeError): pass
class DownloadCancelled(DownloadError): pass

@dataclass(frozen=True)
class DownloadResult:
    path: str
    bytes_written: int
    sha256: str

def sha256_file(path, chunk_size=1024*1024):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        while True:
            chunk=f.read(chunk_size)
            if not chunk: break
            h.update(chunk)
    return h.hexdigest()

def download_file(url,destination,expected_sha256=None,progress=None,cancelled=None,chunk_size=1024*1024,timeout=30):
    destination=Path(destination); destination.parent.mkdir(parents=True,exist_ok=True)
    part=Path(str(destination)+".part")
    existing=part.stat().st_size if part.exists() else 0
    headers={"User-Agent":"Vajra-Bi/8.0"}
    if existing: headers["Range"]=f"bytes={existing}-"
    try: response=urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=timeout)
    except Exception as e: raise DownloadError(str(e)) from e
    status=getattr(response,"status",None)
    if existing and status!=206: existing=0; mode="wb"
    else: mode="ab" if existing else "wb"
    length=response.headers.get("Content-Length")
    total=(existing+int(length)) if length and status==206 else (int(length) if length else None)
    written=existing; started=time.monotonic()
    try:
        with open(part,mode) as f:
            while True:
                if cancelled and cancelled(): raise DownloadCancelled("Download cancelled.")
                chunk=response.read(chunk_size)
                if not chunk: break
                f.write(chunk); written+=len(chunk)
                elapsed=max(time.monotonic()-started,.001)
                speed=max(written-existing,0)/elapsed
                eta=(total-written)/speed if total and speed>0 else None
                if progress: progress(written,total,speed,eta)
    finally: response.close()
    digest=sha256_file(part)
    if expected_sha256 and digest.lower()!=expected_sha256.lower():
        raise DownloadError(f"SHA-256 mismatch. Expected {expected_sha256}, got {digest}.")
    os.replace(part,destination)
    return DownloadResult(str(destination),written,digest)
