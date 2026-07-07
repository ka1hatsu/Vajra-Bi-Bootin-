import shutil,subprocess
from pathlib import Path
from vajra.boot.process_runner import run_managed, ManagedCommandError

class WindowsMediaError(RuntimeError): pass

def split_install_wim(root,max_mb=3800,cancel_check=None):
    wim=Path(root)/"sources"/"install.wim"
    if not wim.exists(): raise WindowsMediaError("install.wim not found.")
    tool=shutil.which("wimlib-imagex")
    if not tool: raise WindowsMediaError("wimlib-imagex is required for large Windows install.wim files.")
    dest=wim.parent/"install.swm"
    try:
        run_managed([tool,"split",str(wim),str(dest),str(max_mb)],cancel_check=cancel_check)
    except ManagedCommandError as e:
        raise WindowsMediaError(str(e)) from e
    wim.unlink()
