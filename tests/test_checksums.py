from vajra.sources.checksums import parse_sha256sums

def test_parse_sha256sums():
    digest = "a" * 64
    result = parse_sha256sums(f"{digest} *linux.iso\n")
    assert result["linux.iso"] == digest
