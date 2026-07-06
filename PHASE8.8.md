# Phase 8.8 — Persistent Download History Core

Adds an atomic JSON-backed download history and a lifecycle session model.

Stored metadata includes distro, version, architecture, destination path, source
URL, trusted expected SHA-256, calculated SHA-256, workflow state, progress, and
update time.

The history can identify:
- recent downloads;
- verified ISO files that still exist;
- interrupted downloads with an existing `.part` file.

This phase intentionally adds the persistence core without guessing at current
main-window layout. The next UI wiring can expose Download History, Resume, and
Flash Again actions against this stable API.
