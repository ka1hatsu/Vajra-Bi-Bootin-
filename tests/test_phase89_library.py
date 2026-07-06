from types import SimpleNamespace
from vajra.downloads.library import sha256_file,inspect_record
def test_library_states(tmp_path):
    p=tmp_path/"x.iso"; r=SimpleNamespace(path=str(p),expected_sha256="")
    assert inspect_record(r)[0]=="missing"
    p.write_bytes(b"abc"); assert inspect_record(r)[0]=="untrusted"
    r.expected_sha256=sha256_file(p); assert inspect_record(r)[0]=="verified"
    r.expected_sha256="0"*64; assert inspect_record(r)[0]=="modified"
