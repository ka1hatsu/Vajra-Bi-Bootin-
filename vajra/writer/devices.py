import json
import platform
import subprocess


class DeviceDetectionError(RuntimeError):
    pass


def _run(command):
    return subprocess.check_output(
        command, stderr=subprocess.STDOUT, text=True
    ).strip()


def _linux_root_parent():
    try:
        source = _run(["findmnt", "-n", "-o", "SOURCE", "/"])
        pkname = _run(["lsblk", "-no", "PKNAME", source])
        return pkname.strip() or source.rsplit("/", 1)[-1]
    except Exception:
        return None


def _linux_devices():
    command = [
        "lsblk", "-J", "-b", "-o",
        "NAME,PATH,MODEL,VENDOR,SERIAL,SIZE,TYPE,RM,RO,TRAN,MOUNTPOINTS"
    ]
    try:
        payload = json.loads(_run(command))
    except Exception as exc:
        raise DeviceDetectionError(f"Could not read block devices: {exc}") from exc

    root_parent = _linux_root_parent()
    devices = []

    for item in payload.get("blockdevices", []):
        if item.get("type") != "disk":
            continue

        name = item.get("name", "")
        transport = (item.get("tran") or "").lower()
        removable_flag = bool(item.get("rm"))
        is_usb = transport == "usb"
        is_system = name == root_parent

        mountpoints = []
        mounted_children = []
        for child in item.get("children", []) or []:
            child_mounts = [m for m in child.get("mountpoints", []) or [] if m]
            mountpoints.extend(child_mounts)
            if child.get("path") and child_mounts:
                mounted_children.append({
                    "path": child["path"],
                    "mountpoints": child_mounts,
                })
        for mount in item.get("mountpoints", []) or []:
            if mount:
                mountpoints.append(mount)

        devices.append({
            "name": name,
            "path": item.get("path") or f"/dev/{name}",
            "model": (item.get("model") or "Unknown").strip(),
            "vendor": (item.get("vendor") or "").strip(),
            "serial": (item.get("serial") or "").strip(),
            "size_bytes": int(item.get("size") or 0),
            "transport": transport or "unknown",
            "removable": removable_flag or is_usb,
            "read_only": bool(item.get("ro")),
            "system_disk": is_system,
            "mountpoints": mountpoints,
            "mounted_children": mounted_children,
            "eligible": (removable_flag or is_usb) and not is_system and not bool(item.get("ro")),
        })

    return devices


def list_storage_devices():
    system = platform.system()
    if system == "Linux":
        return _linux_devices()
    raise DeviceDetectionError(
        f"Phase 4 device detection currently supports Linux only; detected {system}."
    )


def eligible_usb_devices():
    return [device for device in list_storage_devices() if device["eligible"]]


def format_size(size_bytes):
    value = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024
