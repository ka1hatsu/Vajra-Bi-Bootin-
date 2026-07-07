from pathlib import Path
import hashlib
import pytest
from vajra.workflow.end_to_end_guard import WorkflowGuardError, require_flash_ready

def test_accepts_unchanged_file(tmp_path):
    p=tmp_path/"test.iso"; p.write_bytes(b"vajra-test-image")
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    result=require_flash_ready(str(p),digest)
    assert result.path == str(p.resolve()) and result.sha256 == digest

def test_rejects_changed_file(tmp_path):
    p=tmp_path/"test.iso"; p.write_bytes(b"original")
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    p.write_bytes(b"changed")
    with pytest.raises(WorkflowGuardError): require_flash_ready(str(p),digest)

def test_requires_digest(tmp_path):
    p=tmp_path/"test.iso"; p.write_bytes(b"x")
    with pytest.raises(WorkflowGuardError): require_flash_ready(str(p),"")

def test_flash_exposes_recheck():
    t=Path("vajra/ui/flash_dialog.py").read_text()
    assert "validate_verified_handoff" in t and "require_flash_ready" in t

def test_workflow_connections_remain():
    t=Path("vajra/ui/main_window.py").read_text()
    for x in ("RecommendationDownloadFlow","verified_image_ready","open_verified_history_image","open_recommended_download","downloaded_image_ready"):
        assert x in t
