from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QMessageBox
)
from vajra.downloads.history import DownloadHistory
from vajra.downloads.library import inspect_record


class DownloadHistoryDialog(QDialog):
    flash_requested = Signal(str)
    resume_requested = Signal(str, str, str)

    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download History")
        self.resize(760,520)
        self.history=DownloadHistory()

        layout=QVBoxLayout(self)
        title=QLabel("Download History")
        title.setStyleSheet("font-size:24px;font-weight:700;")
        layout.addWidget(title)

        self.scroll=QScrollArea()
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll)

        buttons=QHBoxLayout()
        refresh=QPushButton("Refresh")
        refresh.clicked.connect(self.refresh)
        close=QPushButton("Close")
        close.clicked.connect(self.reject)
        buttons.addWidget(refresh)
        buttons.addStretch()
        buttons.addWidget(close)
        layout.addLayout(buttons)
        self.refresh()

    def refresh(self):
        content=QWidget()
        box=QVBoxLayout(content)
        records=self.history.recent(50)

        if not records:
            label=QLabel("No download history yet.")
            box.addWidget(label)

        for record in records:
            card=QFrame()
            card.setFrameShape(QFrame.StyledPanel)
            row=QVBoxLayout(card)

            name=QLabel(f"{record.distro} {record.version} • {record.architecture}")
            name.setStyleSheet("font-weight:700;")
            row.addWidget(name)

            details=QLabel(
                f"{record.filename}\n"
                f"State: {record.state}\n"
                f"Path: {record.path}"
            )
            details.setWordWrap(True)
            row.addWidget(details)

            actions=QHBoxLayout()
            recheck=QPushButton("Recheck ISO")
            recheck.clicked.connect(lambda checked=False,r=record:self.recheck_record(r))
            remove=QPushButton("Remove Entry")
            remove.clicked.connect(lambda checked=False,r=record:self.remove_record(r))
            actions.addWidget(recheck)
            actions.addWidget(remove)
            if record.resumable:
                resume=QPushButton("Resume")
                resume.setToolTip("Resume is available from the distro download flow.")
                resume.clicked.connect(
                    lambda checked=False, r=record: self.request_resume(r)
                )
                actions.addWidget(resume)

            if record.verified and Path(record.path).is_file():
                flash=QPushButton("Flash Again")
                flash.clicked.connect(
                    lambda checked=False, p=record.path: self.request_flash(p)
                )
                actions.addWidget(flash)

            actions.addStretch()
            row.addLayout(actions)
            box.addWidget(card)

        box.addStretch()
        self.scroll.setWidget(content)

    def request_resume(self,record):
        self.resume_requested.emit(record.distro_id,record.architecture,record.path)
        self.accept()

    def recheck_record(self,record):
        state,digest=inspect_record(record)
        record.state=state
        if digest: record.actual_sha256=digest
        self.history.upsert(record)
        QMessageBox.information(self,"ISO check complete",f"State: {state}")
        self.refresh()

    def remove_record(self,record):
        self.history.remove(record.distro_id,record.path)
        self.refresh()

    def show_resume_info(self,record):
        QMessageBox.information(
            self,
            "Resume available",
            "Open the same distro download again and choose the same destination. "
            "Vajra will reuse the existing .part file.",
        )

    def request_flash(self,path):
        if not Path(path).is_file():
            QMessageBox.warning(self,"Missing image","The ISO file no longer exists.")
            self.refresh()
            return
        self.flash_requested.emit(path)
        self.accept()
