from vajra.architecture.normalize import normalize_architecture, architecture_compatible

def test_aliases():
    assert normalize_architecture("x86_64") == "amd64"
    assert normalize_architecture("i686") == "i386"
    assert normalize_architecture("aarch64") == "arm64"

def test_compatibility():
    assert architecture_compatible("amd64", "x86_64")
    assert not architecture_compatible("i386", "x86_64")
