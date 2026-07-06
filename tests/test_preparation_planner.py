from types import SimpleNamespace
import pytest
from vajra.boot.config import BootConfig
from vajra.boot.planner import build_plan, PreparationPlanError

def analysis(kind="ISO", uefi=True):
    return SimpleNamespace(
        image_type=kind, uefi_hint=uefi, bios_hint=not uefi
    )

def test_raw_plan():
    plan = build_plan(BootConfig(), analysis())
    assert plan.mode == "raw"
    assert not plan.requires_preparation

def test_prepared_uefi_defaults():
    config = BootConfig(
        target_system="UEFI",
        image_option="Extract ISO to prepared USB"
    )
    plan = build_plan(config, analysis())
    assert plan.partition_scheme == "GPT"
    assert plan.file_system == "FAT32"

def test_prepared_img_blocked():
    config = BootConfig(image_option="Extract ISO to prepared USB")
    with pytest.raises(PreparationPlanError):
        build_plan(config, analysis("IMG"))
