from pathlib import Path
p=Path("vajra/ui/flash_dialog.py")
s=p.read_text()
guard_import="from vajra.workflow.end_to_end_guard import require_flash_ready, WorkflowGuardError\n"
if guard_import not in s:
    anchor="from vajra.ui.dialog_theme import DIALOG_STYLE\n"
    if anchor not in s: raise SystemExit("dialog theme import anchor not found")
    s=s.replace(anchor,anchor+guard_import,1)
marker="    def choose_image(self):\n"
method="    def validate_verified_handoff(self):\n        if not self.verified_sha256:\n            return None\n        return require_flash_ready(\n            self.image.text().strip(),\n            self.verified_sha256,\n        )\n\n"
if "def validate_verified_handoff(self):" not in s:
    if marker not in s: raise SystemExit("choose_image method anchor not found")
    s=s.replace(marker,method+marker,1)
p.write_text(s)
print("Phase 9.7 applied.")
