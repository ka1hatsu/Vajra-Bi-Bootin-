from dataclasses import dataclass

@dataclass(frozen=True)
class CompatibilityResult:
    compatible: bool
    severity: str
    message: str
    recommended_scheme: str
    recommended_target: str
    recommended_filesystem: str

def evaluate(image_type, partition_scheme, target_system, file_system,
             uefi_hint=False, bios_hint=False):
    scheme = partition_scheme
    target = target_system
    fs = file_system

    if image_type == "IMG":
        if any(v != "Auto" for v in (scheme, target, fs)):
            return CompatibilityResult(
                False, "error",
                "IMG raw-write mode preserves its embedded disk layout. Use Auto for partition scheme, target system and file system.",
                "Auto", "Auto", "Auto")
        return CompatibilityResult(True, "ok", "IMG will be written as-is.", "Auto", "Auto", "Auto")

    if image_type != "ISO":
        return CompatibilityResult(False, "error", "Unsupported or unknown image type.", "Auto", "Auto", "Auto")

    rec_target = "UEFI" if uefi_hint and not bios_hint else "BIOS / Legacy" if bios_hint and not uefi_hint else "Auto"
    rec_scheme = "GPT" if rec_target == "UEFI" else "MBR" if rec_target == "BIOS / Legacy" else "Auto"
    rec_fs = "FAT32" if rec_target == "UEFI" else "Auto"

    if target == "UEFI" and scheme == "MBR":
        return CompatibilityResult(
            True, "warning",
            "MBR + UEFI can work on some firmware, but GPT is generally the cleaner UEFI choice.",
            "GPT", "UEFI", "FAT32")

    if target == "BIOS / Legacy" and scheme == "GPT":
        return CompatibilityResult(
            False, "error",
            "GPT + BIOS/Legacy requires special bootloader support and is not supported by the current preparation backend.",
            "MBR", "BIOS / Legacy", "Auto")

    if target == "UEFI" and fs == "NTFS":
        return CompatibilityResult(
            True, "warning",
            "Many UEFI firmwares boot FAT32 directly. NTFS may require an additional UEFI NTFS loader.",
            "GPT", "UEFI", "FAT32")

    if target == "BIOS / Legacy" and fs == "exFAT":
        return CompatibilityResult(
            False, "error",
            "exFAT is not supported for the current BIOS/Legacy boot preparation path.",
            "MBR", "BIOS / Legacy", "FAT32")

    return CompatibilityResult(
        True, "ok",
        "Configuration is compatible with the current compatibility rules. Preparation backend support is checked separately before writing.",
        rec_scheme, rec_target, rec_fs)
