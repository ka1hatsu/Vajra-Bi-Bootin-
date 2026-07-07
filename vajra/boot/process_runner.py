import os
import signal
import subprocess


class ManagedCommandError(RuntimeError):
    pass


def run_managed(cmd, input_text=None, cancel_check=None, poll_interval=0.1):
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE if input_text is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )

    if input_text is not None:
        proc.stdin.write(input_text)
        proc.stdin.close()

    while proc.poll() is None:
        if cancel_check and cancel_check():
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait()

            raise ManagedCommandError("Operation cancelled.")

        try:
            proc.wait(timeout=poll_interval)
        except subprocess.TimeoutExpired:
            pass

    stdout = proc.stdout.read() if proc.stdout else ""
    stderr = proc.stderr.read() if proc.stderr else ""

    if proc.returncode:
        raise ManagedCommandError(
            stderr.strip() or stdout.strip() or "Command failed"
        )

    return subprocess.CompletedProcess(
        cmd, proc.returncode, stdout, stderr
    )
