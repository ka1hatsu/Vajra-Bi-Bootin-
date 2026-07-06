import json, time
from dataclasses import asdict
from pathlib import Path
from vajra.sources.models import ReleaseImage

class ResolverCache:
    def __init__(self, path=None, ttl=3600):
        self.path = Path(path or (Path.home()/".cache/vajra-bi/resolver-cache.json"))
        self.ttl = ttl

    def get(self, key):
        try:
            data = json.loads(self.path.read_text())
            item = data[key]
            if time.time() - item["saved_at"] > self.ttl:
                return None
            return [ReleaseImage(**x) for x in item["images"]]
        except Exception:
            return None

    def put(self, key, images):
        try:
            data = json.loads(self.path.read_text()) if self.path.exists() else {}
        except Exception:
            data = {}
        data[key] = {"saved_at": time.time(), "images": [asdict(x) for x in images]}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2))
