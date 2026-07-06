ALIASES = {
    "x86_64": "amd64", "amd64": "amd64", "x64": "amd64",
    "i386": "i386", "i486": "i386", "i586": "i386",
    "i686": "i386", "x86": "i386", "32bit": "i386",
    "aarch64": "arm64", "arm64": "arm64",
}

def normalize_architecture(value):
    key = str(value or "").strip().lower()
    return ALIASES.get(key, key)

def architecture_compatible(candidate, machine):
    return normalize_architecture(candidate) == normalize_architecture(machine)
