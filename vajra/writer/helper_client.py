import json

from PySide6.QtCore import QProcess, QObject, Signal

from vajra.writer.privilege import build_privileged_command


class HelperClient(QObject):
    progress = Signal(int)
    stage = Signal(str)
    completed = Signal()
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, helper_path, image_path, identity, parent=None, plan=None):
        super().__init__(parent)
        self.buffer = ""
        self.reported_error = False
        self.cancel_requested = False
        self.terminal_event = False
        self.process_error = ""
        self.process = QProcess(self)

        cmd = build_privileged_command(helper_path, image_path, identity)
        if plan is not None:
            cmd.extend([
                "--mode", plan.mode,
                "--scheme", plan.partition_scheme,
                "--target-system", plan.target_system,
                "--file-system", plan.file_system,
                "--volume-label", plan.volume_label,
            ])

        self.program, self.arguments = cmd[0], cmd[1:]
        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.finished.connect(self.finished)
        self.process.errorOccurred.connect(self.on_process_error)

    def start(self):
        self.process.start(self.program, self.arguments)

    def cancel(self):
        self.cancel_requested = True
        if self.process.state() != QProcess.NotRunning:
            self.process.terminate()

    def force_kill(self):
        if self.process.state() != QProcess.NotRunning:
            self.process.kill()

    def is_running(self):
        return self.process.state() != QProcess.NotRunning

    def on_process_error(self, _error):
        # QProcess may emit errorOccurred and then finished. Store the error and
        # let finished() produce exactly one terminal signal.
        self.process_error = self.process.errorString()

    def _handle_line(self, line):
        try:
            event = json.loads(line)
        except (TypeError, ValueError, json.JSONDecodeError):
            return

        kind = event.get("event")
        if kind == "progress":
            value = max(0, min(100, int(event.get("value", 0))))
            self.progress.emit(value)
        elif kind == "stage":
            self.stage.emit(str(event.get("message", "")))
        elif kind == "error" and not self.terminal_event:
            self.reported_error = True
            self.terminal_event = True
            self.failed.emit(str(event.get("message", "Helper failed.")))
        elif kind == "complete" and not self.terminal_event:
            self.terminal_event = True
            self.completed.emit()

    def read_stdout(self):
        self.buffer += bytes(
            self.process.readAllStandardOutput()
        ).decode(errors="replace")

        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            self._handle_line(line)

    def _drain_stdout(self):
        self.read_stdout()
        if self.buffer.strip():
            line, self.buffer = self.buffer, ""
            self._handle_line(line)

    def finished(self, code, status):
        # Drain output first: the helper's final complete/error event can arrive
        # in the same event-loop turn as process termination.
        self._drain_stdout()

        if self.terminal_event:
            return

        if self.cancel_requested:
            self.terminal_event = True
            self.cancelled.emit()
            return

        self.terminal_event = True
        stderr = bytes(
            self.process.readAllStandardError()
        ).decode(errors="replace").strip()

        if code:
            message = stderr or self.process_error
            if not message:
                message = (
                    "Authorization cancelled or denied."
                    if code == 126
                    else f"Helper exited with code {code}."
                )
            self.failed.emit(message)
            return

        # A clean process exit without the protocol's complete event is not a
        # successful flash. Treat it as a protocol failure instead of leaving
        # the UI stuck or reporting a false success.
        self.failed.emit(
            "Helper exited without reporting completion; operation status is unknown."
        )
