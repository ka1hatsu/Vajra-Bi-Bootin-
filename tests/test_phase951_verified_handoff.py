from pathlib import Path
from vajra.workflow.image_handoff import ImageHandoff

def test_handoff_carries_digest(tmp_path):
    p=tmp_path/"test.iso"
    p.write_bytes(b"iso")
    h=ImageHandoff.from_download(p,"Test Linux",verified_sha256="ABCDEF")
    assert h.verified_sha256=="abcdef"

def test_recommendation_uses_explicit_digest():
    t=Path("vajra/workflow/recommendation_download.py").read_text()
    assert "verified_sha256=digest" in t
    assert "handoff.verified_sha256=digest" not in t

def test_main_window_passes_digest():
    t=Path("vajra/ui/main_window.py").read_text()
    assert "verified_sha256=handoff.verified_sha256" in t
    assert "dialog.verified_image_ready.connect" in t

def test_catalog_digest_signal():
    t=Path("vajra/ui/catalog_download_dialog.py").read_text()
    assert "verified_image_ready" in t
    assert "verified_image_ready.emit(path, digest)" in t
