import re

SHA256_RE = re.compile(r"^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$")

def parse_sha256sums(text):
    result = {}
    for line in text.splitlines():
        m = SHA256_RE.match(line)
        if m:
            result[m.group(2)] = m.group(1).lower()
    return result
