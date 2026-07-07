from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib

def sha256_file(path,chunk_size=1024*1024):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        while True:
            chunk=f.read(chunk_size)
            if not chunk: break
            h.update(chunk)
    return h.hexdigest()

@dataclass
class WorkflowSession:
    distro_name: str=""
    image_path: str=""
    verified_sha256: str=""
    verification_state: str="unverified"
    target_device: str=""
    flash_state: str="not_started"

    def accept_verified_image(self,path,digest,distro_name=""):
        self.distro_name=distro_name or self.distro_name
        self.image_path=str(path)
        self.verified_sha256=str(digest).lower()
        self.verification_state="verified"

    def validate_image_unchanged(self):
        p=Path(self.image_path)
        if self.verification_state!="verified" or not p.is_file() or not self.verified_sha256:
            return False
        return sha256_file(p)==self.verified_sha256

    def invalidate_verification(self):
        self.verification_state="stale"

    def to_dict(self):
        return asdict(self)
