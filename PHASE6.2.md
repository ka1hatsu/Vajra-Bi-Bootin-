# Phase 6.2 — Privileged Writer Helper

Adds a narrowly scoped writer-helper foundation. The helper independently:

- requires root execution;
- verifies the image exists;
- rediscovers the target;
- rejects ineligible, system, and read-only devices;
- compares serial number and capacity;
- checks image size;
- unmounts mounted child partitions;
- revalidates the target again after unmount and immediately before writing;
- emits JSON-line progress events.

The GUI should invoke this helper through `pkexec` and parse its JSON-line stdout.
This overlay does not install a permissive polkit policy and does not make anything setuid.

Before production packaging, install the Python package into a fixed system location and use an absolute helper path controlled by the package manager.
