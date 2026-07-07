# Phase 9.5.1 — Complete Verified Handoff Wiring

Completes SHA-256 propagation from verified download through ImageHandoff and
MainWindow into FlashDialog. Direct resolved downloads and resumed downloads use
the digest-aware signal. CatalogDownloadDialog gains a digest-aware signal while
retaining its legacy path-only signal for compatibility.
