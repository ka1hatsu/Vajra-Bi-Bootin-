from pathlib import Path

p=Path("vajra/ui/main_window.py")
s=p.read_text()

anchor="from PySide6.QtCore import Qt, QThread, Signal\n"
if "from PySide6.QtGui import QPixmap, QIcon" not in s:
    if anchor not in s: raise SystemExit("QtCore import anchor not found")
    s=s.replace(anchor,anchor+"from PySide6.QtGui import QPixmap, QIcon\n",1)

title='        self.setWindowTitle("Vajra Bi-Bootin")\n'
if "self.setWindowIcon(QIcon(str(asset_path)))" not in s:
    replacement=title+'        asset_path = Path(__file__).resolve().parents[1] / "assets" / "vajra_logo.png"\n        self.setWindowIcon(QIcon(str(asset_path)))\n'
    if title not in s: raise SystemExit("window title anchor not found")
    s=s.replace(title,replacement,1)

start=s.index("    def build_welcome_page(self):")
end=s.index("    def build_scan_page(self):",start)
s=s[:start]+'    def build_welcome_page(self):\n        page = QWidget()\n        page.setObjectName("welcomePage")\n        layout = QVBoxLayout(page)\n        layout.setContentsMargins(80, 34, 80, 40)\n        layout.setSpacing(12)\n        layout.addStretch()\n\n        logo = QLabel()\n        logo.setObjectName("welcomeLogo")\n        logo.setAlignment(Qt.AlignCenter)\n        logo_path = Path(__file__).resolve().parents[1] / "assets" / "vajra_logo.png"\n        pixmap = QPixmap(str(logo_path))\n        if not pixmap.isNull():\n            logo.setPixmap(pixmap.scaled(340, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation))\n        logo.setAccessibleName("Vajra logo")\n        layout.addWidget(logo)\n\n        name = QLabel("Vajra Bi-Bootin")\n        name.setObjectName("hero")\n        name.setAlignment(Qt.AlignCenter)\n        layout.addWidget(name)\n\n        desc = QLabel("Choose the right Linux image, download it safely, and create bootable USB media.")\n        desc.setObjectName("welcomeSubtitle")\n        desc.setAlignment(Qt.AlignCenter)\n        desc.setWordWrap(True)\n        layout.addWidget(desc)\n\n        start = QPushButton("Scan My PC")\n        start.setObjectName("primary")\n        start.setFixedWidth(240)\n        start.setToolTip("Detect hardware locally and recommend compatible Linux distributions.")\n        start.clicked.connect(self.start_scan)\n        row = QHBoxLayout(); row.addStretch(); row.addWidget(start); row.addStretch()\n        layout.addLayout(row)\n\n        quick = QHBoxLayout()\n        manual = QPushButton("Choose Linux"); manual.clicked.connect(self.open_distro_browser)\n        existing = QPushButton("Download ISO"); existing.clicked.connect(self.open_download_center)\n        usb_check = QPushButton("USB Devices"); usb_check.clicked.connect(self.open_usb_devices)\n        flash_usb = QPushButton("Write to USB"); flash_usb.setObjectName("accentAction"); flash_usb.clicked.connect(self.open_flash_dialog)\n        quick.addStretch()\n        for button in (manual, existing, usb_check, flash_usb):\n            button.setMinimumWidth(145)\n            quick.addWidget(button)\n        quick.addStretch()\n        layout.addLayout(quick)\n\n        secondary = QHBoxLayout()\n        history = QPushButton("Download History"); history.setObjectName("secondaryAction"); history.clicked.connect(self.open_download_history)\n        reports = QPushButton("Operation Reports"); reports.setObjectName("secondaryAction"); reports.clicked.connect(self.open_operation_reports)\n        secondary.addStretch(); secondary.addWidget(history); secondary.addWidget(reports); secondary.addStretch()\n        layout.addLayout(secondary)\n        layout.addStretch()\n        return page\n\n'+s[end:]

style_marker='        QScrollArea {\n            border: none;\n        }\n'
if "#welcomePage" not in s:
    if style_marker not in s: raise SystemExit("stylesheet anchor not found")
    s=s.replace(style_marker,style_marker+'\n        #welcomePage {\n            background: qradialgradient(cx:0.5, cy:0.35, radius:0.9,\n                stop:0 #111a32, stop:0.55 #0b1224, stop:1 #080d19);\n        }\n        #welcomeLogo { min-height: 210px; background: transparent; }\n        #welcomeSubtitle {\n            font-size: 16px; color: #aebbd3; padding: 2px 16px 12px 16px;\n        }\n        QPushButton#accentAction {\n            background: #1d62d8; border: 1px solid #3279ef; font-weight: 700;\n        }\n        QPushButton#accentAction:hover { background: #2870e8; }\n        QPushButton#secondaryAction {\n            background: transparent; border: 1px solid #2d3955;\n            color: #aebbd3; padding: 8px 14px;\n        }\n        QPushButton#secondaryAction:hover { background: #141e34; color: #eef4ff; }\n',1)

p.write_text(s)
print("Phase 9.6 applied.")
