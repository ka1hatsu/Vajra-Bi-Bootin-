import pytest

from vajra.sources.base import ResolverError
from vajra.sources.mxlinux import parse_sha256_companion


def test_parse_mx_sha256_companion():
    digest = "a" * 64
    assert parse_sha256_companion(f"{digest}  MX-test.iso\n") == digest


def test_reject_bad_mx_checksum_companion():
    with pytest.raises(ResolverError):
        parse_sha256_companion("not a checksum")
