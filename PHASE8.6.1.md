# Phase 8.6.1 — Verification Gate UI Wiring

The resolved-download completion path now evaluates the trusted upstream digest
against the locally calculated digest before emitting `image_ready`.

Only a `verified` policy decision reaches the existing FlashDialog handoff.
Missing upstream metadata, malformed metadata, pending verification, and checksum
mismatch remain blocked.

The downloader's existing checksum rejection remains in place, so this adds a
second explicit policy gate at the UI handoff boundary.
