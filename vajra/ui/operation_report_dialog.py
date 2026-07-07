from datetime import datetime
from PySide6.QtWidgets import (
    QDialog,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,
    QScrollArea,QWidget,QFrame
)
from vajra.writer.operation_log import FlashOperationLog


def format_time(value):
    try:
        return datetime.fromtimestamp(float(value)).strftime("%Y-%m-%d %H:%M:%S")
    except (TypeError,ValueError,OSError):
        return "Unknown"


class OperationReportDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Flash Operation Reports")
        self.resize(820,560)
        self.log=FlashOperationLog()

        layout=QVBoxLayout(self)
        title=QLabel("Flash Operation Reports")
        title.setStyleSheet("font-size:24px;font-weight:700;")
        layout.addWidget(title)

        self.scroll=QScrollArea()
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll)

        buttons=QHBoxLayout()
        refresh=QPushButton("Refresh")
        refresh.clicked.connect(self.refresh)
        close=QPushButton("Close")
        close.clicked.connect(self.accept)
        buttons.addWidget(refresh)
        buttons.addStretch()
        buttons.addWidget(close)
        layout.addLayout(buttons)
        self.refresh()

    def build_operations(self):
        events=self.log.load()
        operations=[]
        current=None

        for event in events:
            kind=event.get("event","unknown")
            if kind=="started":
                if current:
                    operations.append(current)
                current={
                    "started":event,
                    "stages":[],
                    "terminal":None,
                    "recovery":None,
                }
                continue

            if current is None:
                continue

            if kind=="stage":
                current["stages"].append(event)
            elif kind=="recovery_assessment":
                current["recovery"]=event
            elif kind in {"completed","cancelled","failed"}:
                current["terminal"]=event
                operations.append(current)
                current=None

        if current:
            operations.append(current)

        return list(reversed(operations))

    def refresh(self):
        content=QWidget()
        cards=QVBoxLayout(content)
        operations=self.build_operations()

        if not operations:
            cards.addWidget(QLabel("No flash operation reports yet."))

        for operation in operations:
            start=operation["started"]
            terminal=operation["terminal"] or {}
            recovery=operation["recovery"] or {}

            card=QFrame()
            card.setFrameShape(QFrame.StyledPanel)
            box=QVBoxLayout(card)

            state=terminal.get("event","running")
            heading=QLabel(f"{state.upper()} • {format_time(start.get('time'))}")
            heading.setStyleSheet("font-weight:700;font-size:16px;")
            box.addWidget(heading)

            image=start.get("image","Unknown")
            device=start.get("device","Unknown")
            end_time=format_time(terminal.get("time")) if terminal else "Still running / no terminal event"
            stage=(operation["stages"][-1].get("stage")
                   if operation["stages"] else "No stage recorded")
            recovery_state=(
                terminal.get("recovery_state")
                or recovery.get("state")
                or "not applicable"
            )

            details=QLabel(
                f"Image: {image}\n"
                f"Target: {device}\n"
                f"Started: {format_time(start.get('time'))}\n"
                f"Ended: {end_time}\n"
                f"Last stage: {stage}\n"
                f"Recovery assessment: {recovery_state}"
            )
            details.setWordWrap(True)
            box.addWidget(details)

            if terminal.get("message"):
                error=QLabel(f"Failure: {terminal['message']}")
                error.setWordWrap(True)
                box.addWidget(error)

            cards.addWidget(card)

        cards.addStretch()
        self.scroll.setWidget(content)
