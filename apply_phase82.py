from pathlib import Path

p = Path("vajra/ui/main_window.py")
s = p.read_text()

imports = (
    "from vajra.workflow.recommendation_download import "
    "RecommendationDownloadFlow\n"
)
if imports not in s:
    rows = s.splitlines()
    pos = 0
    for i, line in enumerate(rows):
        if line.startswith("import ") or line.startswith("from "):
            pos = i + 1
    rows.insert(pos, imports.rstrip())
    s = "\n".join(rows) + "\n"

p.write_text(s)

print("Phase 8.2 workflow controller installed.")
print("RecommendationDownloadFlow is now importable in main_window.py.")
print("Run inspect_phase82.sh to identify the exact navigation and ISO-field hooks.")
