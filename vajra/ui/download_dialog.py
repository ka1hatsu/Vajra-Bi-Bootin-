from pathlib import Path
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QDialog,QVBoxLayout,QLabel,QLineEdit,QPushButton,QFileDialog,QProgressBar,QHBoxLayout,QMessageBox
from vajra.downloader.download import download_file, DownloadCancelled
from vajra.downloader.checksum import verify_sha256

class DownloadWorker(QThread):
    progress=Signal(int); completed=Signal(str); failed=Signal(str)
    def __init__(self,url,destination):
        super().__init__(); self.url=url; self.destination=destination; self.cancelled=False
    def cancel(self): self.cancelled=True
    def run(self):
        try:
            def report(done,total):
                if total: self.progress.emit(int(done*100/total))
            result=download_file(self.url,self.destination,report,lambda:self.cancelled)
            self.completed.emit(str(result))
        except DownloadCancelled: self.failed.emit("Download cancelled.")
        except Exception as exc: self.failed.emit(str(exc))

class DownloadDialog(QDialog):
    def __init__(self,url="",parent=None):
        super().__init__(parent); self.setWindowTitle("ISO Downloader"); self.resize(620,300)
        layout=QVBoxLayout(self)
        layout.addWidget(QLabel("Direct ISO URL")); self.url=QLineEdit(url); layout.addWidget(self.url)
        layout.addWidget(QLabel("Expected SHA-256 (optional)")); self.checksum=QLineEdit(); layout.addWidget(self.checksum)
        self.destination=QLineEdit(str(Path.home()/"Downloads"/"linux.iso"))
        choose=QPushButton("Choose Destination"); choose.clicked.connect(self.choose_destination)
        row=QHBoxLayout(); row.addWidget(self.destination); row.addWidget(choose); layout.addLayout(row)
        self.progress=QProgressBar(); layout.addWidget(self.progress)
        buttons=QHBoxLayout(); self.start_button=QPushButton("Download"); self.cancel_button=QPushButton("Cancel")
        self.cancel_button.setEnabled(False); self.start_button.clicked.connect(self.start_download); self.cancel_button.clicked.connect(self.cancel_download)
        buttons.addWidget(self.start_button); buttons.addWidget(self.cancel_button); layout.addLayout(buttons)
    def choose_destination(self):
        path,_=QFileDialog.getSaveFileName(self,"Save ISO",self.destination.text(),"Disk Images (*.iso *.img);;All Files (*)")
        if path: self.destination.setText(path)
    def start_download(self):
        if not self.url.text().strip():
            QMessageBox.warning(self,"Missing URL","Enter a direct ISO URL."); return
        self.worker=DownloadWorker(self.url.text().strip(),self.destination.text().strip())
        self.worker.progress.connect(self.progress.setValue); self.worker.completed.connect(self.download_complete); self.worker.failed.connect(self.download_failed)
        self.start_button.setEnabled(False); self.cancel_button.setEnabled(True); self.worker.start()
    def cancel_download(self):
        if hasattr(self,"worker"): self.worker.cancel()
    def download_complete(self,path):
        self.start_button.setEnabled(True); self.cancel_button.setEnabled(False); expected=self.checksum.text().strip()
        if expected and not verify_sha256(path,expected):
            QMessageBox.critical(self,"Checksum mismatch","The file does not match the expected SHA-256. Do not use this image."); return
        QMessageBox.information(self,"Complete",f"Downloaded successfully:\n{path}")
    def download_failed(self,message):
        self.start_button.setEnabled(True); self.cancel_button.setEnabled(False); QMessageBox.warning(self,"Download stopped",message)
