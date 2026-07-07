import platform
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from vajra.catalog.loader import load_distros
from vajra.sources.registry import RESOLVERS
from vajra.ui.dialog_theme import DIALOG_STYLE
from vajra.ui.resolved_download_dialog import ResolvedDownloadDialog

class CatalogDownloadDialog(QDialog):
    image_ready = Signal(str)
    verified_image_ready = Signal(str, str)

    def __init__(self, parent=None, selected_name=""):
        super().__init__(parent)
        self.setStyleSheet(DIALOG_STYLE)
        self.setWindowTitle("Download Linux ISO")
        self.resize(620, 260)
        self.entries = [d for d in load_distros() if d.get("id") in RESOLVERS]
        layout = QVBoxLayout(self)
        title = QLabel("Download Linux ISO")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        info = QLabel("Choose a distribution. Vajra will resolve the current official image and checksum before downloading.")
        info.setWordWrap(True)
        layout.addWidget(info)
        self.combo = QComboBox()
        for distro in self.entries:
            self.combo.addItem(distro["name"], distro["id"])
        layout.addWidget(self.combo)
        if selected_name:
            wanted = selected_name.strip().lower()
            for i, distro in enumerate(self.entries):
                if distro.get("name", "").lower() == wanted or distro.get("id", "").lower() == wanted:
                    self.combo.setCurrentIndex(i)
                    break
        self.details = QLabel()
        self.details.setWordWrap(True)
        layout.addWidget(self.details)
        row = QHBoxLayout()
        self.download_button = QPushButton("Resolve Official ISO")
        self.download_button.setObjectName("primaryAction")
        self.cancel_button = QPushButton("Close")
        row.addWidget(self.download_button)
        row.addWidget(self.cancel_button)
        layout.addLayout(row)
        self.combo.currentIndexChanged.connect(self.update_details)
        self.download_button.clicked.connect(self.start_download)
        self.cancel_button.clicked.connect(self.reject)
        self.update_details()

    def current_entry(self):
        i = self.combo.currentIndex()
        return self.entries[i] if 0 <= i < len(self.entries) else None

    def update_details(self):
        distro = self.current_entry()
        if not distro:
            self.details.setText("No supported distributions are available.")
            self.download_button.setEnabled(False)
            return
        self.details.setText(f"{distro['name']} - {distro.get('desktop', 'Desktop')}\nRelease URL and SHA-256 will be resolved from the supported source.")
        self.download_button.setEnabled(True)

    def start_download(self):
        distro = self.current_entry()
        if not distro:
            return
        machine = platform.machine().lower()
        architecture = "amd64" if machine in ("x86_64", "amd64") else machine
        dialog = ResolvedDownloadDialog(distro["id"], architecture, parent=self)
        dialog.image_ready.connect(lambda path: self.image_ready.emit(path))
        dialog.verified_image_ready.connect(lambda path, digest: self.verified_image_ready.emit(path, digest))
        dialog.exec()
