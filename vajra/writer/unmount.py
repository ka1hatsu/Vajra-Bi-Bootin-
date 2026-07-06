import subprocess

class UnmountError(RuntimeError):
    pass

def mounted_partition_paths(device):
    paths = []
    for entry in device.get("mounted_children", []) or []:
        path = entry.get("path")
        mounts = [m for m in entry.get("mountpoints", []) or [] if m]
        if path and mounts:
            paths.append(path)
    return paths

def unmount_partitions(device, runner=subprocess.run):
    failures = []
    for path in mounted_partition_paths(device):
        result = runner(["udisksctl", "unmount", "-b", path],
                        capture_output=True, text=True)
        if result.returncode != 0:
            msg = result.stderr.strip() or result.stdout.strip() or "unknown error"
            failures.append(f"{path}: {msg}")
    if failures:
        raise UnmountError("Could not unmount target partitions: " + "; ".join(failures))
    return True
