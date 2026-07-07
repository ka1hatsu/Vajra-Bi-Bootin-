from pathlib import Path

from vajra.writer.devices import list_storage_devices
from vajra.writer.unmount import UnmountError, unmount_partitions


class PreflightError(RuntimeError):
    pass


def _find_device(device_path):
    for device in list_storage_devices():
        if device["path"] == device_path:
            return device
    raise PreflightError("Selected device is no longer present.")


def revalidate_target(device_path, expected_serial="", expected_size=None):
    device = _find_device(device_path)

    if not device["eligible"]:
        raise PreflightError("Target no longer passes removable-device safety checks.")

    if expected_serial and device.get("serial") != expected_serial:
        raise PreflightError("Device identity changed: serial number mismatch.")

    if expected_size is not None and device.get("size_bytes") != expected_size:
        raise PreflightError("Device identity changed: capacity mismatch.")

    return device


def unmount_target(device):
    """Unmount each mounted partition belonging to the selected disk."""
    try:
        return unmount_partitions(device)
    except UnmountError as exc:
        raise PreflightError(str(exc)) from exc


def ensure_image_fits(image_path, device):
    image_size = Path(image_path).stat().st_size
    if image_size > device["size_bytes"]:
        raise PreflightError("Image is larger than the selected target.")
    return image_size
