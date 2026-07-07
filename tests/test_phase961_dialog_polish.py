from pathlib import Path

def test_shared_theme():
    t=Path("vajra/ui/dialog_theme.py").read_text()
    assert "DIALOG_STYLE" in t
    assert "primaryAction" in t
    assert "dangerAction" in t

def test_dialogs_use_theme():
    for name in ("flash_dialog.py","resolved_download_dialog.py","catalog_download_dialog.py"):
        t=(Path("vajra/ui")/name).read_text()
        assert "DIALOG_STYLE" in t
        assert "setStyleSheet(DIALOG_STYLE)" in t

def test_flash_action_hierarchy():
    t=Path("vajra/ui/flash_dialog.py").read_text()
    assert 'setObjectName("primaryAction")' in t
    assert 'setObjectName("dangerAction")' in t
