from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog,QVBoxLayout,QLabel,QComboBox,QProgressBar,QPushButton,QHBoxLayout,QFileDialog,QMessageBox
from vajra.ui.release_resolver_worker import ReleaseResolverWorker
from vajra.downloader.worker import DownloadWorker

class ResolvedDownloadDialog(QDialog):
    image_ready=Signal(str)

    def __init__(self,distro_id,architecture,parent=None):
        super().__init__(parent)
        self.distro_id=distro_id; self.architecture=architecture
        self.images=[]; self.resolver=None; self.worker=None
        self.setWindowTitle("Resolve Compatible ISO"); self.resize(650,320)
        layout=QVBoxLayout(self)
        self.status=QLabel(f"Resolving compatible releases for {architecture}...")
        self.status.setWordWrap(True); layout.addWidget(self.status)
        self.combo=QComboBox(); self.combo.setEnabled(False); layout.addWidget(self.combo)
        self.progress=QProgressBar(); layout.addWidget(self.progress)
        row=QHBoxLayout(); self.download=QPushButton("Download ISO"); self.download.setEnabled(False)
        self.cancel=QPushButton("Cancel"); row.addWidget(self.download); row.addWidget(self.cancel); layout.addLayout(row)
        self.download.clicked.connect(self.start_download); self.cancel.clicked.connect(self.cancel_or_close)
        self.resolve()

    def resolve(self):
        self.progress.setRange(0,0)
        self.resolver=ReleaseResolverWorker(self.distro_id,self.architecture,self)
        self.resolver.completed.connect(self.resolved); self.resolver.failed.connect(self.resolve_failed)
        self.resolver.start()

    def resolved(self,images):
        self.progress.setRange(0,100); self.progress.setValue(0); self.images=list(images); self.combo.clear()
        for image in self.images:
            self.combo.addItem(f"{image.distro} {image.version} | {image.architecture} | {image.filename}")
        if not self.images:
            self.status.setText("No compatible direct ISO was resolved for this distribution and architecture.")
            return
        self.combo.setEnabled(True); self.download.setEnabled(True)
        self.status.setText(f"Found {len(self.images)} compatible image(s). Choose one to download.")

    def resolve_failed(self,message):
        self.progress.setRange(0,100); self.status.setText(f"Resolver failed: {message}")
        QMessageBox.warning(self,"ISO resolution failed",message)

    def selected_image(self):
        i=self.combo.currentIndex()
        return self.images[i] if 0<=i<len(self.images) else None

    def start_download(self):
        image=self.selected_image()
        if not image:return
        destination,_=QFileDialog.getSaveFileName(self,"Save ISO",str(Path.home()/"Downloads"/image.filename),"ISO images (*.iso);;All files (*)")
        if not destination:return
        self.worker=DownloadWorker(image.image_url,destination,image.sha256 or None,self)
        self.worker.progress.connect(self.on_progress); self.worker.completed.connect(self.on_complete)
        self.worker.failed.connect(self.on_failed); self.worker.cancelled_signal.connect(self.on_cancelled)
        self.download.setEnabled(False); self.cancel.setText("Cancel Download"); self.worker.start()

    def on_progress(self,done,total,speed,eta):
        if total:self.progress.setRange(0,100); self.progress.setValue(int(done*100/total))
        else:self.progress.setRange(0,0)
        eta_text=f", ETA {int(eta)}s" if eta>=0 else ""
        self.status.setText(f"{done}/{total or '?'} bytes, {speed/1024/1024:.2f} MiB/s{eta_text}")

    def on_complete(self,path,digest):
        self.progress.setRange(0,100); self.progress.setValue(100)
        self.status.setText(f"Verified ISO ready: {path}"); self.image_ready.emit(path); self.accept()

    def on_failed(self,message):
        self.download.setEnabled(True); self.cancel.setText("Cancel")
        self.status.setText("Download failed; .part file kept for resume.")
        QMessageBox.critical(self,"Download failed",message)

    def on_cancelled(self):
        self.download.setEnabled(True); self.cancel.setText("Cancel")
        self.status.setText("Cancelled; .part file kept for resume.")

    def cancel_or_close(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel(); self.status.setText("Cancelling...")
        else:self.reject()
