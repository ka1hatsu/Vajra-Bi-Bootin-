# Phase 6.1

Adds partition-aware unmounting and a privilege-boundary foundation. The full GUI should not run as root. A future narrowly scoped privileged helper must independently revalidate the target before raw writing.

Apply with:

    python3 apply_phase61.py
    python -m pytest -v

Remove apply_phase61.py after successful application if desired.
