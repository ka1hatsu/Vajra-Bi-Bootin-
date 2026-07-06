# Phase 8.8.1 — History UI and Session Wiring

Adds:
- DownloadSession lifecycle persistence in ResolvedDownloadDialog.
- Download History dialog.
- Verified-file detection.
- Flash Again for verified ISO files that still exist.
- Resume visibility for interrupted downloads with `.part` files.
- Main-window history entry and verified-image FlashDialog handoff.

Resume intentionally reuses the existing downloader's `.part` behavior instead
of creating a second download implementation.
