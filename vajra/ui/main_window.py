import webbrowser
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QFrame, QGridLayout, QComboBox, QScrollArea,
    QMessageBox, QProgressBar
)

from vajra.hardware.scanner import scan_hardware
from vajra.catalog.loader import load_distros
from vajra.recommender.engine import recommend_distros
from vajra.ui.download_dialog import DownloadDialog
from vajra.ui.distro_browser import DistroBrowser
from vajra.ui.usb_dialog import UsbDeviceDialog
from vajra.ui.flash_dialog import FlashDialog
from vajra.ui.catalog_download_dialog import CatalogDownloadDialog


class ScanWorker(QThread):
    finished_scan = Signal(dict)
    failed = Signal(str)

    def run(self):
        try:
            self.finished_scan.emit(scan_hardware())
        except Exception as exc:
            self.failed.emit(str(exc))


class Card(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("card")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.hardware = None
        self.setWindowTitle("Vajra Bi-Bootin")
        self.resize(1050, 720)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.welcome_page = self.build_welcome_page()
        self.scan_page = self.build_scan_page()
        self.preferences_page = self.build_preferences_page()
        self.results_page = QWidget()

        self.stack.addWidget(self.welcome_page)
        self.stack.addWidget(self.scan_page)
        self.stack.addWidget(self.preferences_page)
        self.stack.addWidget(self.results_page)

        self.setStyleSheet(self.stylesheet())

    def title(self, text, subtitle=None):
        box = QVBoxLayout()
        heading = QLabel(text)
        heading.setObjectName("title")
        box.addWidget(heading)
        if subtitle:
            sub = QLabel(subtitle)
            sub.setObjectName("subtitle")
            sub.setWordWrap(True)
            box.addWidget(sub)
        return box

    def build_welcome_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(70, 60, 70, 60)
        layout.addStretch()

        brand = QLabel("VAJRA")
        brand.setObjectName("brand")
        brand.setAlignment(Qt.AlignCenter)
        layout.addWidget(brand)

        name = QLabel("Bi-Bootin")
        name.setObjectName("hero")
        name.setAlignment(Qt.AlignCenter)
        layout.addWidget(name)

        desc = QLabel(
            "Find a Linux distribution suited to your hardware and needs.\n"
            "Vajra scans locally, filters incompatible choices, and explains its ranking."
        )
        desc.setObjectName("subtitle")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        start = QPushButton("Scan My PC")
        start.setObjectName("primary")
        start.setFixedWidth(220)
        start.clicked.connect(self.start_scan)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(start)
        row.addStretch()
        layout.addLayout(row)

        choice_row = QHBoxLayout()
        manual = QPushButton("Choose Linux Myself")
        manual.clicked.connect(self.open_distro_browser)
        existing = QPushButton("Download / Existing ISO Path")
        existing.clicked.connect(self.open_download_center)
        choice_row.addStretch()
        usb_check = QPushButton("Check USB Devices")
        usb_check.clicked.connect(self.open_usb_devices)
        choice_row.addWidget(manual)
        choice_row.addWidget(existing)
        flash_usb = QPushButton("Write Image to USB")
        flash_usb.clicked.connect(self.open_flash_dialog)
        choice_row.addWidget(usb_check)
        choice_row.addWidget(flash_usb)
        choice_row.addStretch()
        layout.addLayout(choice_row)
        layout.addStretch()
        return page

    def build_scan_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(70, 60, 70, 60)
        layout.addLayout(self.title("Scanning your PC", "Hardware detection runs locally on this computer."))
        layout.addStretch()

        self.scan_status = QLabel("Preparing scan…")
        self.scan_status.setAlignment(Qt.AlignCenter)
        self.scan_status.setObjectName("scanStatus")
        layout.addWidget(self.scan_status)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        layout.addWidget(self.progress)
        layout.addStretch()
        return page

    def start_scan(self):
        self.stack.setCurrentWidget(self.scan_page)
        self.scan_status.setText("Detecting CPU, memory, graphics, storage and firmware…")
        self.worker = ScanWorker()
        self.worker.finished_scan.connect(self.scan_complete)
        self.worker.failed.connect(self.scan_failed)
        self.worker.start()

    def scan_complete(self, hardware):
        self.hardware = hardware
        self.refresh_preferences_summary()
        self.stack.setCurrentWidget(self.preferences_page)

    def scan_failed(self, message):
        QMessageBox.critical(self, "Scan failed", message)
        self.stack.setCurrentWidget(self.welcome_page)

    def build_preferences_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(50, 35, 50, 35)
        layout.addLayout(self.title("Hardware detected", "Review the scan, then tell Vajra what you want to do with Linux."))

        self.hardware_grid = QGridLayout()
        layout.addLayout(self.hardware_grid)

        prefs = Card()
        form = QGridLayout(prefs)
        purpose_label = QLabel("Main use")
        self.purpose = QComboBox()
        self.purpose.addItem("Daily use", "daily_use")
        self.purpose.addItem("Coding", "coding")
        self.purpose.addItem("Older / low-spec PC", "old_pc")
        self.purpose.addItem("Stable workstation", "stable")

        experience_label = QLabel("Linux experience")
        self.experience = QComboBox()
        self.experience.addItem("Beginner", "beginner")
        self.experience.addItem("Intermediate", "intermediate")

        form.addWidget(purpose_label, 0, 0)
        form.addWidget(self.purpose, 0, 1)
        form.addWidget(experience_label, 1, 0)
        form.addWidget(self.experience, 1, 1)
        layout.addWidget(prefs)

        button_row = QHBoxLayout()
        back = QPushButton("← Back")
        back.clicked.connect(self.show_welcome)
        button_row.addWidget(back)

        rescan = QPushButton("Scan Again")
        rescan.clicked.connect(self.start_scan)
        recommend = QPushButton("Find My Linux")
        recommend.setObjectName("primary")
        recommend.clicked.connect(self.show_recommendations)
        button_row.addWidget(rescan)
        downloads = QPushButton("Download Center")
        downloads.clicked.connect(self.open_download_center)
        button_row.addWidget(downloads)
        button_row.addStretch()
        button_row.addWidget(recommend)
        layout.addLayout(button_row)
        return page

    def refresh_preferences_summary(self):
        while self.hardware_grid.count():
            item = self.hardware_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        fields = [
            ("CPU", self.hardware.get("cpu")),
            ("Architecture", self.hardware.get("architecture")),
            ("RAM", f'{self.hardware.get("ram_gb")} GB'),
            ("CPU cores", str(self.hardware.get("physical_cores"))),
            ("GPU", self.hardware.get("gpu")),
            ("Firmware", self.hardware.get("firmware")),
            ("Secure Boot", self.hardware.get("secure_boot")),
            ("Free disk", f'{self.hardware.get("disk_free_gb")} GB'),
        ]
        for index, (label, value) in enumerate(fields):
            card = Card()
            box = QVBoxLayout(card)
            key = QLabel(label)
            key.setObjectName("cardKey")
            val = QLabel(str(value))
            val.setObjectName("cardValue")
            val.setWordWrap(True)
            box.addWidget(key)
            box.addWidget(val)
            self.hardware_grid.addWidget(card, index // 4, index % 4)

    def show_welcome(self):
        self.stack.setCurrentIndex(0)

    def open_flash_dialog(self):
        FlashDialog(parent=self).exec()

    def open_usb_devices(self):
        UsbDeviceDialog(parent=self).exec()

    def open_distro_browser(self):
        DistroBrowser(parent=self).exec()

    def open_download_center(self):
        DownloadDialog(parent=self).exec()

    def show_recommendations(self):
        preferences = {
            "purpose": self.purpose.currentData(),
            "experience": self.experience.currentData(),
        }
        results = recommend_distros(self.hardware, load_distros(), preferences)

        new_page = QWidget()
        outer = QVBoxLayout(new_page)
        outer.setContentsMargins(45, 30, 45, 30)
        outer.addLayout(self.title("Your Linux matches", "Compatibility is filtered first; scores then rank suitable choices."))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        cards = QVBoxLayout(content)

        if not results:
            empty = QLabel("No compatible distro was found in the current starter catalog.")
            empty.setWordWrap(True)
            cards.addWidget(empty)

        for rank, result in enumerate(results[:5], 1):
            card = Card()
            layout = QVBoxLayout(card)

            top = QHBoxLayout()
            name = QLabel(f"{rank}. {result['name']}")
            name.setObjectName("resultName")
            score = QLabel(f"{result['score']}/100")
            score.setObjectName("score")
            top.addWidget(name)
            top.addStretch()
            top.addWidget(score)
            layout.addLayout(top)

            reasons = QLabel(" • " + "\n • ".join(result["reasons"]))
            reasons.setWordWrap(True)
            layout.addWidget(reasons)

            download = QPushButton("Open Official Download Page")
            download.clicked.connect(
                lambda checked=False, url=result["official_download_page"]: webbrowser.open(url)
            )
            layout.addWidget(download, alignment=Qt.AlignRight)
            cards.addWidget(card)

        cards.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)

        bottom = QHBoxLayout()
        back = QPushButton("Change Preferences")
        back.clicked.connect(lambda: self.stack.setCurrentWidget(self.preferences_page))
        bottom.addWidget(back)
        bottom.addStretch()
        outer.addLayout(bottom)

        old = self.results_page
        index = self.stack.indexOf(old)
        self.stack.removeWidget(old)
        old.deleteLater()
        self.results_page = new_page
        self.stack.insertWidget(index, self.results_page)
        self.stack.setCurrentWidget(self.results_page)

    def stylesheet(self):
        return """
        QMainWindow, QWidget {
            background: #0b1020;
            color: #e8edf7;
            font-family: Inter, Segoe UI, Arial;
            font-size: 14px;
        }
        #brand {
            font-size: 18px;
            font-weight: 800;
            letter-spacing: 8px;
            color: #8da2fb;
        }
        #hero {
            font-size: 54px;
            font-weight: 800;
            margin: 8px;
        }
        #title {
            font-size: 30px;
            font-weight: 750;
        }
        #subtitle {
            color: #aab4c8;
            font-size: 15px;
            margin-bottom: 18px;
        }
        #card {
            background: #151c30;
            border: 1px solid #26304b;
            border-radius: 12px;
            padding: 8px;
        }
        #cardKey {
            color: #8f9bb3;
            font-size: 12px;
        }
        #cardValue {
            font-size: 15px;
            font-weight: 650;
        }
        #resultName {
            font-size: 20px;
            font-weight: 750;
        }
        #score {
            font-size: 18px;
            font-weight: 800;
            color: #9aabff;
        }
        #scanStatus {
            font-size: 18px;
            margin: 18px;
        }
        QPushButton {
            background: #202a44;
            border: 1px solid #35415f;
            border-radius: 8px;
            padding: 10px 16px;
        }
        QPushButton:hover {
            background: #293653;
        }
        QPushButton#primary {
            background: #5268d8;
            border: none;
            font-weight: 700;
            padding: 12px 20px;
        }
        QPushButton#primary:hover {
            background: #6177e7;
        }
        QComboBox {
            background: #0f1628;
            border: 1px solid #35415f;
            border-radius: 7px;
            padding: 8px;
            min-width: 220px;
        }
        QProgressBar {
            border: 1px solid #35415f;
            border-radius: 6px;
            min-height: 14px;
        }
        QProgressBar::chunk {
            background: #5268d8;
        }
        QScrollArea {
            border: none;
        }
        """
