import hashlib
from vajra.downloader.checksum import sha256_file, verify_sha256

def test_sha256(tmp_path):
    sample=tmp_path/"sample.bin"; sample.write_bytes(b"vajra")
    expected=hashlib.sha256(b"vajra").hexdigest()
    assert sha256_file(sample)==expected
    assert verify_sha256(sample,expected)
