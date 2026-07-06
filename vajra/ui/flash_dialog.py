from pathlib import Path
from PySide6.QtCore import QThread,Signal
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,QFileDialog,QComboBox,QProgressBar,QMessageBox,QFormLayout
from vajra.writer.devices import eligible_usb_devices,format_size,DeviceDetectionError
from vajra.writer.flash import write_image,FlashCancelled
from vajra.writer.verify import verify_written_image
from vajra.writer.preflight import revalidate_target, ensure_image_fits, PreflightError
from vajra.writer.session import TargetIdentity
from vajra.writer.helper_client import HelperClient
from vajra.writer.privilege import PrivilegeError
from vajra.boot.analyzer import analyze_image
from vajra.boot.compatibility import evaluate
from vajra.boot.config import BootConfig, PARTITION_SCHEMES, TARGET_SYSTEMS, FILE_SYSTEMS, IMAGE_OPTIONS
from vajra.boot.planner import build_plan, PreparationPlanError
from vajra.boot.backend import check_backend_available, BackendUnavailable

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
        form=QFormLayout()
        self.image_option=QComboBox(); self.image_option.addItems(IMAGE_OPTIONS); form.addRow("Image option",self.image_option)
        self.partition_scheme=QComboBox(); self.partition_scheme.addItems(PARTITION_SCHEMES); form.addRow("Partition scheme",self.partition_scheme)
        self.target_system=QComboBox(); self.target_system.addItems(TARGET_SYSTEMS); form.addRow("Target system",self.target_system)
        self.file_system=QComboBox(); self.file_system.addItems(FILE_SYSTEMS); form.addRow("File system",self.file_system)
        self.volume_label=QLineEdit(); self.volume_label.setPlaceholderText("Optional volume label"); form.addRow("Volume label",self.volume_label)
        l.addLayout(form)
        self.analysis_label=QLabel("Choose an image to analyze boot compatibility."); self.analysis_label.setWordWrap(True); l.addWidget(self.analysis_label)
        self.compatibility_label=QLabel("Compatibility: waiting for image selection")
        self.compatibility_label.setWordWrap(True)
        l.addWidget(self.compatibility_label)
        self.current_analysis=None
        for control in (self.partition_scheme,self.target_system,self.file_system):
            control.currentTextChanged.connect(self.update_compatibility)
        self.confirm=QLineEdit(); self.confirm.setPlaceholderText("Type ERASE to enable writing"); l.addWidget(self.confirm)
        self.stage=QLabel("Ready"); l.addWidget(self.stage); self.progress=QProgressBar(); l.addWidget(self.progress)
        r=QHBoxLayout(); self.write=QPushButton("Write and Verify"); self.cancel=QPushButton("Cancel"); self.cancel.setEnabled(False)
        self.write.clicked.connect(self.start); self.cancel.clicked.connect(self.stop); r.addWidget(self.write); r.addWidget(self.cancel); l.addLayout(r); self.refresh()
    def choose_image(self):
        p,_=QFileDialog.getOpenFileName(self,"Choose Disk Image",str(Path.home()),"Disk Images (*.iso *.img);;All Files (*)")
        if p:
            self.image.setText(p)
            try:
                a=analyze_image(p)
                self.current_analysis = a
                hints=[]
                if a.uefi_hint: hints.append("UEFI hint")
                if a.bios_hint: hints.append("BIOS/bootable hint")
                self.analysis_label.setText(f"{a.image_type} • {', '.join(hints) if hints else 'no boot-mode hint detected'}. {a.note}")
                self.update_compatibility()
            except Exception as e:
                self.analysis_label.setText(f"Analysis unavailable: {e}")
    def update_compatibility(self):
        a=getattr(self,"current_analysis",None)
        if not a:
            return
        r=evaluate(
            a.image_type,
            self.partition_scheme.currentText(),
            self.target_system.currentText(),
            self.file_system.currentText(),
            a.uefi_hint,
            a.bios_hint,
        )
        prefix={"ok":"Compatible","warning":"Warning","error":"Blocked"}.get(r.severity,"Compatibility")
        self.compatibility_label.setText(
            f"{prefix}: {r.message}\n"
            f"Suggested: {r.recommended_scheme} / {r.recommended_target} / {r.recommended_filesystem}"
        )

    def refresh(self):
        self.combo.clear()
        try:self.devices=eligible_usb_devices()
        except DeviceDetectionError as e: QMessageBox.critical(self,"Detection failed",str(e)); self.devices=[]; return
        for d in self.devices:self.combo.addItem(f'{d["path"]} - {d["vendor"]} {d["model"]} - {format_size(d["size_bytes"])}')
        if not self.devices:self.combo.addItem("No eligible removable USB device detected")
    def start(self):
        p=self.image.text().strip()
        a=getattr(self,"current_analysis",None)
        if a:
            compatibility=evaluate(
                a.image_type,
                self.partition_scheme.currentText(),
                self.target_system.currentText(),
                self.file_system.currentText(),
                a.uefi_hint,
                a.bios_hint,
            )
            if not compatibility.compatible:
                QMessageBox.warning(self,"Incompatible boot configuration",compatibility.message)
                return

        config=BootConfig(self.partition_scheme.currentText(),self.target_system.currentText(),self.file_system.currentText(),self.image_option.currentText(),self.volume_label.text().strip())
        try:
            config.validate()

            if a:
                plan = build_plan(config, a)
                check_backend_available(plan)

        except (
            ValueError,
            PreparationPlanError,
            BackendUnavailable,
        ) as e:
            QMessageBox.warning(
                self,
                "Unsupported configuration",
                str(e),
            )
            return

        if a and plan.requires_preparation:
            answer = QMessageBox.warning(
                self,
                "Prepared-media operation",
                plan.summary
                + "\n\nThis operation will erase and repartition the selected USB. "
                "The ERASE confirmation and final identity checks still apply.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if answer != QMessageBox.Yes:
                return

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
            self.worker = HelperClient(
                helper_path, p, target_identity,
                parent=self,
                plan=plan if a else None,
            )
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
