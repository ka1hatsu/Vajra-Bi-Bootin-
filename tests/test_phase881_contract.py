from pathlib import Path

def test_history_dialog_exists():
    text=Path("vajra/ui/download_history_dialog.py").read_text()
    assert "class DownloadHistoryDialog" in text
    assert "Flash Again" in text
    assert "Resume" in text

def test_download_session_wired():
    text=Path("vajra/ui/resolved_download_dialog.py").read_text()
    assert "DownloadSession" in text
    assert "download_session.completed" in text

def test_main_window_history_methods():
    text=Path("vajra/ui/main_window.py").read_text()
    assert "open_download_history" in text
    assert "open_verified_history_image" in text
