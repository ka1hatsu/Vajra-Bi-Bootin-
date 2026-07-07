import hashlib

import pytest

from vajra.workflow.end_to_end_guard import WorkflowGuardError, require_flash_ready


def digest(data):
    return hashlib.sha256(data).hexdigest()


def test_verified_boundary_returns_size(tmp_path):
    payload = b"vajra-phase-971"
    image = tmp_path / "linux.iso"
    image.write_bytes(payload)

    verified = require_flash_ready(image, digest(payload))

    assert verified.path == str(image.resolve())
    assert verified.sha256 == digest(payload)
    assert verified.size_bytes == len(payload)


def test_verified_boundary_rejects_changed_image(tmp_path):
    image = tmp_path / "linux.iso"
    image.write_bytes(b"original")
    expected = digest(b"original")
    image.write_bytes(b"changed")

    with pytest.raises(WorkflowGuardError, match="changed after verification"):
        require_flash_ready(image, expected)


def test_verified_boundary_rejects_invalid_digest(tmp_path):
    image = tmp_path / "linux.iso"
    image.write_bytes(b"image")

    with pytest.raises(WorkflowGuardError, match="valid verified SHA-256"):
        require_flash_ready(image, "not-a-sha256")


def test_verified_boundary_rejects_non_image_extension(tmp_path):
    image = tmp_path / "linux.txt"
    image.write_bytes(b"image")

    with pytest.raises(WorkflowGuardError, match="ISO or IMG"):
        require_flash_ready(image, digest(b"image"))
