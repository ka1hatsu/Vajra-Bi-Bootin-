from pathlib import Path

def test_logo_asset():
    assert Path("vajra/assets/vajra_logo.png").is_file()

def test_logo_and_icon_wiring():
    t=Path("vajra/ui/main_window.py").read_text()
    assert "QPixmap" in t and "QIcon" in t
    assert "vajra_logo.png" in t
    assert 'setObjectName("welcomeLogo")' in t

def test_clean_actions():
    t=Path("vajra/ui/main_window.py").read_text()
    for label in ("Choose Linux","Download ISO","USB Devices","Write to USB","Download History","Operation Reports"):
        assert label in t
