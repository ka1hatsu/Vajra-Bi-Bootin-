import json
from vajra.downloader.catalog_adapter import load_download_choices


def test_list_catalog(tmp_path):
    p = tmp_path / "distros.json"
    p.write_text(json.dumps([
        {
            "name": "Example Linux",
            "download_url": "https://example.invalid/linux.iso",
            "sha256": "abc",
        }
    ]))
    result = load_download_choices(p)
    assert result[0].name == "Example Linux"
    assert result[0].sha256 == "abc"


def test_wrapped_catalog(tmp_path):
    p = tmp_path / "distros.json"
    p.write_text(json.dumps({
        "distros": [
            {"title": "TestOS", "iso_url": "https://example.invalid/test.iso"}
        ]
    }))
    result = load_download_choices(p)
    assert result[0].name == "TestOS"
