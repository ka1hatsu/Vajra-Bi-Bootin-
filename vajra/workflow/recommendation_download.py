from vajra.ui.catalog_download_dialog import CatalogDownloadDialog
from vajra.workflow.image_handoff import ImageHandoff
from vajra.workflow.session import WorkflowSession, sha256_file


class RecommendationDownloadFlow:
    """
    Small controller joining recommendation/manual selection -> downloader ->
    verified local image callback. It does not know MainWindow widget names.
    """

    def __init__(self, parent, on_image_ready):
        self.parent = parent
        self.on_image_ready = on_image_ready
        self.dialog = None
        self.selected_name = ""
        self.session = WorkflowSession()

    def open(self, distro_name=""):
        self.selected_name = distro_name or ""
        self.dialog = CatalogDownloadDialog(
            self.parent,
            selected_name=self.selected_name,
        )
        self.dialog.image_ready.connect(self._ready)
        self.dialog.exec()

    def _ready(self, path):
        digest=sha256_file(path)
        self.session.accept_verified_image(path,digest,self.selected_name)
        handoff = ImageHandoff.from_download(path, self.selected_name, verified_sha256=digest)
        self.on_image_ready(handoff)
