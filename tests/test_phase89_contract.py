from pathlib import Path
def test_real_resume_contract():
    h=Path("vajra/ui/download_history_dialog.py").read_text()
    r=Path("vajra/ui/resolved_download_dialog.py").read_text()
    m=Path("vajra/ui/main_window.py").read_text()
    assert "resume_requested = Signal(str, str, str)" in h
    assert "resume_destination=None" in r
    assert "resume_requested.connect(self.resume_history_download)" in m
