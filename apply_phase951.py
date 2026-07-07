from pathlib import Path

p=Path("vajra/workflow/image_handoff.py")
s=p.read_text()
s=s.replace('    distro_name: str = ""\n','    distro_name: str = ""\n    verified_sha256: str = ""\n',1)
s=s.replace('def from_download(cls, path, distro_name=""):', 'def from_download(cls, path, distro_name="", verified_sha256=""):',1)
s=s.replace('return cls(str(p), "download", distro_name)', 'return cls(str(p), "download", distro_name, (verified_sha256 or "").lower())',1)
p.write_text(s)

p=Path("vajra/workflow/recommendation_download.py")
s=p.read_text()
old='        handoff = ImageHandoff.from_download(path, self.selected_name)\n        try:\n            handoff.verified_sha256=digest\n        except Exception:\n            pass\n        self.on_image_ready(handoff)\n'
new='        handoff = ImageHandoff.from_download(path, self.selected_name, verified_sha256=digest)\n        self.on_image_ready(handoff)\n'
if old not in s: raise SystemExit("recommendation handoff anchor not found")
s=s.replace(old,new,1)
p.write_text(s)

p=Path("vajra/ui/main_window.py")
s=p.read_text()
old='        dialog = FlashDialog(\n            parent=self,\n            image_path=handoff.path,\n        )\n'
new='        dialog = FlashDialog(\n            parent=self,\n            image_path=handoff.path,\n            verified_sha256=handoff.verified_sha256,\n        )\n'
if old not in s: raise SystemExit("downloaded handoff anchor not found")
s=s.replace(old,new,1)

old='        dialog.image_ready.connect(\n            lambda path: FlashDialog(parent=self, image_path=path).exec()\n        )\n'
new='        dialog.verified_image_ready.connect(\n            lambda path, digest: FlashDialog(parent=self, image_path=path, verified_sha256=digest).exec()\n        )\n'
if old not in s: raise SystemExit("recommended resolver anchor not found")
s=s.replace(old,new,1)

old='        dialog.image_ready.connect(self.open_verified_history_image)\n'
new='        dialog.verified_image_ready.connect(self.open_verified_history_image)\n'
if old not in s: raise SystemExit("resume history anchor not found")
s=s.replace(old,new,1)

old='    def open_verified_history_image(self, path):\n        dialog = FlashDialog(parent=self)\n\n        dialog.image.setText(path)\n'
new='    def open_verified_history_image(self, path, digest=""):\n        dialog = FlashDialog(parent=self, image_path=path, verified_sha256=digest)\n'
if old not in s: raise SystemExit("history method anchor not found")
s=s.replace(old,new,1)
p.write_text(s)

p=Path("vajra/ui/catalog_download_dialog.py")
s=p.read_text()
if "verified_image_ready" not in s:
    if "image_ready = Signal(str)" in s:
        s=s.replace("image_ready = Signal(str)","image_ready = Signal(str)\n    verified_image_ready = Signal(str, str)",1)
    elif "image_ready=Signal(str)" in s:
        s=s.replace("image_ready=Signal(str)","image_ready=Signal(str)\n    verified_image_ready=Signal(str,str)",1)
    else:
        raise SystemExit("catalog signal anchor not found")
old='        self.image_ready.emit(path)\n        QMessageBox.information(\n'
new='        self.verified_image_ready.emit(path, digest)\n        self.image_ready.emit(path)\n        QMessageBox.information(\n'
if old not in s: raise SystemExit("catalog emit anchor not found")
s=s.replace(old,new,1)
p.write_text(s)

print("Phase 9.5.1 applied.")
