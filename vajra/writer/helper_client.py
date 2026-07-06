import json
from PySide6.QtCore import QProcess, QObject, Signal
from vajra.writer.privilege import build_privileged_command

class HelperClient(QObject):
    progress=Signal(int); stage=Signal(str); completed=Signal(); failed=Signal(str)
    def __init__(self,helper_path,image_path,identity,parent=None):
        super().__init__(parent); self.buffer=""; self.reported_error=False
        self.process=QProcess(self)
        cmd=build_privileged_command(helper_path,image_path,identity)
        self.program,self.arguments=cmd[0],cmd[1:]
        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.finished.connect(self.finished)
        self.process.errorOccurred.connect(lambda _: self.failed.emit(self.process.errorString()))
    def start(self): self.process.start(self.program,self.arguments)
    def cancel(self):
        if self.process.state()!=QProcess.NotRunning: self.process.terminate()
    def read_stdout(self):
        self.buffer+=bytes(self.process.readAllStandardOutput()).decode(errors="replace")
        while "\n" in self.buffer:
            line,self.buffer=self.buffer.split("\n",1)
            try:e=json.loads(line)
            except Exception:continue
            kind=e.get("event")
            if kind=="progress":self.progress.emit(int(e.get("value",0)))
            elif kind=="stage":self.stage.emit(str(e.get("message","")))
            elif kind=="error":self.reported_error=True; self.failed.emit(str(e.get("message","Helper failed.")))
            elif kind=="complete":self.completed.emit()
    def finished(self,code,status):
        if code and not self.reported_error:
            err=bytes(self.process.readAllStandardError()).decode(errors="replace").strip()
            self.failed.emit(err or ("Authorization cancelled or denied." if code==126 else f"Helper exited with code {code}."))
