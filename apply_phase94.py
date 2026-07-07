from pathlib import Path

p=Path("vajra/ui/main_window.py")
s=p.read_text()

imp="from vajra.ui.operation_report_dialog import OperationReportDialog\n"
anchor="from vajra.ui.download_history_dialog import DownloadHistoryDialog\n"
if imp not in s:
    if anchor not in s: raise SystemExit("DownloadHistoryDialog import anchor not found")
    s=s.replace(anchor,anchor+imp,1)

if "    def open_operation_reports(self):" not in s:
    anchor="    def open_download_history(self):\n"
    method="    def open_operation_reports(self):\n        OperationReportDialog(parent=self).exec()\n\n"
    if anchor not in s: raise SystemExit("open_download_history anchor not found")
    s=s.replace(anchor,method+anchor,1)

if 'reports = QPushButton("Operation Reports")' not in s:
    anchor='        history = QPushButton("Download History")\n        history.clicked.connect(self.open_download_history)\n'
    block=anchor+'        reports = QPushButton("Operation Reports")\n        reports.clicked.connect(self.open_operation_reports)\n'
    if anchor not in s: raise SystemExit("history button anchor not found")
    s=s.replace(anchor,block,1)

if "        choice_row.addWidget(reports)\n" not in s:
    anchor="        choice_row.addWidget(history)\n"
    if anchor not in s: raise SystemExit("history choice_row anchor not found")
    s=s.replace(anchor,anchor+"        choice_row.addWidget(reports)\n",1)

p.write_text(s)
print("Phase 9.4 applied: operation report UI installed.")
