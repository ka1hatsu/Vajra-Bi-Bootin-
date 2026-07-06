# Phase 8.7 — Download and Flash Workflow UX

Adds explicit workflow states to the resolved ISO download dialog:

- resolving
- ready
- downloading
- verifying
- verified
- failed
- cancelled
- cancelling

The phase also prevents duplicate download starts, makes failure/cancellation
recoverable through Retry Download, keeps resumable `.part` behavior, and
preserves the Phase 8.6.1 verification gate before `image_ready` handoff.

No flashing safety checks are removed or bypassed.
