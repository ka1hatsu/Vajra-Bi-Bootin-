# Phase 6 — Preflight Revalidation and Safer Write Sessions

This overlay adds:

- immutable target identity snapshots;
- immediate target revalidation before destructive operations;
- serial-number and capacity mismatch detection;
- image-size rechecking;
- an unmount helper foundation;
- tests for target identity snapshots.

This package is intentionally an overlay and does not replace `main_window.py`,
`flash_dialog.py`, `scanner.py`, or earlier user fixes.

The next integration step is to wire `TargetIdentity` and `revalidate_target`
into the final confirmation-to-write transition, then introduce a narrowly
scoped privileged helper instead of running the entire GUI as root.
