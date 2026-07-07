from pathlib import Path

p=Path("vajra/writer/helper_client.py"); s=p.read_text()
if "cancelled=Signal()" not in s:
    s=s.replace("progress=Signal(int); stage=Signal(str); completed=Signal(); failed=Signal(str)",
                "progress=Signal(int); stage=Signal(str); completed=Signal(); failed=Signal(str); cancelled=Signal()")
if "self.cancel_requested=False" not in s:
    s=s.replace('super().__init__(parent); self.buffer=""; self.reported_error=False',
                'super().__init__(parent); self.buffer=""; self.reported_error=False; self.cancel_requested=False; self.terminal_event=False')
s=s.replace("    def cancel(self):\n        if self.process.state()!=QProcess.NotRunning: self.process.terminate()",
'''    def cancel(self):
        self.cancel_requested=True
        if self.process.state()!=QProcess.NotRunning:
            self.process.terminate()

    def force_kill(self):
        if self.process.state()!=QProcess.NotRunning:
            self.process.kill()

    def is_running(self):
        return self.process.state()!=QProcess.NotRunning
''')
s=s.replace('elif kind=="error":self.reported_error=True; self.failed.emit(str(e.get("message","Helper failed.")))',
            'elif kind=="error":self.reported_error=True; self.terminal_event=True; self.failed.emit(str(e.get("message","Helper failed.")))')
s=s.replace('elif kind=="complete":self.completed.emit()',
            'elif kind=="complete":self.terminal_event=True; self.completed.emit()')
old='''    def finished(self,code,status):
        if code and not self.reported_error:
            err=bytes(self.process.readAllStandardError()).decode(errors="replace").strip()
            self.failed.emit(err or ("Authorization cancelled or denied." if code==126 else f"Helper exited with code {code}."))
'''
new='''    def finished(self,code,status):
        if self.cancel_requested:
            self.terminal_event=True
            self.cancelled.emit()
            return
        if code and not self.reported_error:
            self.terminal_event=True
            err=bytes(self.process.readAllStandardError()).decode(errors="replace").strip()
            self.failed.emit(err or ("Authorization cancelled or denied." if code==126 else f"Helper exited with code {code}."))
'''
if old in s: s=s.replace(old,new,1)
p.write_text(s)

p=Path("vajra/ui/flash_dialog.py"); s=p.read_text()
imp="from vajra.writer.operation_log import FlashOperationLog\n"
anchor="from vajra.writer.privilege import PrivilegeError\n"
if imp not in s: s=s.replace(anchor,anchor+imp,1)
if "self.operation_log=FlashOperationLog()" not in s:
    s=s.replace("super().__init__(parent); self.setWindowTitle", "super().__init__(parent); self.operation_log=FlashOperationLog(); self.setWindowTitle",1)
needle="        self.worker.failed.connect(self.failed)\n"
if "self.worker.cancelled.connect(self.flash_cancelled)" not in s:
    s=s.replace(needle,needle+"        self.worker.cancelled.connect(self.flash_cancelled)\n",1)
if 'self.operation_log.append("started"' not in s:
    s=s.replace("        self.worker.start()\n",
'''        self.operation_log.append("started",image=p,device=validated_device["path"])
        self.worker.start()
''',1)
s=s.replace('    def stop(self):\n        if hasattr(self,"worker"):self.worker.cancel(); self.stage.setText("Cancellation requested...")',
'''    def stop(self):
        if hasattr(self,"worker") and self.worker.is_running():
            self.cancel.setEnabled(False)
            self.worker.cancel()
            self.stage.setText("Cancellation requested; waiting for helper shutdown...")
''')
old='    def flash_complete(self): self.write.setEnabled(True); self.cancel.setEnabled(False); self.stage.setText("Write and verification complete."); QMessageBox.information(self,"Complete","Image written and verified successfully.")\n'
new='''    def flash_complete(self):
        self.operation_log.append("completed")
        self.write.setEnabled(True); self.cancel.setEnabled(False)
        self.stage.setText("Write and verification complete.")
        QMessageBox.information(self,"Complete","Image written and verified successfully.")

    def flash_cancelled(self):
        self.operation_log.append("cancelled")
        self.write.setEnabled(True); self.cancel.setEnabled(False)
        self.stage.setText("Operation cancelled. Reconnect or reformat the USB before reuse if writing was interrupted.")
        QMessageBox.information(self,"Cancelled","The flash operation was cancelled. The USB may contain incomplete data.")
'''
if old in s: s=s.replace(old,new,1)
old='    def failed(self,msg): self.write.setEnabled(True); self.cancel.setEnabled(False); self.stage.setText("Stopped"); QMessageBox.critical(self,"Write failed",msg)\n'
new='''    def failed(self,msg):
        self.operation_log.append("failed",message=str(msg))
        self.write.setEnabled(True); self.cancel.setEnabled(False)
        self.stage.setText("Stopped")
        QMessageBox.critical(self,"Write failed",msg)
'''
if old in s: s=s.replace(old,new,1)
p.write_text(s)
print("Phase 9.1 applied.")
