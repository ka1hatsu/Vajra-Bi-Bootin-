# Phase 7.4
Adds a privileged prepared-media transaction: approved plan handoff, GPT/MBR creation, FAT32 formatting, ISO extraction, sync/unmount, and GUI progress events.

Limitations: FAT32 has a 4 GiB per-file limit. Windows installation media and universal BIOS bootloader installation require dedicated later backends. Plain extraction is not guaranteed to make every ISO bootable.
