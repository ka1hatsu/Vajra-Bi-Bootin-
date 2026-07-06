import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import time


def default_history_path():
    base = Path(os.environ.get("XDG_STATE_HOME", Path.home()/".local"/"state"))
    return base/"vajra"/"downloads.json"


@dataclass
class DownloadRecord:
    distro_id: str
    distro: str
    version: str
    architecture: str
    filename: str
    path: str
    image_url: str
    expected_sha256: str = ""
    actual_sha256: str = ""
    state: str = "pending"
    bytes_downloaded: int = 0
    total_bytes: int = 0
    updated_at: float = 0.0

    @property
    def verified(self):
        return (
            self.state == "verified"
            and len(self.expected_sha256) == 64
            and self.expected_sha256.lower() == self.actual_sha256.lower()
        )

    @property
    def resumable(self):
        return self.state in {"downloading","cancelled","failed"} and Path(self.path+".part").exists()


class DownloadHistory:
    def __init__(self,path=None):
        self.path=Path(path) if path else default_history_path()

    def load(self):
        if not self.path.exists():
            return []
        try:
            raw=json.loads(self.path.read_text())
            if not isinstance(raw,list):
                return []
            return [DownloadRecord(**item) for item in raw if isinstance(item,dict)]
        except (OSError,ValueError,TypeError):
            return []

    def save(self,records):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        payload=json.dumps([asdict(x) for x in records],indent=2,sort_keys=True)
        with NamedTemporaryFile("w",dir=self.path.parent,delete=False) as f:
            f.write(payload)
            temp=Path(f.name)
        temp.replace(self.path)

    def upsert(self,record):
        record.updated_at=time()
        records=self.load()
        key=(record.distro_id,record.path)
        records=[x for x in records if (x.distro_id,x.path)!=key]
        records.append(record)
        records.sort(key=lambda x:x.updated_at,reverse=True)
        self.save(records)
        return record

    def recent(self,limit=20):
        return self.load()[:limit]

    def remove(self,distro_id,path):
        records=[x for x in self.load() if not (x.distro_id==distro_id and x.path==str(path))]
        self.save(records)

    def get(self,distro_id,path):
        for record in self.load():
            if record.distro_id==distro_id and record.path==str(path): return record
        return None

    def verified_existing(self):
        return [x for x in self.load() if x.verified and Path(x.path).is_file()]
