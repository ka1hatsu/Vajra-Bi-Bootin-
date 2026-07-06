# Phase 7.2 — Boot Compatibility Engine

Adds a deterministic compatibility engine for image type, GPT/MBR, UEFI/Legacy and filesystem combinations. The GUI shows Compatible, Warning or Blocked guidance and suggested settings. Incompatible combinations are blocked before the destructive flow.

This phase does not yet create custom partition tables or filesystems; Phase 7.3 supplies preparation backends.
