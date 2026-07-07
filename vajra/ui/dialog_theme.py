DIALOG_STYLE = """
QDialog { background: #0b1224; color: #eef4ff; }
QLabel { color: #dce6f7; }
QLabel#dialogTitle { font-size: 24px; font-weight: 800; color: #f5f8ff; padding-bottom: 2px; }
QLabel#dialogSubtitle { color: #9eacc5; font-size: 13px; padding-bottom: 8px; }
QLineEdit, QComboBox {
    background: #10192d; color: #eef4ff; border: 1px solid #33415f;
    border-radius: 8px; padding: 9px 10px; min-height: 20px;
}
QLineEdit:focus, QComboBox:focus { border: 1px solid #4e7df2; }
QPushButton {
    background: #202c48; color: #eef4ff; border: 1px solid #354563;
    border-radius: 8px; padding: 9px 15px; min-height: 20px;
}
QPushButton:hover { background: #293956; }
QPushButton:disabled { color: #69758c; background: #151d30; border-color: #263149; }
QPushButton#primaryAction { background: #2563dc; border-color: #3476ef; font-weight: 700; }
QPushButton#primaryAction:hover { background: #3273ea; }
QPushButton#dangerAction { background: #51212a; border-color: #7c3441; }
QPushButton#dangerAction:hover { background: #652936; }
QProgressBar {
    border: 1px solid #33415f; border-radius: 7px; background: #10192d;
    text-align: center; min-height: 18px;
}
QProgressBar::chunk { background: #3973e6; border-radius: 6px; }
QMessageBox { background: #0b1224; }

/* Phase 9.6.2 flash workflow hierarchy */
QLabel#sectionLabel { color: #7895cf; font-size: 11px; font-weight: 800; padding-top: 10px; padding-bottom: 2px; }
QLabel#compatibilityPanel { background: #10192d; border: 1px solid #2d3b59; border-radius: 8px; padding: 10px; color: #cbd7eb; }
QLabel#stageStatus { background: #0f1729; border-left: 3px solid #3973e6; padding: 8px 10px; color: #b9c8e2; }
QLineEdit#eraseConfirmation { border: 1px solid #6e3944; }
QLineEdit#eraseConfirmation:focus { border: 1px solid #b24b5e; }

"""
