import shutil
import subprocess


class PrivilegeError(RuntimeError):
    pass


def build_privileged_command(helper_path, image_path, identity):
    pkexec=shutil.which("pkexec")
    if not pkexec:
        raise PrivilegeError("pkexec is not installed or unavailable.")
    return [
        pkexec,
        helper_path,
        "--image", image_path,
        "--device", identity.path,
        "--serial", identity.serial,
        "--size", str(identity.size_bytes),
    ]


def run_privileged_helper(helper_path, image_path, identity):
    return subprocess.Popen(
        build_privileged_command(helper_path,image_path,identity),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
