from pathlib import Path

# Wire DownloadSession into resolved download dialog.
p=Path("vajra/ui/resolved_download_dialog.py")
s=p.read_text()

imp="from vajra.downloads.session import DownloadSession\n"
anchor="from vajra.verification.policy import evaluate_download_verification\n"
if imp not in s:
    if anchor not in s:
        raise SystemExit("verification policy import anchor not found")
    s=s.replace(anchor,anchor+imp,1)

init_anchor="        self.images=[]; self.resolver=None; self.worker=None;"
if init_anchor in s and "self.download_session" not in s:
    s=s.replace(init_anchor,init_anchor+" self.download_session=None",1)

worker_anchor="        self.worker=DownloadWorker(image.image_url,path,image.sha256 or None)"
if worker_anchor not in s:
    raise SystemExit("DownloadWorker construction anchor not found")
if "DownloadSession(" not in s:
    replacement=(
        '        self.download_session=DownloadSession(self.distro_id,image,path)\n'
        + worker_anchor
    )
    s=s.replace(worker_anchor,replacement,1)

progress_anchor="    def on_progress(self,done,total):"
if progress_anchor in s and "self.download_session.progress" not in s:
    start=s.index(progress_anchor)
    line_end=s.index("\n",start)+1
    s=s[:line_end]+'        if self.download_session: self.download_session.progress(done,total)\n'+s[line_end:]

failed_anchor="    def on_failed(self,message):"
if failed_anchor in s and "self.download_session.failed()" not in s:
    start=s.index(failed_anchor); end=s.index("\n",start)+1
    s=s[:end]+'        if self.download_session: self.download_session.failed()\n'+s[end:]

cancel_anchor="    def on_cancelled(self):"
if cancel_anchor in s and "self.download_session.cancelled()" not in s:
    start=s.index(cancel_anchor); end=s.index("\n",start)+1
    s=s[:end]+'        if self.download_session: self.download_session.cancelled()\n'+s[end:]

emit_anchor="        self.image_ready.emit(path)"
if emit_anchor in s and "self.download_session.completed" not in s:
    s=s.replace(
        emit_anchor,
        '        if self.download_session: self.download_session.completed(path,digest,True)\n'+emit_anchor,
        1
    )

p.write_text(s)

# Wire history dialog into main window with an adaptive welcome-page button.
p=Path("vajra/ui/main_window.py")
s=p.read_text()

history_import="from vajra.ui.download_history_dialog import DownloadHistoryDialog\n"
flash_import="from vajra.ui.flash_dialog import FlashDialog\n"
if history_import not in s:
    if flash_import not in s:
        raise SystemExit("FlashDialog import anchor not found")
    s=s.replace(flash_import,flash_import+history_import,1)

method_anchor="    def open_usb_devices(self):"
if "def open_download_history" not in s:
    method=(
        '    def open_download_history(self):\n'
        '        dialog=DownloadHistoryDialog(parent=self)\n'
        '        dialog.flash_requested.connect(self.open_verified_history_image)\n'
        '        dialog.exec()\n\n'
        '    def open_verified_history_image(self,path):\n'
        '        dialog=FlashDialog(parent=self)\n'
        '        dialog.image.setText(path)\n'
        '        try:\n'
        '            dialog.analyze_path(path)\n'
        '        except AttributeError:\n'
        '            pass\n'
        '        dialog.exec()\n\n'
    )
    if method_anchor not in s:
        raise SystemExit("main-window method anchor not found")
    s=s.replace(method_anchor,method+method_anchor,1)

# Add button beside existing welcome actions when a stable anchor is present.
if 'history.clicked.connect(self.open_download_history)' not in s:
    anchors=[
        '        existing.clicked.connect(self.open_download_center)\n',
        '        manual.clicked.connect(self.open_distro_browser)\n',
    ]
    inserted=False
    for a in anchors:
        if a in s:
            block=(
                a+
                '        history = QPushButton("Download History")\n'
                '        history.clicked.connect(self.open_download_history)\n'
            )
            s=s.replace(a,block,1)
            # Add widget near known welcome layout calls if possible.
            for widget_anchor in (
                '        actions.addWidget(existing)\n',
                '        button_row.addWidget(downloads)\n',
            ):
                if widget_anchor in s:
                    s=s.replace(widget_anchor,widget_anchor+'        actions.addWidget(history)\n' if "actions.addWidget" in widget_anchor else widget_anchor,1)
                    break
            inserted=True
            break
    if not inserted:
        print("Warning: history methods installed, but welcome button anchor was not found.")

p.write_text(s)
print("Phase 8.8.1 applied: persistent sessions and Download History UI installed.")
