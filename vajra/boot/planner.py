from dataclasses import dataclass

class PreparationPlanError(ValueError):
    pass

@dataclass(frozen=True)
class PreparationPlan:
    mode: str
    partition_scheme: str
    target_system: str
    file_system: str
    volume_label: str
    requires_preparation: bool
    summary: str

def build_plan(config, analysis):
    if config.image_option in ("Auto", "Raw image write"):
        return PreparationPlan(
            "raw", "Auto", "Auto", "Auto", config.volume_label, False,
            "Write image byte-for-byte and preserve its embedded layout."
        )

    if analysis.image_type != "ISO":
        raise PreparationPlanError(
            "Prepared media mode currently supports ISO images only."
        )

    target = config.target_system
    if target == "Auto":
        target = "UEFI" if analysis.uefi_hint else "BIOS / Legacy"

    scheme = config.partition_scheme
    if scheme == "Auto":
        scheme = "GPT" if target == "UEFI" else "MBR"

    fs = config.file_system if config.file_system != "Auto" else "FAT32"
    if fs != "FAT32":
        raise PreparationPlanError(
            "Phase 7.3 prepared-media backend currently supports FAT32 only."
        )

    return PreparationPlan(
        "prepared_fat32", scheme, target, fs,
        config.volume_label or "VAJRA_BOOT", True,
        f"Prepare {scheme} / {target} / FAT32 media and extract ISO contents."
    )
