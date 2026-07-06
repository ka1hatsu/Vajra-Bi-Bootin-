from pathlib import Path

def test_dialog_has_safe_close_contract():
    text=Path("vajra/ui/resolved_download_dialog.py").read_text()
    assert "def closeEvent(self,event):" in text
    assert "self.worker.cancel()" in text
    assert "self.worker.wait(5000)" in text
    assert "event.ignore()" in text
