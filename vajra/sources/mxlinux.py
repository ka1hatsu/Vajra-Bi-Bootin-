import re
import xml.etree.ElementTree as ET

from vajra.architecture.normalize import normalize_architecture
from vajra.sources.base import Resolver, ResolverError, UnsupportedArchitecture
from vajra.sources.http import fetch_text
from vajra.sources.models import ReleaseImage
from vajra.sources.security import validate_download_url


SHA256_RE = re.compile(r"\b([0-9a-fA-F]{64})\b")


def parse_sha256_companion(text):
    match = SHA256_RE.search(text)
    if not match:
        raise ResolverError("MX checksum companion did not contain a SHA-256 digest.")
    return match.group(1).lower()


class MXLinuxXfceResolver(Resolver):
    distro_ids = ("mx-linux-xfce",)
    rss = "https://sourceforge.net/projects/mx-linux/rss?path=/Final/Xfce"
    file_base = "https://sourceforge.net/projects/mx-linux/files/Final/Xfce/"

    def resolve(self, architecture):
        arch = normalize_architecture(architecture)
        if arch != "amd64":
            raise UnsupportedArchitecture(
                "MX Linux Xfce resolver currently selects x64 images."
            )

        root = ET.fromstring(fetch_text(self.rss))
        candidates = []

        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            enclosure = item.find("enclosure")
            enclosure_url = (
                enclosure.get("url", "").strip()
                if enclosure is not None else ""
            )

            filename = title.rsplit("/", 1)[-1]
            low = filename.lower()

            if not low.endswith(".iso"):
                continue
            if "xfce" not in low:
                continue
            if "ahs" in low:
                continue
            if not any(token in low for token in ("x64", "64", "amd64")):
                continue

            image_url = enclosure_url or link
            if image_url.startswith("http://"):
                image_url = "https://" + image_url[7:]
            validate_download_url(image_url)

            checksum_url = self.file_base + filename + ".sha256/download"
            validate_download_url(checksum_url)

            checksum_text = fetch_text(checksum_url)
            sha256 = parse_sha256_companion(checksum_text)

            version_match = re.search(r"MX-([0-9.]+)", filename, re.I)
            version = version_match.group(1) if version_match else "current"

            candidates.append(
                ReleaseImage(
                    distro="MX Linux Xfce",
                    version=version,
                    architecture="amd64",
                    image_url=image_url,
                    filename=filename,
                    sha256=sha256,
                    checksum_url=checksum_url,
                    source_page=self.file_base,
                )
            )

        if not candidates:
            raise ResolverError(
                "No checksum-verified stable MX Linux Xfce x64 ISO was found."
            )

        candidates.sort(key=lambda image: image.version, reverse=True)
        return [candidates[0]]
