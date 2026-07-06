# Vajra Bi (Bootin)

AI-assisted Linux distribution recommendation and bootable-media utility.

## Phase 1

This prototype:
- scans CPU, architecture, RAM, GPU, disk space, firmware mode, and Secure Boot status;
- loads a local Linux distribution catalog;
- filters incompatible choices;
- scores compatible distributions;
- prints recommendations and official download pages.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

On Windows, activate with:

```powershell
.venv\Scripts\Activate.ps1
```

## Test

```bash
pip install pytest
pytest
```

> The distro catalog is starter data for the prototype. Hardware requirements and boot support should be verified against official distro documentation before release.


## Phase 2 GUI

Install dependencies and launch:

```bash
pip install -r requirements.txt
python main.py
```

The desktop GUI provides:
- welcome screen;
- background hardware scan;
- hardware summary cards;
- usage and experience preferences;
- ranked Linux recommendations;
- recommendation reasons;
- buttons that open official distro download pages.

The recommendation engine remains deterministic. The current GUI does not write USB drives yet.
\n\n## Phase 3\nAdds streamed image downloads, progress, cancellation, `.part` cleanup, SHA-256 verification, a GUI Download Center, and checksum tests.\n

## Phase 3.1: Optional AI path and manual distro choice

The home workflow now supports:
- Smart Recommendation: scan hardware and rank compatible distros.
- Choose Linux Myself: search and browse the distro catalog without AI.
- Download Center: use a valid direct ISO/image URL and optionally verify SHA-256.

The manual path never requires accepting an AI recommendation. Hard compatibility checks should warn about genuine architecture incompatibility, but ordinary preference choices remain with the user.

This merge package intentionally omits `vajra/hardware/scanner.py` so a locally improved scanner is not overwritten.


## Phase 4: USB detection and safety layer

Phase 4 adds Linux block-device discovery using `lsblk`, removable/USB eligibility checks,
root/system-disk blocking, read-only-device blocking, model/capacity/transport/mountpoint display,
refresh support, and a GUI safety-check dialog.

**Phase 4 is detection-only. It does not write, erase, format, mount, or unmount drives.**
Actual image writing belongs to a later phase after additional safeguards and testing.

The merge package continues to omit `vajra/hardware/scanner.py`, preserving the user's improved scanner.
\n\n## Phase 5\nAdds guarded ISO/IMG writing, image/device size checks, explicit ERASE confirmation, final device identity confirmation, progress, cancellation requests, fsync, and post-write byte-range SHA-256 verification. Raw device access may require privileges; production packaging should use a narrowly scoped privileged helper rather than running the full GUI as root.\n
## Phase 5: USB image writing and post-write verification

Phase 5 adds the guarded USB image-writing pipeline:

- ISO and IMG file selection.
- Eligible removable USB device selection.
- Image-size and target-capacity validation.
- Mandatory `ERASE` confirmation before writing.
- Final destructive-action confirmation showing the exact device path, model, capacity, and selected image.
- Chunked raw image writing with progress reporting.
- Cooperative cancellation support during writing and verification.
- `fsync` before reporting write completion.
- Post-write SHA-256 verification of the written image data.
- Protection inherited from Phase 4 against system disks, read-only devices, and ineligible storage devices.

> **Warning:** Writing an image destroys existing data on the selected target device. Vajra performs multiple checks and confirmations, but users should still verify the exact target device before approving the operation.

### Phase 5 fixes

The following fixes were added after the initial Phase 5 implementation:

- Fixed cancellation during the verification stage.
- Improved cancellation responsiveness.
- Fixed the `QDialog.done()` method-name collision in the PySide6 flash dialog.
- Added a Back button from the Hardware Detected page to the Welcome page.

