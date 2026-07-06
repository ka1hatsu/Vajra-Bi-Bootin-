# Phase 8.2 — Recommendation-to-Download-to-Flash Workflow Foundation

Adds:
- validated downloaded-image handoff objects;
- a controller joining recommended/manual distro selection to the catalog
  downloader;
- verified local image callback after download;
- tests for missing files and invalid extensions;
- an inspection script for matching the final GUI navigation hooks to the
  current customized MainWindow and FlashDialog.

The final two UI hooks are intentionally not guessed: existing Vajra revisions
have different recommendation-card methods and FlashDialog image-field names.
Run inspect_phase82.sh after applying and use its output for the final direct
patch.
