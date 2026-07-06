import os
import platform
import subprocess
import psutil


def _run(command):
    try:
        return subprocess.check_output(
            command, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        return None


def _detect_gpu():
    system = platform.system()
    if system == "Linux":
        output = _run(["sh", "-c", "lspci | grep -Ei 'VGA|3D|Display'"])
        return output or "Unknown"
    if system == "Windows":
        output = _run([
            "powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"
        ])
        return output or "Unknown"
    return "Unknown"


def _detect_firmware():
    system = platform.system()
    if system == "Linux":
        return "UEFI" if os.path.exists("/sys/firmware/efi") else "Legacy BIOS"
    if system == "Windows":
        output = _run([
            "powershell", "-NoProfile", "-Command",
            "(Get-ItemProperty 'HKLM:\\SYSTEM\\CurrentControlSet\\Control').PEFirmwareType"
        ])
        return {"1": "Legacy BIOS", "2": "UEFI"}.get(output, "Unknown")
    return "Unknown"


def _detect_secure_boot():
    system = platform.system()
    if system == "Linux":
        output = _run(["sh", "-c", "mokutil --sb-state 2>/dev/null"])
        if not output:
            return "Unknown"
        return "Enabled" if "enabled" in output.lower() else "Disabled"
    if system == "Windows":
        output = _run([
            "powershell", "-NoProfile", "-Command",
            "try { Confirm-SecureBootUEFI } catch { 'Unknown' }"
        ])
        if output == "True":
            return "Enabled"
        if output == "False":
            return "Disabled"
    return "Unknown"


def scan_hardware():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(os.path.abspath(os.sep))

    return {
        "os": platform.system(),
        "os_version": platform.release(),
        "architecture": platform.machine().lower(),
        "cpu": platform.processor() or "Unknown",
        "physical_cores": psutil.cpu_count(logical=False) or 1,
        "logical_cores": psutil.cpu_count(logical=True) or 1,
        "ram_gb": round(memory.total / (1024 ** 3), 1),
        "disk_free_gb": round(disk.free / (1024 ** 3), 1),
        "gpu": _detect_gpu(),
        "firmware": _detect_firmware(),
        "secure_boot": _detect_secure_boot(),
    }
