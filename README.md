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
