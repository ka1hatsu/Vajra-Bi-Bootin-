import pytest

from vajra.verification.policy import (
    VerificationPolicyError,
    evaluate_download_verification,
    require_verified_download,
)


def test_verified_image_can_flash():
    digest = "a" * 64
    result = evaluate_download_verification(digest, digest)
    assert result.can_flash is True
    assert result.state == "verified"


def test_checksum_mismatch_blocks_flash():
    result = evaluate_download_verification("a" * 64, "b" * 64)
    assert result.can_flash is False
    assert result.state == "mismatch"


def test_missing_upstream_checksum_blocks_automatic_flash():
    result = evaluate_download_verification("", "a" * 64)
    assert result.can_flash is False
    assert result.state == "untrusted"


def test_require_verified_download_raises():
    with pytest.raises(VerificationPolicyError):
        require_verified_download("a" * 64, "b" * 64)
