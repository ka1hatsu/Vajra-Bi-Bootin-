from PySide6.QtCore import QThread, Signal
from vajra.sources.service import ResolverService

class ReleaseResolverWorker(QThread):
    completed = Signal(list)
    failed = Signal(str)

    def __init__(self, distro_id, architecture, parent=None):
        super().__init__(parent)
        self.distro_id = distro_id
        self.architecture = architecture

    def run(self):
        try:
            images = ResolverService().resolve(self.distro_id, self.architecture)
            self.completed.emit(images)
        except Exception as e:
            self.failed.emit(str(e))
