from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class DownloadChoice:
    name: str
    url: str
    sha256: str = ""
    filename: str = ""


def _first(mapping, *keys, default=""):
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


def load_download_choices(path="vajra/catalog/distros.json"):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        entries = data.get("distros", data.get("items", data.get("distributions", [])))
    else:
        entries = data

    choices = []
    for item in entries:
        if not isinstance(item, dict):
            continue

        name = _first(item, "name", "title", "distro")
        url = _first(
            item,
            "download_url",
            "iso_url",
            "url",
            "download",
        )
        sha256 = _first(item, "sha256", "checksum", default="")
        filename = _first(item, "filename", default="")

        if name and url:
            choices.append(DownloadChoice(name, url, sha256, filename))

    return choices
