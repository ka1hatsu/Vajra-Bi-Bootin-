from pathlib import Path

p=Path("vajra/ui/resolved_download_dialog.py"); s=p.read_text()
if "verified_image_ready=Signal(str,str)" not in s:
    s=s.replace("    image_ready=Signal(str)\n","    image_ready=Signal(str)\n    verified_image_ready=Signal(str,str)\n",1)
if "self.verified_image_ready.emit(path,digest)" not in s:
    s=s.replace("        self.image_ready.emit(path)\n","        self.verified_image_ready.emit(path,digest)\n        self.image_ready.emit(path)\n",1)
p.write_text(s)

p=Path("vajra/ui/flash_dialog.py"); s=p.read_text()
imp="from vajra.workflow.session import sha256_file\n"
anchor="from vajra.boot.preflight_media import run_media_preflight, MediaPreflightError\n"
if imp not in s:
    if anchor not in s: raise SystemExit("flash import anchor not found")
    s=s.replace(anchor,anchor+imp,1)
s=s.replace('def __init__(self,parent=None,image_path=""):', 'def __init__(self,parent=None,image_path="",verified_sha256=""):',1)
needle='super().__init__(parent); self.operation_log=FlashOperationLog(); self.last_flash_stage="ready";'
if "self.verified_sha256=" not in s:
    if needle not in s: raise SystemExit("flash init anchor not found")
    s=s.replace(needle,needle+' self.verified_sha256=(verified_sha256 or "").lower();',1)
anchor='        helper_path = str(Path(__file__).resolve().parents[1] / "writer" / "helper.py")\n'
guard='        if self.verified_sha256:\n            current_digest=sha256_file(p)\n            if current_digest.lower()!=self.verified_sha256:\n                QMessageBox.critical(self,"Verified image changed","The image file no longer matches the SHA-256 digest verified at download time. Flashing was blocked.")\n                return\n\n'
if guard not in s:
    if anchor not in s: raise SystemExit("helper_path anchor not found")
    s=s.replace(anchor,guard+anchor,1)
p.write_text(s)

p=Path("vajra/workflow/recommendation_download.py"); s=p.read_text()
imp="from vajra.workflow.session import WorkflowSession, sha256_file\n"
if imp not in s:
    s=s.replace("from vajra.workflow.image_handoff import ImageHandoff\n","from vajra.workflow.image_handoff import ImageHandoff\n"+imp,1)
if "self.session = WorkflowSession()" not in s:
    s=s.replace('        self.selected_name = ""\n','        self.selected_name = ""\n        self.session = WorkflowSession()\n',1)
old='    def _ready(self, path):\n        handoff = ImageHandoff.from_download(path, self.selected_name)\n        self.on_image_ready(handoff)\n'
new='    def _ready(self, path):\n        digest=sha256_file(path)\n        self.session.accept_verified_image(path,digest,self.selected_name)\n        handoff = ImageHandoff.from_download(path, self.selected_name)\n        try:\n            handoff.verified_sha256=digest\n        except Exception:\n            pass\n        self.on_image_ready(handoff)\n'
if old not in s: raise SystemExit("recommendation _ready anchor not found")
s=s.replace(old,new,1)
p.write_text(s)
print("Phase 9.5 applied.")
