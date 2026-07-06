import pytest
import vajra.boot.preflight_media as pf
from types import SimpleNamespace

def plan(): return SimpleNamespace(mode="prepared_fat32",file_system="FAT32",partition_scheme="GPT")

def test_estimate():
    assert pf.estimate_required_bytes([("a",1000),("b",2000)])>3000

def test_small_target(monkeypatch):
    monkeypatch.setattr(pf,"check_backend_available",lambda p: True)
    monkeypatch.setattr(pf,"inspect_iso",lambda x:{"files":[("x",900000000)],"windows_install_media":False,"large_files":[],"fat32_compatible":True})
    with pytest.raises(pf.MediaPreflightError): pf.run_media_preflight("x.iso",100000000,plan())

def test_summary(monkeypatch):
    monkeypatch.setattr(pf,"check_backend_available",lambda p: True)
    monkeypatch.setattr(pf,"inspect_iso",lambda x:{"files":[("x",1024)],"windows_install_media":False,"large_files":[],"fat32_compatible":True})
    assert "Estimated required capacity" in pf.run_media_preflight("x.iso",2*1024**3,plan()).summary
