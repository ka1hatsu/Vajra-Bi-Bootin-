# Phase 9.5 — End-to-End Workflow Session

Adds a workflow session model and stale-image protection. Verified image metadata
can travel with the workflow, and FlashDialog can enforce the verified SHA-256
again immediately before privileged helper creation. The existing path-only
image_ready signal remains for compatibility.
