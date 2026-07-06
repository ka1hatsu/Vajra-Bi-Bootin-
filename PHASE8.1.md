# Phase 8.1 — Catalog Download Integration

Adds:
- tolerant adapter for several distros.json shapes;
- catalog-backed distro chooser;
- resumable downloader integration;
- checksum handoff to the Phase 8 downloader;
- image_ready(path) signal after successful download and verification;
- preselection support for recommendation-driven flows.

The dialog is intentionally not blindly injected into customized MainWindow
layouts. It can be opened with CatalogDownloadDialog(self), and image_ready can
be connected to the existing ISO path field or flash workflow.
