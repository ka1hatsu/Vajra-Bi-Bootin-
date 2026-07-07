from pathlib import Path

def test_layout_sections():
    t=Path("vajra/ui/flash_dialog.py").read_text()
    for x in ("SectionLabel","BOOT IMAGE","TARGET USB DEVICE","BOOT AND FORMAT OPTIONS","COMPATIBILITY","SAFETY CONFIRMATION"):
        assert x in t

def test_workflow_preserved():
    t=Path("vajra/ui/flash_dialog.py").read_text()
    for x in ("ensure_image_fits","revalidate_target","verify_written_image","FlashOperationLog","assess_interruption","run_media_preflight"):
        assert x in t

def test_theme_rules():
    t=Path("vajra/ui/dialog_theme.py").read_text()
    assert "Phase 9.6.2 flash workflow hierarchy" in t
    assert "sectionLabel" in t and "eraseConfirmation" in t
