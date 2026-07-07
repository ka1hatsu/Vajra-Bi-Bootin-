from pathlib import Path

def test_flash_dialog_tracks_stage():
    t=Path("vajra/ui/flash_dialog.py").read_text()
    assert "def on_flash_stage(self,message):" in t
    assert "self.last_flash_stage" in t

def test_flash_dialog_has_recovery_refresh():
    t=Path("vajra/ui/flash_dialog.py").read_text()
    assert "def refresh_device_state(self):" in t
    assert "assess_interruption" in t
    assert "recovery_state" in t
