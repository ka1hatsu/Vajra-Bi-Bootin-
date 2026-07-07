from pathlib import Path

theme_path=Path("vajra/ui/dialog_theme.py")
theme_path.write_text('DIALOG_STYLE = """\nQDialog { background: #0b1224; color: #eef4ff; }\nQLabel { color: #dce6f7; }\nQLabel#dialogTitle { font-size: 24px; font-weight: 800; color: #f5f8ff; padding-bottom: 2px; }\nQLabel#dialogSubtitle { color: #9eacc5; font-size: 13px; padding-bottom: 8px; }\nQLineEdit, QComboBox {\n    background: #10192d; color: #eef4ff; border: 1px solid #33415f;\n    border-radius: 8px; padding: 9px 10px; min-height: 20px;\n}\nQLineEdit:focus, QComboBox:focus { border: 1px solid #4e7df2; }\nQPushButton {\n    background: #202c48; color: #eef4ff; border: 1px solid #354563;\n    border-radius: 8px; padding: 9px 15px; min-height: 20px;\n}\nQPushButton:hover { background: #293956; }\nQPushButton:disabled { color: #69758c; background: #151d30; border-color: #263149; }\nQPushButton#primaryAction { background: #2563dc; border-color: #3476ef; font-weight: 700; }\nQPushButton#primaryAction:hover { background: #3273ea; }\nQPushButton#dangerAction { background: #51212a; border-color: #7c3441; }\nQPushButton#dangerAction:hover { background: #652936; }\nQProgressBar {\n    border: 1px solid #33415f; border-radius: 7px; background: #10192d;\n    text-align: center; min-height: 18px;\n}\nQProgressBar::chunk { background: #3973e6; border-radius: 6px; }\nQMessageBox { background: #0b1224; }\n"""\n')

def add_theme_import(s):
    line="from vajra.ui.dialog_theme import DIALOG_STYLE\\n"
    if line not in s:
        idx=s.find("class ")
        if idx < 0: raise SystemExit("class anchor not found")
        s=s[:idx]+line+"\\n"+s[idx:]
    return s

p=Path("vajra/ui/flash_dialog.py"); s=add_theme_import(p.read_text())
needle='        super().__init__(parent); self.setWindowTitle("Write Image to USB");'
if needle in s and "self.setStyleSheet(DIALOG_STYLE)" not in s:
    s=s.replace(needle,'        super().__init__(parent); self.setStyleSheet(DIALOG_STYLE); self.setWindowTitle("Write Image to USB");',1)
s=s.replace('title=QLabel("Write ISO / IMG to USB"); title.setStyleSheet("font-size:24px;font-weight:700;");','title=QLabel("Write ISO / IMG to USB"); title.setObjectName("dialogTitle");',1)
s=s.replace('note=QLabel("Writing destroys existing data on the selected USB drive. Only devices passing Vajra eligibility checks are listed.");','note=QLabel("Select an image and an eligible USB device. Writing will erase the selected device."); note.setObjectName("dialogSubtitle");',1)
old='self.write=QPushButton("Write and Verify"); self.cancel=QPushButton("Cancel");'
new='self.write=QPushButton("Write and Verify"); self.write.setObjectName("primaryAction"); self.cancel=QPushButton("Cancel"); self.cancel.setObjectName("dangerAction");'
if old in s: s=s.replace(old,new,1)
p.write_text(s)

for filename in ("resolved_download_dialog.py","catalog_download_dialog.py"):
    p=Path("vajra/ui")/filename
    s=add_theme_import(p.read_text())
    anchor="        super().__init__(parent)\\n"
    if anchor in s and "self.setStyleSheet(DIALOG_STYLE)" not in s:
        s=s.replace(anchor,anchor+"        self.setStyleSheet(DIALOG_STYLE)\\n",1)
    p.write_text(s)

p=Path("vajra/ui/resolved_download_dialog.py"); s=p.read_text()
if 'self.download.setObjectName("primaryAction")' not in s:
    s=s.replace('self.download=QPushButton("Download ISO")','self.download=QPushButton("Download ISO"); self.download.setObjectName("primaryAction")',1)
p.write_text(s)

p=Path("vajra/ui/catalog_download_dialog.py"); s=p.read_text()
if 'self.download_button.setObjectName("primaryAction")' not in s:
    lines=s.splitlines(); out=[]; inserted=False
    for line in lines:
        out.append(line)
        if not inserted and "self.download_button" in line and "QPushButton(" in line:
            indent=line[:len(line)-len(line.lstrip())]
            out.append(indent+'self.download_button.setObjectName("primaryAction")')
            inserted=True
    s="\\n".join(out)+"\\n"
p.write_text(s)

print("Phase 9.6.1 applied.")
