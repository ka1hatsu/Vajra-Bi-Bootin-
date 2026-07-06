from vajra.architecture.normalize import normalize_architecture
def test_scanner_arch_mapping():
    assert normalize_architecture("x86_64")=="amd64"
