import re
from urllib.parse import urljoin, urlparse
from vajra.architecture.normalize import normalize_architecture
from vajra.sources.base import Resolver, ResolverError
from vajra.sources.http import fetch_text
from vajra.sources.models import ReleaseImage
from vajra.sources.security import validate_download_url

ISO_LINK = re.compile(r'href=["\']([^"\']+\.iso(?:\?[^"\']*)?)["\']', re.I)

class OfficialPageResolver(Resolver):
    def __init__(self, distro_id, name, page):
        self.distro_ids = (distro_id,)
        self.name = name
        self.page = page

    def resolve(self, architecture):
        arch = normalize_architecture(architecture)
        html = fetch_text(self.page)
        links = []
        for href in ISO_LINK.findall(html):
            url = urljoin(self.page, href)
            low = url.lower()
            if arch == "amd64" and not any(x in low for x in ("64bit", "x64", "amd64")):
                continue
            if arch == "i386" and not any(x in low for x in ("32bit", "386", "i686", "x86")):
                continue
            try:
                validate_download_url(url)
            except ValueError:
                continue
            if url not in links:
                links.append(url)
        if not links:
            raise ResolverError(
                f"{self.name}: no compatible direct ISO link was exposed by the official release page."
            )
        return [
            ReleaseImage(
                distro=self.name, version="current", architecture=arch,
                image_url=url, filename=urlparse(url).path.rsplit("/", 1)[-1],
                source_page=self.page
            )
            for url in links[:8]
        ]
