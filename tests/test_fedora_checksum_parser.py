from vajra.sources.fedora import FEDORA_SHA_RE

def test_fedora_checksum_format():
    d="a"*64
    text=f"SHA256 (Fedora-Workstation-Live-44-1.0.x86_64.iso) = {d}"
    assert FEDORA_SHA_RE.findall(text)[0][1]==d
