from pathlib import Path
from urllib.request import Request, urlopen

class DownloadCancelled(Exception):
    pass

def download_file(url, destination, progress_callback=None, cancel_check=None, chunk_size=1024*1024):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    request = Request(url, headers={"User-Agent": "Vajra-Bi-Bootin/0.3"})
    downloaded = 0
    try:
        with urlopen(request, timeout=30) as response, partial.open("wb") as output:
            total = int(response.headers.get("Content-Length", 0))
            while True:
                if cancel_check and cancel_check():
                    raise DownloadCancelled("Download cancelled")
                chunk = response.read(chunk_size)
                if not chunk: break
                output.write(chunk)
                downloaded += len(chunk)
                if progress_callback: progress_callback(downloaded, total)
        partial.replace(destination)
        return destination
    except Exception:
        if partial.exists(): partial.unlink()
        raise
