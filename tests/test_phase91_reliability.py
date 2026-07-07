from pathlib import Path
def test_helper_has_distinct_cancel_terminal_state():
    t=Path("vajra/writer/helper_client.py").read_text()
    assert "cancelled=Signal()" in t
    assert "self.cancel_requested=True" in t
    assert "self.cancelled.emit()" in t
def test_flash_dialog_logs_terminal_states():
    t=Path("vajra/ui/flash_dialog.py").read_text()
    for x in ('"started"','"completed"','"cancelled"','"failed"'): assert x in t
def test_cancel_button_disabled_during_shutdown():
    t=Path("vajra/ui/flash_dialog.py").read_text()
    assert "self.cancel.setEnabled(False)" in t
    assert "waiting for helper shutdown" in t
