import os
from pathlib import Path

class FlashCancelled(Exception): pass

def write_image(image_path, device_path, progress_callback=None, cancel_check=None, chunk_size=1024 * 1024):
    image_path=Path(image_path)
    if not image_path.is_file(): raise FileNotFoundError(f"Image not found: {image_path}")
    total=image_path.stat().st_size; written=0
    with image_path.open("rb") as source, open(device_path,"wb",buffering=0) as target:
        while True:
            if cancel_check and cancel_check(): raise FlashCancelled("Writing cancelled.")
            chunk=source.read(chunk_size)
            if not chunk: break
            target.write(chunk); written += len(chunk)
            if progress_callback: progress_callback(written,total)
        target.flush(); os.fsync(target.fileno())
    return written
