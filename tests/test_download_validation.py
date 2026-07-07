import pytest

from vajra.downloader.manager import DownloadError, download_file


def test_malformed_expected_digest_is_rejected_before_request(tmp_path):
    with pytest.raises(DownloadError, match="malformed"):
        download_file(
            "https://cdimage.ubuntu.com/example.iso",
            tmp_path / "example.iso",
            expected_sha256="bad-digest",
        )


def test_unknown_download_host_is_rejected_before_request(tmp_path):
    with pytest.raises(DownloadError):
        download_file(
            "https://invalid.example/example.iso",
            tmp_path / "example.iso",
        )
