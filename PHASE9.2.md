# Phase 9.2 — Privileged Helper Process Safety

Adds managed subprocess process groups for prepared-media commands.

Cancellation is propagated from SIGTERM/SIGINT in the privileged helper into
partitioning, formatting, extraction, copying, syncing, and Windows WIM
splitting. Managed commands receive SIGTERM as a process group and escalate to
SIGKILL after a bounded wait when necessary. Existing finally-based unmount
cleanup remains intact.
