from pathlib import Path
from vajra.workflow.session import WorkflowSession, sha256_file

def test_verified_file_detects_change(tmp_path):
    p=tmp_path/"image.iso"; p.write_bytes(b"original")
    x=WorkflowSession(); x.accept_verified_image(p,sha256_file(p),"Test Linux")
    assert x.validate_image_unchanged()
    p.write_bytes(b"changed")
    assert not x.validate_image_unchanged()

def test_flash_has_digest_guard():
    t=Path("vajra/ui/flash_dialog.py").read_text()
    assert 'verified_sha256=""' in t
    assert "current_digest=sha256_file(p)" in t
    assert "Verified image changed" in t

def test_resolver_digest_signal():
    t=Path("vajra/ui/resolved_download_dialog.py").read_text()
    assert "verified_image_ready=Signal(str,str)" in t
    assert "self.verified_image_ready.emit(path,digest)" in t
