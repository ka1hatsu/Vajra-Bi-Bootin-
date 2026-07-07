import webbrowser
from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog,QVBoxLayout,QLabel,QComboBox,QProgressBar,QPushButton,QHBoxLayout,QFileDialog,QMessageBox
from vajra.ui.release_resolver_worker import ReleaseResolverWorker
from vajra.sources.registry import get_official_fallback
from vajra.downloader.worker import DownloadWorker
from vajra.verification.policy import evaluate_download_verification
from vajra.downloads.session import DownloadSession

from vajra.ui.dialog_theme import DIALOG_STYLE

class ResolvedDownloadDialog(QDialog):
    image_ready=Signal(str)
    verified_image_ready=Signal(str,str)

    def __init__(self,distro_id,architecture,parent=None,resume_destination=None):
        super().__init__(parent)
        self.setStyleSheet(DIALOG_STYLE)
        self.distro_id=distro_id; self.architecture=architecture
        self.resume_destination=resume_destination
        self.images=[]; self.resolver=None; self.worker=None; self.workflow_state="resolving"; self.download_session=None
        self.setWindowTitle("Resolve Compatible ISO"); self.resize(650,320)
        layout=QVBoxLayout(self)
        self.status=QLabel(f"Resolving compatible releases for {architecture}...")
        self.status.setWordWrap(True); layout.addWidget(self.status)
        self.combo=QComboBox(); self.combo.setEnabled(False); layout.addWidget(self.combo)
        self.progress=QProgressBar(); layout.addWidget(self.progress)
        row=QHBoxLayout(); self.download=QPushButton("Download ISO"); self.download.setObjectName("primaryAction"); self.download.setEnabled(False)
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
        self.progress.setRange(0,100)
        self.progress.setValue(0)
        fallback=get_official_fallback(self.distro_id)
        self.status.setText('No compatible direct ISO was resolved automatically. You can use the official download page instead.\n\n'+message)
        if fallback:
            self.download.setText('Open Official Download Page')
            self.download.setEnabled(True)
            try:
                self.download.clicked.disconnect()
            except Exception:
                pass
            self.download.clicked.connect(lambda: webbrowser.open(fallback))
        else:
            self.download.setEnabled(False)

    def selected_image(self):
        i=self.combo.currentIndex()
        return self.images[i] if 0<=i<len(self.images) else None

    def set_workflow_state(self,state,message):
        self.workflow_state=state
        self.status.setText(message)

        busy=state in ("resolving","downloading","verifying","cancelling")
        self.combo.setEnabled(bool(self.images) and not busy)

        if state=="ready":
            self.download.setText("Download ISO")
            self.download.setEnabled(bool(self.images))
            self.cancel.setText("Close")
        elif state=="downloading":
            self.download.setText("Downloading...")
            self.download.setEnabled(False)
            self.cancel.setText("Cancel Download")
        elif state=="verifying":
            self.download.setText("Verifying...")
            self.download.setEnabled(False)
            self.cancel.setText("Cancel")
        elif state=="verified":
            self.download.setText("Verified")
            self.download.setEnabled(False)
            self.cancel.setText("Close")
        elif state in ("failed","cancelled"):
            self.download.setText("Retry Download")
            self.download.setEnabled(bool(self.images))
            self.cancel.setText("Close")
        elif state=="cancelling":
            self.download.setEnabled(False)
            self.cancel.setEnabled(False)

    def start_download(self):
        if self.worker and self.worker.isRunning():
            return
        image=self.selected_image()
        if not image:return
        if self.resume_destination:
            destination=self.resume_destination
            self.resume_destination=None
        else:
            destination,_=QFileDialog.getSaveFileName(self,"Save ISO",str(Path.home()/"Downloads"/image.filename),"ISO images (*.iso);;All files (*)")
            if not destination:return
        self.download_session=DownloadSession(self.distro_id,image,destination)
        self.worker=DownloadWorker(image.image_url,destination,image.sha256 or None,self)
        self.worker.progress.connect(self.on_progress); self.worker.completed.connect(self.on_complete)
        self.worker.failed.connect(self.on_failed); self.worker.cancelled_signal.connect(self.on_cancelled)
        self.set_workflow_state("downloading","Downloading ISO...")
        self.worker.start()

    def on_progress(self,done,total,speed,eta):
        if self.download_session:
            self.download_session.progress(done,total)
        if total:self.progress.setRange(0,100); self.progress.setValue(int(done*100/total))
        else:self.progress.setRange(0,0)
        eta_text=f", ETA {int(eta)}s" if eta>=0 else ""
        self.status.setText(f"{done}/{total or '?'} bytes, {speed/1024/1024:.2f} MiB/s{eta_text}")

    def on_complete(self,path,digest):
        self.set_workflow_state("verifying","Download complete. Verifying SHA-256...")
        self.progress.setRange(0,100)
        self.progress.setValue(100)

        image = self.selected_image()
        expected = image.sha256 if image else ""
        decision = evaluate_download_verification(expected, digest)

        if not decision.can_flash:
            self.status.setText(
                f"Verification state: {decision.state}\n{decision.message}\n\n"
                f"Downloaded file: {path}\n"
                f"Calculated SHA-256: {digest}"
            )
            self.download.setEnabled(False)
            self.cancel.setText("Close")
            QMessageBox.critical(self, "Image verification blocked", decision.message)
            return

        self.status.setText(
            f"Verification state: verified\n"
            f"{decision.message}\n\n"
            f"Image: {path}\n"
            f"SHA-256: {digest}"
        )
        self.set_workflow_state("verified", self.status.text())
        if self.download_session:
            self.download_session.completed(path,digest,True)
        self.verified_image_ready.emit(path,digest)
        self.image_ready.emit(path)
        self.accept()

    def on_failed(self,message):
        if self.download_session:
            self.download_session.failed()
        self.set_workflow_state("failed","Download failed; .part file kept for resume. Retry will resume when supported.")
        QMessageBox.critical(self,"Download failed",message)

    def on_cancelled(self):
        if self.download_session:
            self.download_session.cancelled()
        self.set_workflow_state("cancelled","Cancelled; .part file kept for resume. You can retry.")

    def closeEvent(self,event):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            if not self.worker.wait(5000):
                event.ignore()
                self.set_workflow_state("cancelling","Waiting for the active download to stop safely...")
                return
        event.accept()

    def cancel_or_close(self):
        if self.worker and self.worker.isRunning():
            self.set_workflow_state("cancelling","Cancelling download safely...")
            self.worker.cancel()
        else:self.reject()
