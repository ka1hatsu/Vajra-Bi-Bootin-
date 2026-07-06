import pytest
from vajra.workflow.image_handoff import ImageHandoff, ImageHandoffError


def test_valid_iso(tmp_path):
    p = tmp_path / "linux.iso"
    p.write_bytes(b"iso")
    h = ImageHandoff.from_download(p, "Example Linux")
    assert h.source == "download"
    assert h.distro_name == "Example Linux"
    assert h.path.endswith("linux.iso")


def test_missing_image_blocked(tmp_path):
    with pytest.raises(ImageHandoffError):
        ImageHandoff.from_download(tmp_path / "missing.iso")


def test_wrong_extension_blocked(tmp_path):
    p = tmp_path / "file.txt"
    p.write_text("x")
    with pytest.raises(ImageHandoffError):
        ImageHandoff.from_download(p)
