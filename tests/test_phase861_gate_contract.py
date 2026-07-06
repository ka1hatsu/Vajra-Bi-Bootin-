from pathlib import Path

def test_resolved_dialog_uses_verification_policy():
    text=Path("vajra/ui/resolved_download_dialog.py").read_text()
    assert "evaluate_download_verification" in text
    assert "if not decision.can_flash:" in text
    assert "self.image_ready.emit(path)" in text

def test_emit_occurs_after_gate():
    text=Path("vajra/ui/resolved_download_dialog.py").read_text()
    start=text.index("    def on_complete(self,path,digest):")
    end=text.index("\n    def on_failed",start)
    method=text[start:end]
    assert method.index("if not decision.can_flash:") < method.index("self.image_ready.emit(path)")
