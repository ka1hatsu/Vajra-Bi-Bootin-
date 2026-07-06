import subprocess
class IsoInspectionError(RuntimeError): pass

def list_iso_files(image):
    x=subprocess.run(["7z","l","-slt",image],capture_output=True,text=True)
    if x.returncode: raise IsoInspectionError(x.stderr.strip() or x.stdout.strip() or "Unable to inspect ISO.")
    files=[]; path=None
    for line in x.stdout.splitlines():
        if line.startswith("Path = "): path=line[7:].strip()
        elif line.startswith("Size = ") and path is not None:
            try: files.append((path,int(line[7:].strip())))
            except ValueError: pass
            path=None
    return files

def inspect_iso(image):
    files=list_iso_files(image)
    names=[p.replace(chr(92),"/").lower() for p,_ in files]
    windows=any(p.endswith("sources/install.wim") or p.endswith("sources/install.esd") for p in names)
    large=[(p,n) for p,n in files if n>4*1024**3-1]
    return {"files":files,"windows_install_media":windows,"large_files":large,"fat32_compatible":not large}
