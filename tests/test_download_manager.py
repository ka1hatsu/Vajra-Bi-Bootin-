import hashlib
from vajra.downloader.manager import sha256_file
def test_sha256_file(tmp_path):
    p=tmp_path/"x.bin"; p.write_bytes(b"vajra")
    assert sha256_file(p)==hashlib.sha256(b"vajra").hexdigest()
