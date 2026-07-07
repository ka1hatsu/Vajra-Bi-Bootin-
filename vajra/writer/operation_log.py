import json, os
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import time

def default_log_path():
    base=Path(os.environ.get("XDG_STATE_HOME",Path.home()/".local"/"state"))
    return base/"vajra"/"flash_operations.json"

class FlashOperationLog:
    def __init__(self,path=None):
        self.path=Path(path) if path else default_log_path()
    def load(self):
        if not self.path.exists(): return []
        try:
            data=json.loads(self.path.read_text())
            return data if isinstance(data,list) else []
        except (OSError,ValueError): return []
    def append(self,event,**fields):
        rows=self.load()
        rows.append({"time":time(),"event":event,**fields})
        self.path.parent.mkdir(parents=True,exist_ok=True)
        payload=json.dumps(rows[-500:],indent=2,sort_keys=True)
        with NamedTemporaryFile("w",dir=self.path.parent,delete=False) as f:
            f.write(payload); temp=Path(f.name)
        temp.replace(self.path)
