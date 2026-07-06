from pathlib import Path

p=Path("vajra/downloads/history.py"); s=p.read_text()
if "    def remove(self,distro_id,path):" not in s:
    anchor="    def verified_existing(self):\n"
    methods="    def remove(self,distro_id,path):\n        records=[x for x in self.load() if not (x.distro_id==distro_id and x.path==str(path))]\n        self.save(records)\n\n    def get(self,distro_id,path):\n        for record in self.load():\n            if record.distro_id==distro_id and record.path==str(path): return record\n        return None\n\n"
    if anchor not in s: raise SystemExit("history anchor not found")
    s=s.replace(anchor,methods+anchor,1)
p.write_text(s)

p=Path("vajra/ui/download_history_dialog.py"); s=p.read_text()
if "from vajra.downloads.library import inspect_record" not in s:
    s=s.replace("from vajra.downloads.history import DownloadHistory\n","from vajra.downloads.history import DownloadHistory\nfrom vajra.downloads.library import inspect_record\n",1)
if "resume_requested = Signal(str, str, str)" not in s:
    s=s.replace("    flash_requested = Signal(str)\n","    flash_requested = Signal(str)\n    resume_requested = Signal(str, str, str)\n",1)
s=s.replace("lambda checked=False, r=record: self.show_resume_info(r)","lambda checked=False, r=record: self.request_resume(r)")
if "    def request_resume(self,record):" not in s:
    anchor="    def show_resume_info(self,record):\n"
    methods="    def request_resume(self,record):\n        self.resume_requested.emit(record.distro_id,record.architecture,record.path)\n        self.accept()\n\n    def recheck_record(self,record):\n        state,digest=inspect_record(record)\n        record.state=state\n        if digest: record.actual_sha256=digest\n        self.history.upsert(record)\n        QMessageBox.information(self,\"ISO check complete\",f\"State: {state}\")\n        self.refresh()\n\n    def remove_record(self,record):\n        self.history.remove(record.distro_id,record.path)\n        self.refresh()\n\n"
    if anchor not in s: raise SystemExit("resume method anchor not found")
    s=s.replace(anchor,methods+anchor,1)
if 'QPushButton("Recheck ISO")' not in s:
    anchor="            actions=QHBoxLayout()\n"
    block="            actions=QHBoxLayout()\n            recheck=QPushButton(\"Recheck ISO\")\n            recheck.clicked.connect(lambda checked=False,r=record:self.recheck_record(r))\n            remove=QPushButton(\"Remove Entry\")\n            remove.clicked.connect(lambda checked=False,r=record:self.remove_record(r))\n            actions.addWidget(recheck)\n            actions.addWidget(remove)\n"
    if anchor not in s: raise SystemExit("actions anchor not found")
    s=s.replace(anchor,block,1)
p.write_text(s)

p=Path("vajra/ui/resolved_download_dialog.py"); s=p.read_text()
if "resume_destination=None" not in s:
    s=s.replace("    def __init__(self,distro_id,architecture,parent=None):\n","    def __init__(self,distro_id,architecture,parent=None,resume_destination=None):\n",1)
if "self.resume_destination=resume_destination" not in s:
    s=s.replace("        self.distro_id=distro_id; self.architecture=architecture\n","        self.distro_id=distro_id; self.architecture=architecture\n        self.resume_destination=resume_destination\n",1)
old='        destination,_=QFileDialog.getSaveFileName(self,"Save ISO",str(Path.home()/"Downloads"/image.filename),"ISO images (*.iso);;All files (*)")\n        if not destination:return\n'
new='        if self.resume_destination:\n            destination=self.resume_destination\n            self.resume_destination=None\n        else:\n            destination,_=QFileDialog.getSaveFileName(self,"Save ISO",str(Path.home()/"Downloads"/image.filename),"ISO images (*.iso);;All files (*)")\n            if not destination:return\n'
if old in s: s=s.replace(old,new,1)
elif "if self.resume_destination:" not in s: raise SystemExit("destination anchor not found")
p.write_text(s)

p=Path("vajra/ui/main_window.py"); s=p.read_text()
needle="        dialog.flash_requested.connect(\n            self.open_verified_history_image\n        )\n"
if "dialog.resume_requested.connect" not in s:
    if needle not in s: raise SystemExit("history signal anchor not found")
    s=s.replace(needle,needle+"        dialog.resume_requested.connect(self.resume_history_download)\n",1)
if "    def resume_history_download(self,distro_id,architecture,path):" not in s:
    anchor="    def open_verified_history_image(self, path):\n"
    method="    def resume_history_download(self,distro_id,architecture,path):\n        dialog=ResolvedDownloadDialog(distro_id,architecture,parent=self,resume_destination=path)\n        dialog.image_ready.connect(self.open_verified_history_image)\n        dialog.exec()\n\n"
    if anchor not in s: raise SystemExit("flash history anchor not found")
    s=s.replace(anchor,method+anchor,1)
p.write_text(s)
print("Phase 8.9 applied.")
