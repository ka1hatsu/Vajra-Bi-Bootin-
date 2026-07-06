from pathlib import Path
p=Path("vajra/ui/resolved_download_dialog.py")
s=p.read_text()

# Add explicit workflow state helper after selected_image.
anchor = """    def selected_image(self):
        i=self.combo.currentIndex()
        return self.images[i] if 0<=i<len(self.images) else None
"""
helper = """    def selected_image(self):
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
"""
if 'def set_workflow_state' not in s:
    if anchor not in s: raise SystemExit('selected_image anchor not found')
    s=s.replace(anchor,helper,1)

# Initialize state.
needle="        self.images=[]; self.resolver=None; self.worker=None"
repl="        self.images=[]; self.resolver=None; self.worker=None; self.workflow_state=\"resolving\""
if needle in s: s=s.replace(needle,repl,1)

# Download start state.
needle='        self.download.setEnabled(False); self.cancel.setText("Cancel Download"); self.worker.start()'
repl='        self.set_workflow_state("downloading","Downloading ISO...")\n        self.worker.start()'
if needle not in s: raise SystemExit('download start anchor not found')
s=s.replace(needle,repl,1)

# Mark verifying as soon as worker completion callback enters.
needle="    def on_complete(self,path,digest):\n        self.progress.setRange(0,100)"
repl='    def on_complete(self,path,digest):\n        self.set_workflow_state("verifying","Download complete. Verifying SHA-256...")\n        self.progress.setRange(0,100)'
if needle not in s: raise SystemExit('on_complete anchor not found')
s=s.replace(needle,repl,1)

# Verified state before handoff.
needle='        self.cancel.setText("Close")\n        self.image_ready.emit(path)'
repl='        self.set_workflow_state("verified", self.status.text())\n        self.image_ready.emit(path)'
if needle not in s: raise SystemExit('verified handoff anchor not found')
s=s.replace(needle,repl,1)

# Retry states.
old='        self.download.setEnabled(True); self.cancel.setText("Cancel")\n        self.status.setText("Download failed; .part file kept for resume.")'
new='        self.set_workflow_state("failed","Download failed; .part file kept for resume. Retry will resume when supported.")'
if old in s: s=s.replace(old,new,1)
old='        self.download.setEnabled(True); self.cancel.setText("Cancel")\n        self.status.setText("Cancelled; .part file kept for resume.")'
new='        self.set_workflow_state("cancelled","Cancelled; .part file kept for resume. You can retry.")'
if old in s: s=s.replace(old,new,1)

# Prevent duplicate starts.
needle="    def start_download(self):\n        image=self.selected_image()"
repl='    def start_download(self):\n        if self.worker and self.worker.isRunning():\n            return\n        image=self.selected_image()'
if needle not in s: raise SystemExit('start_download anchor not found')
s=s.replace(needle,repl,1)

# Cancellation UX.
old='            self.worker.cancel(); self.status.setText("Cancelling...")'
new='            self.set_workflow_state("cancelling","Cancelling download safely...")\n            self.worker.cancel()'
if old in s: s=s.replace(old,new,1)

p.write_text(s)
print("Phase 8.7 applied: explicit workflow states, retry UX and duplicate-start protection installed.")
