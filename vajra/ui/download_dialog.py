from pathlib import Path
from PySide6.QtWidgets import QDialog,QVBoxLayout,QFormLayout,QLineEdit,QPushButton,QFileDialog,QProgressBar,QLabel,QHBoxLayout,QMessageBox
from vajra.downloader.worker import DownloadWorker

def human_bytes(v):
    v=float(v)
    for u in ("B","KiB","MiB","GiB","TiB"):
        if v<1024 or u=="TiB": return f"{v:.1f} {u}"
        v/=1024

class DownloadDialog(QDialog):
    def __init__(self,parent=None,url="",sha256=""):
        super().__init__(parent); self.setWindowTitle("Vajra Download Manager"); self.resize(620,300); self.worker=None
        l=QVBoxLayout(self); f=QFormLayout()
        self.url=QLineEdit(url); self.destination=QLineEdit(); self.sha256=QLineEdit(sha256)
        self.sha256.setPlaceholderText("Optional SHA-256 checksum")
        browse=QPushButton("Choose destination"); browse.clicked.connect(self.choose_destination)
        f.addRow("ISO URL",self.url); f.addRow("Save as",self.destination); f.addRow("",browse); f.addRow("SHA-256",self.sha256); l.addLayout(f)
        self.progress=QProgressBar(); self.status=QLabel("Ready"); l.addWidget(self.progress); l.addWidget(self.status)
        row=QHBoxLayout(); self.start_button=QPushButton("Download"); self.cancel_button=QPushButton("Cancel"); self.cancel_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_download); self.cancel_button.clicked.connect(self.cancel_download)
        row.addWidget(self.start_button); row.addWidget(self.cancel_button); l.addLayout(row)
    def choose_destination(self):
        p,_=QFileDialog.getSaveFileName(self,"Save ISO",str(Path.home()/"Downloads"),"Images (*.iso *.img);;All files (*)")
        if p:self.destination.setText(p)
    def start_download(self):
        u=self.url.text().strip(); d=self.destination.text().strip()
        if not u or not d: QMessageBox.warning(self,"Missing information","Enter a URL and destination."); return
        self.worker=DownloadWorker(u,d,self.sha256.text().strip(),self)
        self.worker.progress.connect(self.on_progress); self.worker.completed.connect(self.on_complete); self.worker.failed.connect(self.on_failed); self.worker.cancelled_signal.connect(self.on_cancelled)
        self.start_button.setEnabled(False); self.cancel_button.setEnabled(True); self.worker.start()
    def cancel_download(self):
        if self.worker:self.worker.cancel(); self.status.setText("Cancelling...")
    def on_progress(self,done,total,speed,eta):
        if total>0:self.progress.setRange(0,100); self.progress.setValue(int(done*100/total))
        else:self.progress.setRange(0,0)
        et=f" - ETA {int(eta)}s" if eta>=0 else ""
        self.status.setText(f"{human_bytes(done)}"+(f" / {human_bytes(total)}" if total else "")+f" - {human_bytes(speed)}/s{et}")
    def finish_ui(self):
        self.start_button.setEnabled(True); self.cancel_button.setEnabled(False); self.progress.setRange(0,100)
    def on_complete(self,path,digest):
        self.finish_ui(); self.progress.setValue(100); self.status.setText(f"Complete: {path}\nSHA-256: {digest}")
    def on_failed(self,message):
        self.finish_ui(); QMessageBox.critical(self,"Download failed",message); self.status.setText("Failed. .part file kept for resume.")
    def on_cancelled(self):
        self.finish_ui(); self.status.setText("Cancelled. .part file kept for resume.")
