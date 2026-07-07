import pytest

from vajra.sources.security import SafeDownloadRedirectHandler, validate_download_url


def test_allows_official_cdimage():
    assert validate_download_url("https://cdimage.ubuntu.com/x.iso")


def test_allows_sourceforge_download_mirror():
    assert validate_download_url("https://netix.dl.sourceforge.net/project/example.iso")


def test_blocks_http():
    with pytest.raises(ValueError):
        validate_download_url("http://cdimage.ubuntu.com/x.iso")


def test_blocks_unknown_host():
    with pytest.raises(ValueError):
        validate_download_url("https://example.invalid/x.iso")


def test_blocks_lookalike_sourceforge_host():
    with pytest.raises(ValueError):
        validate_download_url("https://sourceforge.net.example.invalid/x.iso")


def test_blocks_url_credentials():
    with pytest.raises(ValueError):
        validate_download_url("https://user:secret@cdimage.ubuntu.com/x.iso")


def test_redirect_handler_blocks_unapproved_target():
    handler = SafeDownloadRedirectHandler()
    with pytest.raises(ValueError):
        handler.redirect_request(
            None,
            None,
            302,
            "Found",
            {},
            "https://example.invalid/payload.iso",
        )
