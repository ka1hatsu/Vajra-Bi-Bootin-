from pathlib import Path
from urllib.parse import urlparse

from PySide6.QtWidgets import (
    QComboBox, QDialog, QFileDialog, QFormLayout, QHBoxLayout,
    QLabel, QMessageBox, QProgressBar, QPushButton, QVBoxLayout,
)

from vajra.downloader.catalog_adapter import load_download_choices
from vajra.downloader.worker import DownloadWorker


def human_bytes(value):
    value = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return f"{value:.1f} {unit}"
        value /= 1024


class CatalogDownloadDialog(QDialog):
    image_ready = __import__("PySide6.QtCore", fromlist=["Signal"]).Signal(str)

    def __init__(self, parent=None, selected_name=""):
        super().__init__(parent)
        self.setWindowTitle("Download Linux ISO")
        self.resize(620, 280)
        self.worker = None
        self.choices = load_download_choices()

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.combo = QComboBox()

        for choice in self.choices:
            self.combo.addItem(choice.name)

        if selected_name:
            for i, choice in enumerate(self.choices):
                if choice.name.lower() == selected_name.lower():
                    self.combo.setCurrentIndex(i)
                    break

        form.addRow("Distribution", self.combo)
        layout.addLayout(form)

        self.details = QLabel()
        self.details.setWordWrap(True)
        layout.addWidget(self.details)

        self.progress = QProgressBar()
        self.status = QLabel("Ready")
        layout.addWidget(self.progress)
        layout.addWidget(self.status)

        row = QHBoxLayout()
        self.download_button = QPushButton("Download ISO")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        row.addWidget(self.download_button)
        row.addWidget(self.cancel_button)
        layout.addLayout(row)

        self.combo.currentIndexChanged.connect(self.update_details)
        self.download_button.clicked.connect(self.start_download)
        self.cancel_button.clicked.connect(self.cancel_download)
        self.update_details()

    def current_choice(self):
        i = self.combo.currentIndex()
        return self.choices[i] if 0 <= i < len(self.choices) else None

    def update_details(self):
        choice = self.current_choice()
        if not choice:
            self.details.setText(
                "No downloadable ISO entries were found in distros.json. "
                "Add download_url or iso_url fields to catalog entries."
            )
            self.download_button.setEnabled(False)
            return

        checksum = "Checksum available" if choice.sha256 else "No checksum in catalog"
        self.details.setText(f"{choice.name}\n{checksum}")
        self.download_button.setEnabled(True)

    def default_filename(self, choice):
        if choice.filename:
            return choice.filename
        name = Path(urlparse(choice.url).path).name
        return name or f"{choice.name.replace(' ', '-')}.iso"

    def start_download(self):
        choice = self.current_choice()
        if not choice:
            return

        destination, _ = QFileDialog.getSaveFileName(
            self,
            "Save ISO",
            str(Path.home() / "Downloads" / self.default_filename(choice)),
            "ISO images (*.iso);;All files (*)",
        )
        if not destination:
            return

        self.worker = DownloadWorker(
            choice.url,
            destination,
            choice.sha256 or None,
            self,
        )
        self.worker.progress.connect(self.on_progress)
        self.worker.completed.connect(self.on_complete)
        self.worker.failed.connect(self.on_failed)
        self.worker.cancelled_signal.connect(self.on_cancelled)

        self.download_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.worker.start()

    def cancel_download(self):
        if self.worker:
            self.worker.cancel()
            self.status.setText("Cancelling...")

    def on_progress(self, done, total, speed, eta):
        if total:
            self.progress.setRange(0, 100)
            self.progress.setValue(int(done * 100 / total))
        else:
            self.progress.setRange(0, 0)

        eta_text = f" | ETA {int(eta)}s" if eta >= 0 else ""
        self.status.setText(
            f"{human_bytes(done)}"
            + (f" / {human_bytes(total)}" if total else "")
            + f" | {human_bytes(speed)}/s{eta_text}"
        )

    def reset_buttons(self):
        self.progress.setRange(0, 100)
        self.download_button.setEnabled(bool(self.choices))
        self.cancel_button.setEnabled(False)

    def on_complete(self, path, digest):
        self.reset_buttons()
        self.progress.setValue(100)
        self.status.setText(f"Verified and ready: {path}")
        self.image_ready.emit(path)
        QMessageBox.information(
            self,
            "ISO ready",
            f"Download completed.\n\n{path}\n\nSHA-256:\n{digest}",
        )

    def on_failed(self, message):
        self.reset_buttons()
        self.status.setText("Download failed; partial file kept for resume.")
        QMessageBox.critical(self, "Download failed", message)

    def on_cancelled(self):
        self.reset_buttons()
        self.status.setText("Cancelled; partial file kept for resume.")
