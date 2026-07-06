import re
import xml.etree.ElementTree as ET
from vajra.architecture.normalize import normalize_architecture
from vajra.sources.base import Resolver, ResolverError, UnsupportedArchitecture
from vajra.sources.http import fetch_text
from vajra.sources.models import ReleaseImage
from vajra.sources.security import validate_download_url

class MXLinuxXfceResolver(Resolver):
    distro_ids=("mx-linux-xfce",)
    rss="https://sourceforge.net/projects/mx-linux/rss?path=/Final/Xfce"

    def resolve(self,architecture):
        arch=normalize_architecture(architecture)
        if arch!="amd64":
            raise UnsupportedArchitecture("MX Linux Xfce resolver currently selects x64 images.")
        root=ET.fromstring(fetch_text(self.rss))
        candidates=[]
        for item in root.findall(".//item"):
            title=(item.findtext("title") or "").strip()
            link=(item.findtext("link") or "").strip()
            enc=item.find("enclosure")
            enc_url=enc.get("url","").strip() if enc is not None else ""
            filename=title.rsplit("/",1)[-1]
            low=filename.lower()
            if not low.endswith(".iso") or "xfce" not in low:
                continue
            if not any(x in low for x in ("x64","64","amd64")):
                continue
            url=enc_url or link
            if url.startswith("http://"):
                url="https://"+url[7:]
            validate_download_url(url)
            m=re.search(r"MX-([0-9.]+)",filename,re.I)
            candidates.append((m.group(1) if m else "current",filename,url))
        if not candidates:
            raise ResolverError("No stable MX Linux Xfce x64 ISO found in the official Final/Xfce feed.")
        version,filename,url=candidates[0]
        return [ReleaseImage(distro="MX Linux Xfce",version=version,architecture="amd64",
            image_url=url,filename=filename,
            source_page="https://sourceforge.net/projects/mx-linux/files/Final/Xfce/")]
