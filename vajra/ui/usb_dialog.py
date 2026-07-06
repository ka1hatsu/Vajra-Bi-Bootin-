from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QMessageBox
)
from vajra.writer.devices import list_storage_devices, format_size, DeviceDetectionError


class UsbDeviceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("USB Safety Check")
        self.resize(760, 520)

        layout = QVBoxLayout(self)
        title = QLabel("Removable USB Detection")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        layout.addWidget(title)

        note = QLabel(
            "Phase 4 is detection-only: Vajra will not write, format, erase, mount, or unmount any drive. "
            "System disks and read-only devices are blocked from eligibility."
        )
        note.setWordWrap(True)
        layout.addWidget(note)

        self.list = QListWidget()
        self.list.currentItemChanged.connect(self.update_details)
        layout.addWidget(self.list)

        self.details = QLabel("Select a device to inspect its safety status.")
        self.details.setWordWrap(True)
        layout.addWidget(self.details)

        row = QHBoxLayout()
        refresh = QPushButton("Refresh Devices")
        refresh.clicked.connect(self.refresh)
        self.select_button = QPushButton("Validate Selection")
        self.select_button.clicked.connect(self.validate_selection)
        row.addWidget(refresh)
        row.addStretch()
        row.addWidget(self.select_button)
        layout.addLayout(row)

        self.refresh()

    def refresh(self):
        self.list.clear()
        try:
            devices = list_storage_devices()
        except DeviceDetectionError as exc:
            QMessageBox.critical(self, "Detection failed", str(exc))
            return

        for device in devices:
            state = "ELIGIBLE USB" if device["eligible"] else "BLOCKED"
            label = (
                f'{device["path"]} — {device["vendor"]} {device["model"]} '
                f'— {format_size(device["size_bytes"])} — {state}'
            )
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, device)
            self.list.addItem(item)

        if self.list.count():
            self.list.setCurrentRow(0)
        else:
            self.details.setText("No disk devices were detected.")

    def selected(self):
        item = self.list.currentItem()
        return item.data(Qt.UserRole) if item else None

    def update_details(self):
        device = self.selected()
        if not device:
            return
        reasons = []
        if device["system_disk"]:
            reasons.append("Blocked: detected as the system/root disk.")
        if device["read_only"]:
            reasons.append("Blocked: device is read-only.")
        if not device["removable"]:
            reasons.append("Blocked: device is not identified as removable or USB transport.")
        if device["eligible"]:
            reasons.append("Eligible for a future write-confirmation stage. No write occurs in Phase 4.")

        mounts = ", ".join(device["mountpoints"]) or "None"
        self.details.setText(
            f'Path: {device["path"]}\n'
            f'Model: {device["vendor"]} {device["model"]}\n'
            f'Size: {format_size(device["size_bytes"])}\n'
            f'Transport: {device["transport"]}\n'
            f'Mounted at: {mounts}\n\n' + "\n".join(reasons)
        )

    def validate_selection(self):
        device = self.selected()
        if not device:
            QMessageBox.warning(self, "No selection", "Select a device first.")
            return
        if not device["eligible"]:
            QMessageBox.critical(
                self, "Device blocked",
                "Vajra will not allow this device into the future writing workflow."
            )
            return
        QMessageBox.information(
            self, "Safety check passed",
            f'{device["path"]} passed Phase 4 eligibility checks.\n\n'
            "No data has been written or erased."
        )
