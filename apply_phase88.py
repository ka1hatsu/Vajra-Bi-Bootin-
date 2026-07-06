from pathlib import Path

gitignore=Path(".gitignore")
text=gitignore.read_text() if gitignore.exists() else ""
entry=".vajra-state/\n"
if entry not in text:
    gitignore.write_text(text+("\n" if text and not text.endswith("\n") else "")+entry)

print("Phase 8.8 core installed: persistent download history and resumable session model.")
