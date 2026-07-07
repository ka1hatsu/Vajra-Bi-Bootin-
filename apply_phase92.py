from pathlib import Path

# Patch prepared_helper.py
p = Path("vajra/boot/prepared_helper.py")
s = p.read_text()
imp = "from vajra.boot.process_runner import run_managed, ManagedCommandError\n"
anchor = "from vajra.boot.windows_media import split_install_wim, WindowsMediaError\n"
if imp not in s:
    if anchor not in s: raise SystemExit("prepared_helper import anchor not found")
    s = s.replace(anchor, anchor + imp, 1)

old = """def run(cmd, input_text=None):
    x = subprocess.run(cmd, input=input_text, capture_output=True, text=True)
    if x.returncode:
        raise PreparedMediaError(x.stderr.strip() or x.stdout.strip() or "Command failed")
    return x
"""
new = """def run(cmd, input_text=None, cancel_check=None):
    try:
        return run_managed(
            cmd,
            input_text=input_text,
            cancel_check=cancel_check,
        )
    except ManagedCommandError as e:
        raise PreparedMediaError(str(e)) from e
"""
if old not in s and "run_managed(" not in s: raise SystemExit("prepared_helper run anchor not found")
if old in s: s = s.replace(old, new, 1)

s = s.replace(
    "def prepare_fat32_media(image, device, plan, progress=None):",
    "def prepare_fat32_media(image, device, plan, progress=None, cancel_check=None):",
)

# Explicitly pass cancel_check to all single-line run calls.
repls = {
    'run(["sgdisk", "--zap-all", device])': 'run(["sgdisk", "--zap-all", device], cancel_check=cancel_check)',
    'run(["sgdisk", "-n", "1:0:0", "-t", "1:ef00", device])': 'run(["sgdisk", "-n", "1:0:0", "-t", "1:ef00", device], cancel_check=cancel_check)',
    'run(["sfdisk", device], "label: dos\\n,0x0c,*\\n")': 'run(["sfdisk", device], "label: dos\\n,0x0c,*\\n", cancel_check=cancel_check)',
    'run(["partprobe", device])': 'run(["partprobe", device], cancel_check=cancel_check)',
    'run(["mkfs.fat", "-F", "32", "-n", sanitize_label(plan.volume_label), part])': 'run(["mkfs.fat", "-F", "32", "-n", sanitize_label(plan.volume_label), part], cancel_check=cancel_check)',
    'run(["mount", part, mount_dir])': 'run(["mount", part, mount_dir], cancel_check=cancel_check)',
    'run(["sync"])': 'run(["sync"], cancel_check=cancel_check)',
}
for a, b in repls.items(): s = s.replace(a, b)

# Multiline extraction/copy commands.
s = s.replace(
    '                        image,\n                    ])',
    '                        image,\n                    ], cancel_check=cancel_check)',
)
s = s.replace(
    '                        mount_dir,\n                    ])',
    '                        mount_dir,\n                    ], cancel_check=cancel_check)',
)
s = s.replace(
    '                    image,\n                ])',
    '                    image,\n                ], cancel_check=cancel_check)',
)
s = s.replace(
    "split_install_wim(extract_dir)",
    "split_install_wim(extract_dir, cancel_check=cancel_check)",
)
p.write_text(s)

# Patch windows_media.py
p = Path("vajra/boot/windows_media.py")
s = p.read_text()
imp = "from vajra.boot.process_runner import run_managed, ManagedCommandError\n"
if imp not in s:
    s = s.replace("from pathlib import Path\n", "from pathlib import Path\n" + imp, 1)
s = s.replace(
    "def split_install_wim(root,max_mb=3800):",
    "def split_install_wim(root,max_mb=3800,cancel_check=None):",
)
old = '    x=subprocess.run([tool,"split",str(wim),str(dest),str(max_mb)],capture_output=True,text=True)\n    if x.returncode: raise WindowsMediaError(x.stderr.strip() or "WIM split failed.")'
new = '    try:\n        run_managed([tool,"split",str(wim),str(dest),str(max_mb)],cancel_check=cancel_check)\n    except ManagedCommandError as e:\n        raise WindowsMediaError(str(e)) from e'
if old in s: s = s.replace(old, new, 1)
p.write_text(s)

# Patch privileged helper signal handling and cancellation propagation.
p = Path("vajra/writer/helper.py")
s = p.read_text()
s = s.replace("import argparse,json,os", "import argparse,json,os,signal", 1)
anchor = 'def emit(event,**fields): print(json.dumps({"event":event,**fields}),flush=True)\n'
if "_cancel_requested=False" not in s:
    block = """_cancel_requested=False

def request_cancel(signum, frame):
    global _cancel_requested
    _cancel_requested=True

def cancel_requested():
    return _cancel_requested

signal.signal(signal.SIGTERM, request_cancel)
signal.signal(signal.SIGINT, request_cancel)

"""
    if anchor not in s: raise SystemExit("helper emit anchor not found")
    s = s.replace(anchor, block + anchor, 1)
old = """                progress=lambda value, message: (
                    emit("stage", message=message),
                    emit("progress", value=value),
                ),
            )"""
new = """                progress=lambda value, message: (
                    emit("stage", message=message),
                    emit("progress", value=value),
                ),
                cancel_check=cancel_requested,
            )"""
if old in s: s = s.replace(old, new, 1)
p.write_text(s)

print("Phase 9.2 applied successfully.")
