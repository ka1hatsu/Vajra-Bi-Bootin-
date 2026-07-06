import os, re, subprocess, tempfile
from vajra.boot.iso_inspector import inspect_iso
from vajra.boot.large_file_policy import choose_strategy, LargeFilePolicyError
from vajra.boot.windows_media import split_install_wim, WindowsMediaError

class PreparedMediaError(RuntimeError):
    pass

def run(cmd, input_text=None):
    x = subprocess.run(cmd, input=input_text, capture_output=True, text=True)
    if x.returncode:
        raise PreparedMediaError(x.stderr.strip() or x.stdout.strip() or "Command failed")
    return x

def sanitize_label(label):
    return (re.sub(r"[^A-Za-z0-9_-]", "_", label or "VAJRA_BOOT")[:11] or "VAJRA_BOOT")

def partition_path(device):
    return device + ("p1" if device[-1:].isdigit() else "1")

def prepare_fat32_media(image, device, plan, progress=None):
    if os.geteuid() != 0:
        raise PreparedMediaError("Prepared-media helper must run as root.")
    if progress: progress(5, "Creating partition table...")
    if plan.partition_scheme == "GPT":
        run(["sgdisk", "--zap-all", device])
        run(["sgdisk", "-n", "1:0:0", "-t", "1:ef00", device])
    elif plan.partition_scheme == "MBR":
        run(["sfdisk", device], "label: dos\n,0x0c,*\n")
    else:
        raise PreparedMediaError("Unsupported partition scheme.")
    run(["partprobe", device])
    part = partition_path(device)
    if progress: progress(20, "Formatting FAT32...")
    run(["mkfs.fat", "-F", "32", "-n", sanitize_label(plan.volume_label), part])
    with tempfile.TemporaryDirectory(prefix="vajra-mount-") as mount_dir:
        run(["mount", part, mount_dir])
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
                    ])

                    if progress:
                        progress(
                            70,
                            "Splitting Windows install.wim for FAT32..."
                        )

                    try:
                        split_install_wim(extract_dir)
                    except WindowsMediaError as e:
                        raise PreparedMediaError(str(e))

                    run([
                        "cp",
                        "-a",
                        f"{extract_dir}/.",
                        mount_dir,
                    ])

            else:
                run([
                    "7z",
                    "x",
                    "-y",
                    f"-o{mount_dir}",
                    image,
                ])

            run(["sync"])
        finally:
            subprocess.run(["umount", mount_dir], capture_output=True, text=True)
    if progress: progress(100, "Prepared media complete.")
