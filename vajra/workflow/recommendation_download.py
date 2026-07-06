from vajra.ui.catalog_download_dialog import CatalogDownloadDialog
from vajra.workflow.image_handoff import ImageHandoff


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

    def open(self, distro_name=""):
        self.selected_name = distro_name or ""
        self.dialog = CatalogDownloadDialog(
            self.parent,
            selected_name=self.selected_name,
        )
        self.dialog.image_ready.connect(self._ready)
        self.dialog.exec()

    def _ready(self, path):
        handoff = ImageHandoff.from_download(path, self.selected_name)
        self.on_image_ready(handoff)
