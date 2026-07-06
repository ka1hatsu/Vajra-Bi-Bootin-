import shutil

class BackendUnavailable(RuntimeError):
    pass

def required_tools(plan):
    if plan.mode == "raw":
        return ()
    tools = ["lsblk", "mount", "umount", "7z", "mkfs.fat"]
    tools.append("sgdisk" if plan.partition_scheme == "GPT" else "sfdisk")
    return tuple(tools)

def check_backend_available(plan):
    missing = [x for x in required_tools(plan) if shutil.which(x) is None]
    if missing:
        raise BackendUnavailable(
            "Missing required system tools: " + ", ".join(missing)
        )
    return True
