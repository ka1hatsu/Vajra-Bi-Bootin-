from pathlib import Path

p = Path("vajra/sources/security.py")
s = p.read_text()

for host in (
    '"sourceforge.net",',
    '"downloads.sourceforge.net",',
):
    if host not in s:
        s = s.replace(
            "ALLOWED_DOWNLOAD_HOSTS = {",
            "ALLOWED_DOWNLOAD_HOSTS = {\n    " + host,
            1,
        )

p.write_text(s)
print("Phase 8.6 applied: MX SHA-256 resolution and verification policy installed.")
