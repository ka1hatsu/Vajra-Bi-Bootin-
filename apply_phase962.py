from pathlib import Path
p=Path("vajra/ui/flash_dialog.py")
s=p.read_text()
s=s.replace("self.resize(720,440)","self.resize(820,680)",1)
marker="class FlashDialog(QDialog):\n"
helper="class SectionLabel(QLabel):\n    def __init__(self, text):\n        super().__init__(text)\n        self.setObjectName(\"sectionLabel\")\n\n\n"
if "class SectionLabel(QLabel):" not in s:
    if marker not in s: raise SystemExit("FlashDialog anchor not found")
    s=s.replace(marker,helper+marker,1)
anchors=[
("self.image=QLineEdit();","l.addWidget(SectionLabel(\"BOOT IMAGE\"))\n        self.image=QLineEdit();"),
("self.combo=QComboBox();","l.addWidget(SectionLabel(\"TARGET USB DEVICE\"))\n        self.combo=QComboBox();"),
("form=QFormLayout()","l.addWidget(SectionLabel(\"BOOT AND FORMAT OPTIONS\"))\n        form=QFormLayout(); form.setHorizontalSpacing(18); form.setVerticalSpacing(9)"),
("self.analysis_label=QLabel(","l.addWidget(SectionLabel(\"COMPATIBILITY\"))\n        self.analysis_label=QLabel("),
("self.confirm=QLineEdit();","l.addWidget(SectionLabel(\"SAFETY CONFIRMATION\"))\n        self.confirm=QLineEdit();"),
]
for a,b in anchors:
    if a in s and b not in s: s=s.replace(a,b,1)
s=s.replace('self.compatibility_label=QLabel("Compatibility: waiting for image selection")','self.compatibility_label=QLabel("Compatibility: waiting for image selection"); self.compatibility_label.setObjectName("compatibilityPanel")',1)
s=s.replace('self.confirm=QLineEdit(); self.confirm.setPlaceholderText("Type ERASE to enable writing")','self.confirm=QLineEdit(); self.confirm.setObjectName("eraseConfirmation"); self.confirm.setPlaceholderText("Type ERASE to enable writing")',1)
s=s.replace('self.stage=QLabel("Ready")','self.stage=QLabel("Ready"); self.stage.setObjectName("stageStatus")',1)
p.write_text(s)
theme=Path("vajra/ui/dialog_theme.py"); t=theme.read_text()
extra="\n/* Phase 9.6.2 flash workflow hierarchy */\nQLabel#sectionLabel { color: #7895cf; font-size: 11px; font-weight: 800; padding-top: 10px; padding-bottom: 2px; }\nQLabel#compatibilityPanel { background: #10192d; border: 1px solid #2d3b59; border-radius: 8px; padding: 10px; color: #cbd7eb; }\nQLabel#stageStatus { background: #0f1729; border-left: 3px solid #3973e6; padding: 8px 10px; color: #b9c8e2; }\nQLineEdit#eraseConfirmation { border: 1px solid #6e3944; }\nQLineEdit#eraseConfirmation:focus { border: 1px solid #b24b5e; }\n"
if "Phase 9.6.2 flash workflow hierarchy" not in t:
    pos=t.rfind('"""')
    if pos<0: raise SystemExit("Theme closing anchor not found")
    t=t[:pos]+extra+"\n"+t[pos:]; theme.write_text(t)
print("Phase 9.6.2 applied.")
