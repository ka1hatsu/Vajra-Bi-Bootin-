import os
import signal
import subprocess
import tempfile


class ManagedCommandError(RuntimeError):
    pass


def run_managed(cmd, input_text=None, cancel_check=None, poll_interval=0.1):
    # Long-running tools such as 7z can produce more output than an OS pipe can
    # hold. Spool output to temporary files so the child can never block waiting
    # for this polling loop to drain stdout or stderr.
    with tempfile.TemporaryFile(mode="w+t") as stdout_file, tempfile.TemporaryFile(mode="w+t") as stderr_file:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE if input_text is not None else None,
            stdout=stdout_file,
            stderr=stderr_file,
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

        stdout_file.seek(0)
        stderr_file.seek(0)
        stdout = stdout_file.read()
        stderr = stderr_file.read()

        if proc.returncode:
            raise ManagedCommandError(
                stderr.strip() or stdout.strip() or "Command failed"
            )

        return subprocess.CompletedProcess(
            cmd, proc.returncode, stdout, stderr
        )
