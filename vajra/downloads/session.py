from pathlib import Path
from vajra.downloads.history import DownloadHistory, DownloadRecord


class DownloadSession:
    def __init__(self,distro_id,image,destination,history=None):
        self.history=history or DownloadHistory()
        self.record=DownloadRecord(
            distro_id=distro_id,
            distro=image.distro,
            version=image.version,
            architecture=image.architecture,
            filename=image.filename,
            path=str(Path(destination)),
            image_url=image.image_url,
            expected_sha256=image.sha256 or "",
            state="pending",
        )
        self.history.upsert(self.record)

    def progress(self,done,total):
        self.record.state="downloading"
        self.record.bytes_downloaded=int(done)
        self.record.total_bytes=int(total or 0)
        self.history.upsert(self.record)

    def cancelled(self):
        self.record.state="cancelled"
        self.history.upsert(self.record)

    def failed(self):
        self.record.state="failed"
        self.history.upsert(self.record)

    def completed(self,path,digest,verified):
        self.record.path=str(path)
        self.record.actual_sha256=digest or ""
        self.record.state="verified" if verified else "untrusted"
        self.history.upsert(self.record)
