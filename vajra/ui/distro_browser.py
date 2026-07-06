import webbrowser
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QMessageBox
)

from vajra.catalog.loader import load_distros
from vajra.ui.download_dialog import DownloadDialog


class DistroBrowser(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose Linux Manually")
        self.resize(760, 560)
        self.distros = load_distros()

        layout = QVBoxLayout(self)
        title = QLabel("Choose Linux Manually")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        layout.addWidget(title)

        subtitle = QLabel(
            "Search the catalog, open the official download page, or paste a direct ISO URL "
            "into the Download Center. AI recommendations are optional."
        )
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search Ubuntu, Lubuntu, Mint, Fedora…")
        self.search.textChanged.connect(self.refresh)
        layout.addWidget(self.search)

        self.list = QListWidget()
        self.list.currentItemChanged.connect(self.update_details)
        layout.addWidget(self.list)

        self.details = QLabel("Select a distribution.")
        self.details.setWordWrap(True)
        layout.addWidget(self.details)

        row = QHBoxLayout()
        self.official = QPushButton("Open Official Download Page")
        self.download = QPushButton("Open Download Center")
        self.official.clicked.connect(self.open_official)
        self.download.clicked.connect(self.open_downloader)
        row.addWidget(self.official)
        row.addWidget(self.download)
        layout.addLayout(row)

        self.refresh()

    def refresh(self):
        query = self.search.text().strip().lower()
        self.list.clear()
        for distro in self.distros:
            haystack = " ".join([
                distro.get("name", ""),
                distro.get("desktop", ""),
                " ".join(distro.get("categories", [])),
            ]).lower()
            if query and query not in haystack:
                continue
            item = QListWidgetItem(distro["name"])
            item.setData(Qt.UserRole, distro)
            self.list.addItem(item)

        if self.list.count():
            self.list.setCurrentRow(0)

    def selected(self):
        item = self.list.currentItem()
        return item.data(Qt.UserRole) if item else None

    def update_details(self):
        distro = self.selected()
        if not distro:
            self.details.setText("No distribution selected.")
            return
        self.details.setText(
            f"Desktop: {distro.get('desktop', 'Unknown')}\n"
            f"Difficulty: {distro.get('difficulty', 'Unknown').title()}\n"
            f"Recommended RAM: {distro.get('recommended_ram_gb', '?')} GB\n"
            f"Categories: {', '.join(distro.get('categories', []))}"
        )

    def open_official(self):
        distro = self.selected()
        if distro:
            webbrowser.open(distro["official_download_page"])

    def open_downloader(self):
        DownloadDialog(parent=self).exec()
