import pytest
from vajra.sources.security import validate_download_url

def test_allows_official_cdimage():
    assert validate_download_url("https://cdimage.ubuntu.com/x.iso")

def test_blocks_http():
    with pytest.raises(ValueError):
        validate_download_url("http://cdimage.ubuntu.com/x.iso")

def test_blocks_unknown_host():
    with pytest.raises(ValueError):
        validate_download_url("https://example.invalid/x.iso")
