from pathlib import Path


def test_managed_runner_uses_process_group():
    t = Path("vajra/boot/process_runner.py").read_text()
    assert "start_new_session=True" in t
    assert "os.killpg" in t
    assert "signal.SIGTERM" in t
    assert "signal.SIGKILL" in t


def test_prepared_helper_cancellation_contract():
    t = Path("vajra/boot/prepared_helper.py").read_text()
    assert "cancel_check=None" in t
    assert "run_managed" in t
    assert "cancel_check=cancel_check" in t


def test_helper_handles_termination():
    t = Path("vajra/writer/helper.py").read_text()
    assert "signal.signal(signal.SIGTERM, request_cancel)" in t
    assert "cancel_check=cancel_requested" in t


def test_wim_split_is_managed():
    t = Path("vajra/boot/windows_media.py").read_text()
    assert "run_managed(" in t
    assert "cancel_check=cancel_check" in t
