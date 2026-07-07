from pathlib import Path

def test_report_dialog_exists():
    t=Path("vajra/ui/operation_report_dialog.py").read_text()
    assert "class OperationReportDialog" in t
    assert "def build_operations(self):" in t
    assert "Recovery assessment:" in t

def test_main_window_wires_reports():
    t=Path("vajra/ui/main_window.py").read_text()
    assert "OperationReportDialog" in t
    assert "def open_operation_reports(self):" in t
    assert 'QPushButton("Operation Reports")' in t
