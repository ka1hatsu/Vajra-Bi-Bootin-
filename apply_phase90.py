from pathlib import Path

p=Path("vajra/downloader/worker.py")
s=p.read_text()
s=s.replace("progress=Signal(int,int,float,float)","progress=Signal(object,object,float,float)")
if "    def request_stop(self):" not in s:
    anchor="    def run(self):\n"
    if anchor not in s: raise SystemExit("DownloadWorker.run anchor not found")
    s=s.replace(anchor,"    def request_stop(self):\n        self.cancel()\n\n"+anchor,1)
p.write_text(s)

p=Path("vajra/ui/resolved_download_dialog.py")
s=p.read_text()
if "    def closeEvent(self,event):" not in s:
    anchor="    def cancel_or_close(self):\n"
    if anchor not in s: raise SystemExit("cancel_or_close anchor not found")
    method="    def closeEvent(self,event):\n        if self.worker and self.worker.isRunning():\n            self.worker.cancel()\n            if not self.worker.wait(5000):\n                event.ignore()\n                self.set_workflow_state(\"cancelling\",\"Waiting for the active download to stop safely...\")\n                return\n        event.accept()\n\n"
    s=s.replace(anchor,method+anchor,1)
p.write_text(s)
print("Phase 9.0 applied: large-file regression protection and safe worker shutdown.")
