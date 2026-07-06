import re
from urllib.parse import urljoin
from vajra.architecture.normalize import normalize_architecture
from vajra.sources.base import Resolver, ResolverError, UnsupportedArchitecture
from vajra.sources.checksums import parse_sha256sums
from vajra.sources.http import fetch_text
from vajra.sources.models import ReleaseImage
from vajra.sources.security import validate_download_url

class LinuxMintXfceResolver(Resolver):
    distro_ids=("linux-mint-xfce",)
    base="https://mirrors.kernel.org/linuxmint/stable/"

    def resolve(self,architecture):
        arch=normalize_architecture(architecture)
        if arch!="amd64":
            raise UnsupportedArchitecture("Current Linux Mint Xfce images are resolved for amd64 only.")
        index=fetch_text(self.base)
        versions=sorted(
            set(re.findall(r'href="(\d+\.\d+(?:\.\d+)?)/"',index)),
            key=lambda s:tuple(int(x) for x in s.split(".")),reverse=True)
        errors=[]
        for version in versions[:10]:
            page=urljoin(self.base,version+"/")
            try:
                html=fetch_text(page)
                names=re.findall(r'href="(linuxmint-[^"]+-xfce-64bit\.iso)"',html,re.I)
                if not names: continue
                filename=sorted(set(names))[-1]
                sums_url=urljoin(page,"sha256sum.txt")
                sums=parse_sha256sums(fetch_text(sums_url))
                url=validate_download_url(urljoin(page,filename))
                return [ReleaseImage(
                    distro="Linux Mint Xfce",version=version,architecture="amd64",
                    image_url=url,filename=filename,sha256=sums.get(filename,""),
                    checksum_url=sums_url,source_page=page
                )]
            except Exception as e:
                errors.append(f"{version}: {e}")
        raise ResolverError("No usable Linux Mint Xfce image resolved. "+"; ".join(errors[:4]))
