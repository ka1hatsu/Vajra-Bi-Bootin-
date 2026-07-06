from pathlib import Path
from vajra.downloads.history import DownloadHistory,DownloadRecord

def record(path,state="verified"):
    d="a"*64
    return DownloadRecord(
        distro_id="test",distro="Test Linux",version="1",architecture="amd64",
        filename="test.iso",path=str(path),image_url="https://example.invalid/test.iso",
        expected_sha256=d,actual_sha256=d,state=state
    )

def test_history_roundtrip(tmp_path):
    h=DownloadHistory(tmp_path/"history.json")
    h.upsert(record(tmp_path/"test.iso"))
    rows=h.load()
    assert len(rows)==1
    assert rows[0].verified

def test_upsert_replaces_same_target(tmp_path):
    h=DownloadHistory(tmp_path/"history.json")
    r=record(tmp_path/"test.iso","failed")
    h.upsert(r)
    r.state="verified"
    h.upsert(r)
    assert len(h.load())==1
    assert h.load()[0].state=="verified"

def test_verified_existing_requires_file(tmp_path):
    h=DownloadHistory(tmp_path/"history.json")
    iso=tmp_path/"test.iso"
    h.upsert(record(iso))
    assert h.verified_existing()==[]
    iso.write_bytes(b"x")
    assert len(h.verified_existing())==1
