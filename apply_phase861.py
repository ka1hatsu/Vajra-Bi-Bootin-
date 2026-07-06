from pathlib import Path

p = Path("vajra/ui/resolved_download_dialog.py")
s = p.read_text()

policy_import = "from vajra.verification.policy import evaluate_download_verification\n"
anchor = "from vajra.downloader.worker import DownloadWorker\n"
if policy_import not in s:
    if anchor not in s:
        raise SystemExit("DownloadWorker import anchor not found")
    s = s.replace(anchor, anchor + policy_import, 1)

old = "    def on_complete(self,path,digest):\n        self.progress.setRange(0,100); self.progress.setValue(100)\n        self.status.setText(f\"Verified ISO ready: {path}\"); self.image_ready.emit(path); self.accept()\n"

new = """    def on_complete(self,path,digest):
        self.progress.setRange(0,100)
        self.progress.setValue(100)

        image = self.selected_image()
        expected = image.sha256 if image else ""
        decision = evaluate_download_verification(expected, digest)

        if not decision.can_flash:
            self.status.setText(
                f"Verification state: {decision.state}\\n{decision.message}\\n\\n"
                f"Downloaded file: {path}\\n"
                f"Calculated SHA-256: {digest}"
            )
            self.download.setEnabled(False)
            self.cancel.setText("Close")
            QMessageBox.critical(self, "Image verification blocked", decision.message)
            return

        self.status.setText(
            f"Verification state: verified\\n"
            f"{decision.message}\\n\\n"
            f"Image: {path}\\n"
            f"SHA-256: {digest}"
        )
        self.cancel.setText("Close")
        self.image_ready.emit(path)
        self.accept()
"""

if old not in s:
    raise SystemExit("on_complete anchor not found; current dialog differs from inspected version")
s = s.replace(old, new, 1)
p.write_text(s)
print("Phase 8.6.1 applied: verified-download gate wired into ISO-to-flash handoff.")
