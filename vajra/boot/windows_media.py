import shutil,subprocess
from pathlib import Path

class WindowsMediaError(RuntimeError): pass

def split_install_wim(root,max_mb=3800):
    wim=Path(root)/"sources"/"install.wim"
    if not wim.exists(): raise WindowsMediaError("install.wim not found.")
    tool=shutil.which("wimlib-imagex")
    if not tool: raise WindowsMediaError("wimlib-imagex is required for large Windows install.wim files.")
    dest=wim.parent/"install.swm"
    x=subprocess.run([tool,"split",str(wim),str(dest),str(max_mb)],capture_output=True,text=True)
    if x.returncode: raise WindowsMediaError(x.stderr.strip() or "WIM split failed.")
    wim.unlink()
