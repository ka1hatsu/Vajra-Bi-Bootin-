from pathlib import Path

p=Path("vajra/ui/flash_dialog.py")
s=p.read_text()

anchor="from vajra.writer.operation_log import FlashOperationLog\n"
imp="from vajra.writer.recovery import assess_interruption\n"
if imp not in s:
    if anchor not in s: raise SystemExit("operation log import anchor not found")
    s=s.replace(anchor,anchor+imp,1)

if "self.last_flash_stage=" not in s:
    needle="super().__init__(parent); self.operation_log=FlashOperationLog();"
    if needle not in s: raise SystemExit("FlashDialog init anchor not found")
    s=s.replace(needle,needle+' self.last_flash_stage="ready";',1)

old="self.worker.stage.connect(self.stage.setText)"
if old in s:
    s=s.replace(old,"self.worker.stage.connect(self.on_flash_stage)",1)

if "    def on_flash_stage(self,message):" not in s:
    anchor="    def stop(self):\n"
    if anchor not in s: raise SystemExit("FlashDialog stop anchor not found")
    methods="    def on_flash_stage(self,message):\n        self.last_flash_stage=str(message)\n        self.stage.setText(str(message))\n        self.operation_log.append(\"stage\",stage=self.last_flash_stage)\n\n    def refresh_device_state(self):\n        self.refresh()\n        self.stage.setText(\"Device state refreshed.\")\n\n"
    s=s.replace(anchor,methods+anchor,1)

old='        self.stage.setText("Operation cancelled. Reconnect or reformat the USB before reuse if writing was interrupted.")\n        QMessageBox.information(self,"Cancelled","The flash operation was cancelled. The USB may contain incomplete data.")\n'
new='        assessment=assess_interruption(self.last_flash_stage)\n        self.operation_log.append("recovery_assessment",state=assessment.state,stage=self.last_flash_stage)\n        self.stage.setText(assessment.message)\n        QMessageBox.information(self,"Operation cancelled",f"Recovery state: {assessment.state}\\n\\n{assessment.message}")\n        self.refresh_device_state()\n'
if old in s: s=s.replace(old,new,1)

old='        self.operation_log.append("failed",message=str(msg))\n        self.write.setEnabled(True); self.cancel.setEnabled(False)\n        self.stage.setText("Stopped")\n        QMessageBox.critical(self,"Write failed",msg)\n'
new='        assessment=assess_interruption(self.last_flash_stage)\n        self.operation_log.append("failed",message=str(msg),stage=self.last_flash_stage,recovery_state=assessment.state)\n        self.write.setEnabled(True); self.cancel.setEnabled(False)\n        self.stage.setText(assessment.message)\n        QMessageBox.critical(self,"Write failed",f"{msg}\\n\\nRecovery state: {assessment.state}\\n{assessment.message}")\n        self.refresh_device_state()\n'
if old in s: s=s.replace(old,new,1)

p.write_text(s)
print("Phase 9.3 applied.")
