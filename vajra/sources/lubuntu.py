import re
from urllib.parse import urljoin
from vajra.architecture.normalize import normalize_architecture
from vajra.sources.base import Resolver, ResolverError, UnsupportedArchitecture
from vajra.sources.checksums import parse_sha256sums
from vajra.sources.http import fetch_text
from vajra.sources.models import ReleaseImage
from vajra.sources.security import validate_download_url

class LubuntuResolver(Resolver):
    distro_ids = ("lubuntu",)
    releases_index = "https://cdimage.ubuntu.com/lubuntu/releases/"

    def resolve(self, architecture):
        arch = normalize_architecture(architecture)
        if arch != "amd64":
            raise UnsupportedArchitecture(
                "Current supported Lubuntu desktop releases are not offered for this architecture."
            )

        index = fetch_text(self.releases_index)
        # Prefer current numeric release directories, newest version first.
        versions = sorted(
            set(re.findall(r'href="(\d+\.\d+(?:\.\d+)?)/"', index)),
            key=lambda s: tuple(int(x) for x in s.split(".")),
            reverse=True,
        )
        errors = []
        for version in versions[:8]:
            page = urljoin(self.releases_index, version + "/release/")
            try:
                html = fetch_text(page)
                names = re.findall(r'href="([^"]+desktop-amd64\.iso)"', html)
                if not names:
                    continue
                filename = names[0]
                sums_url = urljoin(page, "SHA256SUMS")
                sums = parse_sha256sums(fetch_text(sums_url))
                digest = sums.get(filename, "")
                image_url = validate_download_url(urljoin(page, filename))
                return [ReleaseImage(
                    distro="Lubuntu", version=version, architecture="amd64",
                    image_url=image_url, filename=filename, sha256=digest,
                    checksum_url=sums_url, source_page=page
                )]
            except Exception as e:
                errors.append(f"{version}: {e}")
        raise ResolverError("No usable Lubuntu release image was resolved. " + "; ".join(errors[:3]))
