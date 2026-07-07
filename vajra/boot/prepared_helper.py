import os, re, subprocess, tempfile
from vajra.boot.iso_inspector import inspect_iso
from vajra.boot.large_file_policy import choose_strategy, LargeFilePolicyError
from vajra.boot.windows_media import split_install_wim, WindowsMediaError
from vajra.boot.process_runner import run_managed, ManagedCommandError

class PreparedMediaError(RuntimeError):
    pass

def run(cmd, input_text=None, cancel_check=None):
    try:
        return run_managed(
            cmd,
            input_text=input_text,
            cancel_check=cancel_check,
        )
    except ManagedCommandError as e:
        raise PreparedMediaError(str(e)) from e

def sanitize_label(label):
    return (re.sub(r"[^A-Za-z0-9_-]", "_", label or "VAJRA_BOOT")[:11] or "VAJRA_BOOT")

def partition_path(device):
    return device + ("p1" if device[-1:].isdigit() else "1")

def prepare_fat32_media(image, device, plan, progress=None, cancel_check=None):
    if os.geteuid() != 0:
        raise PreparedMediaError("Prepared-media helper must run as root.")
    if progress: progress(5, "Creating partition table...")
    if plan.partition_scheme == "GPT":
        run(["sgdisk", "--zap-all", device], cancel_check=cancel_check)
        run(["sgdisk", "-n", "1:0:0", "-t", "1:ef00", device], cancel_check=cancel_check)
    elif plan.partition_scheme == "MBR":
        run(["sfdisk", device], "label: dos\n,0x0c,*\n", cancel_check=cancel_check)
    else:
        raise PreparedMediaError("Unsupported partition scheme.")
    run(["partprobe", device], cancel_check=cancel_check)
    part = partition_path(device)
    if progress: progress(20, "Formatting FAT32...")
    run(["mkfs.fat", "-F", "32", "-n", sanitize_label(plan.volume_label), part], cancel_check=cancel_check)
    with tempfile.TemporaryDirectory(prefix="vajra-mount-") as mount_dir:
        run(["mount", part, mount_dir], cancel_check=cancel_check)
        try:
            if progress: progress(40, "Extracting ISO contents...")
            info = inspect_iso(image)

            try:
                strategy = choose_strategy(info, "FAT32")
            except LargeFilePolicyError as e:
                raise PreparedMediaError(str(e))

            if strategy == "split_windows_wim":
                with tempfile.TemporaryDirectory(
                    prefix="vajra-extract-"
                ) as extract_dir:

                    run([
                        "7z",
                        "x",
                        "-y",
                        f"-o{extract_dir}",
                        image,
                    ], cancel_check=cancel_check)

                    if progress:
                        progress(
                            70,
                            "Splitting Windows install.wim for FAT32..."
                        )

                    try:
                        split_install_wim(extract_dir, cancel_check=cancel_check)
                    except WindowsMediaError as e:
                        raise PreparedMediaError(str(e))

                    run([
                        "cp",
                        "-a",
                        f"{extract_dir}/.",
                        mount_dir,
                    ], cancel_check=cancel_check)

            else:
                run([
                    "7z",
                    "x",
                    "-y",
                    f"-o{mount_dir}",
                    image,
                ], cancel_check=cancel_check)

            run(["sync"], cancel_check=cancel_check)
        finally:
            subprocess.run(["umount", mount_dir], capture_output=True, text=True)
    if progress: progress(100, "Prepared media complete.")
