from pathlib import Path
p=Path("vajra/sources/security.py")
s=p.read_text()
for host in ('"releases.ubuntu.com",','"cdimage.debian.org",','"fedoraproject.org",','"download.fedoraproject.org",'):
    if host not in s: s=s.replace('ALLOWED_DOWNLOAD_HOSTS = {','ALLOWED_DOWNLOAD_HOSTS = {\n    '+host,1)
p.write_text(s)
p=Path("vajra/ui/resolved_download_dialog.py")
s=p.read_text()
if 'import webbrowser' not in s: s='import webbrowser\n'+s
anchor='from vajra.ui.release_resolver_worker import ReleaseResolverWorker\n'
imp='from vajra.sources.registry import get_official_fallback\n'
if imp not in s: s=s.replace(anchor,anchor+imp,1)
start=s.find('    def resolve_failed(self,message):')
end=s.find('\n    def selected_image',start)
if start<0 or end<0: raise SystemExit('resolve_failed method anchor not found')
new = "    def resolve_failed(self,message):\n        self.progress.setRange(0,100)\n        self.progress.setValue(0)\n        fallback=get_official_fallback(self.distro_id)\n        self.status.setText('No compatible direct ISO was resolved automatically. You can use the official download page instead.\\n\\n'+message)\n        if fallback:\n            self.download.setText('Open Official Download Page')\n            self.download.setEnabled(True)\n            try:\n                self.download.clicked.disconnect()\n            except Exception:\n                pass\n            self.download.clicked.connect(lambda: webbrowser.open(fallback))\n        else:\n            self.download.setEnabled(False)\n"
s=s[:start]+new+s[end:]
p.write_text(s)
print('Phase 8.4 applied.')
