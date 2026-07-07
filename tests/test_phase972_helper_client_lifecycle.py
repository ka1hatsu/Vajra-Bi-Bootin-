from pathlib import Path


def helper_client_source():
    return Path("vajra/writer/helper_client.py").read_text()


def test_finished_drains_protocol_output_before_terminal_decision():
    source = helper_client_source()
    finished = source[source.index("    def finished("):]
    assert finished.index("self._drain_stdout()") < finished.index("if self.terminal_event:")


def test_clean_exit_without_complete_is_failure():
    source = helper_client_source()
    assert "Helper exited without reporting completion" in source


def test_process_error_is_deferred_to_single_terminal_path():
    source = helper_client_source()
    method = source[source.index("    def on_process_error("):source.index("    def _handle_line(")]
    assert "self.process_error = self.process.errorString()" in method
    assert "self.failed.emit" not in method


def test_progress_is_clamped_to_qprogressbar_range():
    source = helper_client_source()
    assert "max(0, min(100" in source


def test_terminal_protocol_events_are_idempotent():
    source = helper_client_source()
    assert 'kind == "error" and not self.terminal_event' in source
    assert 'kind == "complete" and not self.terminal_event' in source
