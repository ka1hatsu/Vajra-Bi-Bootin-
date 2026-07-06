from PySide6.QtCore import QThread,Signal
from vajra.downloader.manager import download_file,DownloadCancelled

class DownloadWorker(QThread):
    progress=Signal(int,int,float,float); completed=Signal(str,str); failed=Signal(str); cancelled_signal=Signal()
    def __init__(self,url,destination,sha256=None,parent=None):
        super().__init__(parent); self.url=url; self.destination=destination; self.sha256=sha256; self._cancel=False
    def cancel(self): self._cancel=True
    def run(self):
        try:
            r=download_file(self.url,self.destination,self.sha256 or None,
                progress=lambda d,t,s,e:self.progress.emit(d,t or 0,s,e if e is not None else -1.0),
                cancelled=lambda:self._cancel)
            self.completed.emit(r.path,r.sha256)
        except DownloadCancelled: self.cancelled_signal.emit()
        except Exception as e: self.failed.emit(str(e))
