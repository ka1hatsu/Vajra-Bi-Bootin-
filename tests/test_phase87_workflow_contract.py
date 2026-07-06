from pathlib import Path

def dialog_text():
    return Path("vajra/ui/resolved_download_dialog.py").read_text()

def test_explicit_workflow_states_exist():
    text=dialog_text()
    for state in ("resolving","downloading","verifying","verified","failed","cancelled","cancelling"):
        assert state in text

def test_duplicate_download_guard_exists():
    text=dialog_text()
    assert "if self.worker and self.worker.isRunning():" in text

def test_verification_precedes_handoff():
    text=dialog_text()
    start=text.index("    def on_complete(self,path,digest):")
    end=text.index("\n    def on_failed",start)
    method=text[start:end]
    assert method.index('set_workflow_state("verifying"') < method.index("evaluate_download_verification")
    assert method.index("if not decision.can_flash:") < method.index("self.image_ready.emit(path)")
