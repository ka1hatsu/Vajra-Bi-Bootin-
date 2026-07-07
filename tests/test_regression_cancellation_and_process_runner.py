import sys

import pytest

from vajra.boot.process_runner import ManagedCommandError, run_managed
from vajra.writer import flash
from vajra.writer import verify


def test_raw_writer_honors_cancellation_before_first_write(tmp_path):
    image = tmp_path / "image.img"
    target = tmp_path / "target.img"
    image.write_bytes(b"x" * 4096)

    with pytest.raises(flash.FlashCancelled):
        flash.write_image(
            image,
            target,
            cancel_check=lambda: True,
            chunk_size=512,
        )

    assert target.read_bytes() == b""


def test_verifier_honors_cancellation(tmp_path):
    image = tmp_path / "image.img"
    target = tmp_path / "target.img"
    payload = b"vajra" * 1024
    image.write_bytes(payload)
    target.write_bytes(payload)

    with pytest.raises(verify.VerificationCancelled):
        verify.verify_written_image(
            image,
            target,
            cancel_check=lambda: True,
        )


def test_managed_command_handles_output_larger_than_pipe_buffer():
    size = 2 * 1024 * 1024
    command = [
        sys.executable,
        "-c",
        f"import sys; sys.stdout.write('x' * {size}); sys.stderr.write('y' * {size})",
    ]

    result = run_managed(command, poll_interval=0.01)

    assert result.returncode == 0
    assert len(result.stdout) == size
    assert len(result.stderr) == size


def test_managed_command_reports_nonzero_output():
    command = [
        sys.executable,
        "-c",
        "import sys; sys.stderr.write('expected failure'); raise SystemExit(7)",
    ]

    with pytest.raises(ManagedCommandError, match="expected failure"):
        run_managed(command, poll_interval=0.01)
