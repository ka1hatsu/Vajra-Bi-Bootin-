import os
import shutil
import subprocess

class PrivilegeError(RuntimeError):
    pass

def can_write_device(device_path):
    return os.access(device_path, os.W_OK)

def build_privileged_command(helper_path, image_path, device_path):
    pkexec = shutil.which("pkexec")
    if not pkexec:
        raise PrivilegeError("pkexec is not installed or not available in PATH.")
    return [pkexec, helper_path, "--image", image_path, "--device", device_path]

def run_privileged_helper(helper_path, image_path, device_path):
    return subprocess.Popen(build_privileged_command(helper_path, image_path, device_path))
