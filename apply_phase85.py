from pathlib import Path
p=Path("vajra/sources/security.py")
s=p.read_text()
hosts=[
    '"download.fedoraproject.org",',
    '"sourceforge.net",',
    '"downloads.sourceforge.net",',
]
for host in hosts:
    if host not in s:
        s=s.replace("ALLOWED_DOWNLOAD_HOSTS = {","ALLOWED_DOWNLOAD_HOSTS = {\n    "+host,1)
p.write_text(s)
print("Phase 8.5 applied: dedicated Mint, MX Linux and Fedora resolvers installed.")
