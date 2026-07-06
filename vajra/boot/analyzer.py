from dataclasses import dataclass
from pathlib import Path
import subprocess
@dataclass(frozen=True)
class ImageAnalysis:
    image_type:str
    size_bytes:int
    uefi_hint:bool
    bios_hint:bool
    note:str
def analyze_image(image_path):
    p=Path(image_path)
    if not p.is_file(): raise FileNotFoundError(f"Image not found: {p}")
    try:
        r=subprocess.run(["file","-b",str(p)],capture_output=True,text=True,timeout=10)
        desc=r.stdout.lower() if r.returncode==0 else ""
    except Exception: desc=""
    kind="ISO" if p.suffix.lower()==".iso" else "IMG" if p.suffix.lower()==".img" else "Unknown"
    return ImageAnalysis(kind,p.stat().st_size,"uefi" in desc or "efi" in desc,"bootable" in desc or "boot sector" in desc,"Raw mode preserves the image's own partition and boot structure.")
