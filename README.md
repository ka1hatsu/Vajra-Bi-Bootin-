# Vajra Bi-Bootin

Vajra Bi-Bootin is a Linux desktop utility that helps people choose a distribution for their hardware, download an official image, verify it, and prepare bootable USB media from one application.

The project started as a hardware-aware distro recommender and gradually grew into a complete download and USB preparation workflow. The recommendation engine is deterministic: hardware compatibility is checked first, then suitable distributions are ranked using the user's intended use and experience level.

## What it does

- Scans CPU architecture, memory, graphics, storage and firmware information locally.
- Filters out distributions that do not match the detected architecture.
- Ranks compatible Linux distributions and explains the recommendation.
- Resolves current ISO releases from supported official sources.
- Downloads large images with progress reporting, cancellation and resume support.
- Verifies downloaded images with SHA-256 when a trusted checksum is available.
- Keeps download history so completed images can be reused.
- Detects eligible removable USB devices and blocks system disks and read-only targets.
- Checks image size, target capacity and device identity before a write begins.
- Supports raw image writing and prepared-media workflows where the selected image and configuration allow them.
- Verifies written data after the operation and records operation status for recovery guidance.

## Current status

Vajra is under active development. The core recommendation, download, verification and USB workflow is implemented, but the project should still be treated as pre-release software. USB writing is a destructive operation, so test changes with disposable media before relying on them for important data.

The application currently targets Linux. Some parts of the media preparation pipeline depend on common system tools and `pkexec` for the narrowly scoped privileged helper.

## Requirements

- Python 3.10 or newer
- Linux
- PySide6
- `lsblk` and other standard Linux storage utilities
- `pkexec` for operations that require elevated access

Additional media tools may be required for some prepared-media workflows. The application checks backend availability before starting those operations.

## Installation

Clone the repository and create a virtual environment:

```bash
git clone <repository-url>
cd Vajra-Bi-Bootin-
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the application with:

```bash
python main.py
```

## Running the tests

Install pytest in the virtual environment if it is not already available, then run the complete suite:

```bash
pip install pytest
python -m pytest tests/ -q
```

For a quick syntax check of the application package:

```bash
python -m compileall -q vajra
```

## How the workflow is organised

The source is split by responsibility rather than by UI screen:

- `vajra/hardware/` collects local hardware information.
- `vajra/catalog/` loads distribution metadata.
- `vajra/recommender/` filters and ranks distributions.
- `vajra/sources/` resolves release images and validates download sources.
- `vajra/downloader/` handles image downloads and checksum work.
- `vajra/verification/` contains verification policy decisions.
- `vajra/workflow/` carries trusted state between download and USB preparation.
- `vajra/writer/` contains device discovery, preflight checks, the privileged helper protocol and write verification.
- `vajra/boot/` analyses images and plans prepared-media operations.
- `vajra/ui/` contains the PySide6 interface.

A verified download carries its digest into the USB workflow. Before the operation begins, the application checks the image again and revalidates the selected device. The privileged helper independently checks the target identity before touching the device. These checks are intentionally repeated at different boundaries.

## Safety notes

Writing an image to a USB device erases data on the selected target. Vajra uses several safeguards, including removable-device eligibility checks, system-disk blocking, an explicit `ERASE` confirmation, a final device summary, capacity checks and target identity revalidation.

Those safeguards reduce mistakes, but they do not replace checking the selected device yourself. Keep backups of anything important and avoid testing development builds with storage that contains valuable data.

## Contributing

Bug reports and small, focused pull requests are welcome. If you are changing the download or USB workflow, please include tests for the behavior you changed and run the full suite before submitting the change.

For larger changes, open an issue first so the design can be discussed before code is written. In particular, changes around device detection, privilege boundaries, cancellation and verification should be kept small and easy to review.

## License

A license file has not been added yet. Until one is chosen, the repository is publicly visible but should not be assumed to grant open-source redistribution rights.