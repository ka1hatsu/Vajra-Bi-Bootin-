import re
from urllib.parse import urljoin
from vajra.architecture.normalize import normalize_architecture
from vajra.sources.base import Resolver, ResolverError, UnsupportedArchitecture
from vajra.sources.checksums import parse_sha256sums
from vajra.sources.http import fetch_text
from vajra.sources.models import ReleaseImage
from vajra.sources.security import validate_download_url

class DebianXfceResolver(Resolver):
    distro_ids=("debian-xfce",)
    base="https://cdimage.debian.org/debian-cd/current-live/amd64/iso-hybrid/"

    def resolve(self,architecture):
        arch=normalize_architecture(architecture)
        if arch!="amd64":
            raise UnsupportedArchitecture("This Debian Xfce provider currently resolves amd64 live images.")
        html=fetch_text(self.base)
        names=re.findall(r'href="(debian-live-[^"]+-amd64-xfce\.iso)"',html)
        if not names:
            raise ResolverError("No Debian Xfce live ISO found in current-live.")
        filename=sorted(set(names))[-1]
        sums_url=urljoin(self.base,"SHA256SUMS")
        sums=parse_sha256sums(fetch_text(sums_url))
        url=validate_download_url(urljoin(self.base,filename))
        return [ReleaseImage(distro="Debian Xfce",version="current",architecture="amd64",
            image_url=url,filename=filename,sha256=sums.get(filename,""),
            checksum_url=sums_url,source_page=self.base)]
