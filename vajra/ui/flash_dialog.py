from pathlib import Path
from PySide6.QtCore import QThread,Signal
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,QFileDialog,QComboBox,QProgressBar,QMessageBox
from vajra.writer.devices import eligible_usb_devices,format_size,DeviceDetectionError
from vajra.writer.flash import write_image,FlashCancelled
from vajra.writer.verify import verify_written_image
from vajra.writer.preflight import revalidate_target, ensure_image_fits, PreflightError
from vajra.writer.session import TargetIdentity
from vajra.writer.helper_client import HelperClient
from vajra.writer.privilege import PrivilegeError

class FlashWorker(QThread):
    progress=Signal(int); stage=Signal(str); completed=Signal(); failed=Signal(str)
    def __init__(self,image,device): super().__init__(); self.image=image; self.device=device; self.cancelled=False
    def cancel(self): self.cancelled=True
    def run(self):
        try:
            self.stage.emit("Writing image...")
            write_image(self.image,self.device,lambda d,t:self.progress.emit(int(d*80/t)) if t else None,lambda:self.cancelled)
            if self.cancelled: raise FlashCancelled("Writing cancelled.")
            self.stage.emit("Verifying written data...")
            ok = verify_written_image(self.image,self.device,progress_callback=lambda d, t: self.progress.emit(80 + int(d * 20 / t)) if t else None,cancel_check=lambda: self.cancelled,)
            if not ok: raise RuntimeError("Post-write verification failed.")
            self.progress.emit(100); self.completed.emit()
        except PermissionError: self.failed.emit("Permission denied. Production builds should use a narrowly scoped privileged helper.")
        except Exception as e: self.failed.emit(str(e))

class FlashDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle("Write Image to USB"); self.resize(720,440); self.devices=[]
        l=QVBoxLayout(self); title=QLabel("Write ISO / IMG to USB"); title.setStyleSheet("font-size:24px;font-weight:700;"); l.addWidget(title)
        note=QLabel("Writing destroys existing data on the selected USB drive. Only devices passing Vajra eligibility checks are listed."); note.setWordWrap(True); l.addWidget(note)
        self.image=QLineEdit(); self.image.setPlaceholderText("Choose an .iso or .img file"); choose=QPushButton("Choose Image"); choose.clicked.connect(self.choose_image)
        r=QHBoxLayout(); r.addWidget(self.image); r.addWidget(choose); l.addLayout(r)
        self.combo=QComboBox(); l.addWidget(self.combo); refresh=QPushButton("Refresh Eligible USB Devices"); refresh.clicked.connect(self.refresh); l.addWidget(refresh)
        self.confirm=QLineEdit(); self.confirm.setPlaceholderText("Type ERASE to enable writing"); l.addWidget(self.confirm)
        self.stage=QLabel("Ready"); l.addWidget(self.stage); self.progress=QProgressBar(); l.addWidget(self.progress)
        r=QHBoxLayout(); self.write=QPushButton("Write and Verify"); self.cancel=QPushButton("Cancel"); self.cancel.setEnabled(False)
        self.write.clicked.connect(self.start); self.cancel.clicked.connect(self.stop); r.addWidget(self.write); r.addWidget(self.cancel); l.addLayout(r); self.refresh()
    def choose_image(self):
        p,_=QFileDialog.getOpenFileName(self,"Choose Disk Image",str(Path.home()),"Disk Images (*.iso *.img);;All Files (*)")
        if p:self.image.setText(p)
    def refresh(self):
        self.combo.clear()
        try:self.devices=eligible_usb_devices()
        except DeviceDetectionError as e: QMessageBox.critical(self,"Detection failed",str(e)); self.devices=[]; return
        for d in self.devices:self.combo.addItem(f'{d["path"]} - {d["vendor"]} {d["model"]} - {format_size(d["size_bytes"])}')
        if not self.devices:self.combo.addItem("No eligible removable USB device detected")
    def start(self):
        p=self.image.text().strip()
        if not Path(p).is_file(): QMessageBox.warning(self,"Invalid image","Choose an existing ISO or IMG file."); return
        if not self.devices: QMessageBox.warning(self,"No USB","No eligible USB device is selected."); return
        if self.confirm.text().strip()!="ERASE": QMessageBox.warning(self,"Confirmation required","Type ERASE exactly."); return
        d=self.devices[self.combo.currentIndex()]

        # Phase 6: freeze the identity of the device selected by the user.
        target_identity = TargetIdentity.from_device(d)

        try:
            ensure_image_fits(p, d)
        except PreflightError as e:
            QMessageBox.critical(self, "Preflight failed", str(e))
            return
        ans=QMessageBox.warning(self,"Final confirmation",f'ALL DATA WILL BE ERASED on:\n\nPath: {d["path"]}\nModel: {d["vendor"]} {d["model"]}\nSize: {format_size(d["size_bytes"])}\n\nImage: {p}',QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if ans != QMessageBox.Yes:
            return

        # Phase 6: rediscover and verify the target immediately before writing.
        try:
            validated_device = revalidate_target(
                target_identity.path,
                expected_serial=target_identity.serial,
                expected_size=target_identity.size_bytes,
            )
            ensure_image_fits(p, validated_device)

        except PreflightError as e:
            QMessageBox.critical(
                self,
                "Safety check failed",
                "Writing was blocked because the target device changed "
                "or no longer passes safety checks.\n\n" + str(e),
            )
            self.refresh()
            return

        helper_path = str(Path(__file__).resolve().parents[1] / "writer" / "helper.py")
        try:
            self.worker = HelperClient(helper_path, p, target_identity, parent=self)
        except PrivilegeError as e:
            QMessageBox.critical(self, "Privilege setup failed", str(e))
            return
        self.worker.progress.connect(self.progress.setValue)
        self.worker.stage.connect(self.stage.setText)
        self.worker.completed.connect(self.flash_complete)
        self.worker.failed.connect(self.failed)
        self.write.setEnabled(False)
        self.cancel.setEnabled(True)
        self.worker.start()
    def stop(self):
        if hasattr(self,"worker"):self.worker.cancel(); self.stage.setText("Cancellation requested...")
    def flash_complete(self): self.write.setEnabled(True); self.cancel.setEnabled(False); self.stage.setText("Write and verification complete."); QMessageBox.information(self,"Complete","Image written and verified successfully.")
    def failed(self,msg): self.write.setEnabled(True); self.cancel.setEnabled(False); self.stage.setText("Stopped"); QMessageBox.critical(self,"Write failed",msg)
