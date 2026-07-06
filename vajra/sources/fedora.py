import json
import re

FEDORA_SHA_RE = re.compile(
    r"SHA256\s*\(([^)]+\.iso)\)\s*=\s*([0-9a-fA-F]{64})"
)

from vajra.architecture.normalize import normalize_architecture
from vajra.sources.base import Resolver, ResolverError, UnsupportedArchitecture
from vajra.sources.http import fetch_text
from vajra.sources.models import ReleaseImage
from vajra.sources.security import validate_download_url

def walk_json(value):
    if isinstance(value,dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value,list):
        for child in value:
            yield from walk_json(child)

def first_string(d,*keys):
    for key in keys:
        value=d.get(key)
        if isinstance(value,str) and value:
            return value
    return ""

class FedoraWorkstationResolver(Resolver):
    distro_ids=("fedora-workstation",)
    metadata="https://fedoraproject.org/releases.json"

    def resolve(self,architecture):
        arch=normalize_architecture(architecture)
        if arch!="amd64":
            raise UnsupportedArchitecture("Fedora Workstation resolver currently selects x86_64 images.")
        data=json.loads(fetch_text(self.metadata,max_bytes=32*1024*1024))
        candidates=[]
        for node in walk_json(data):
            blob=" ".join(str(v) for v in node.values() if isinstance(v,(str,int))).lower()
            if "workstation" not in blob or "x86_64" not in blob:
                continue
            url=first_string(node,"link","url","download","location")
            filename=first_string(node,"filename","name")
            sha256=first_string(node,"sha256","checksum","sha256sum")
            if not url.lower().split("?",1)[0].endswith(".iso"):
                continue
            if not filename:
                filename=url.split("?",1)[0].rsplit("/",1)[-1]
            if len(sha256)!=64: sha256=""
            validate_download_url(url)
            version=str(node.get("version") or node.get("release") or "current")
            candidates.append(ReleaseImage(distro="Fedora Workstation",version=version,
                architecture="amd64",image_url=url,filename=filename,sha256=sha256,
                source_page="https://fedoraproject.org/workstation/download/"))
        if not candidates:
            raise ResolverError("Fedora release metadata contained no compatible Workstation x86_64 ISO.")
        candidates.sort(key=lambda x:x.version,reverse=True)
        return [candidates[0]]
