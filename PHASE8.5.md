# Phase 8.5 — Dedicated Mint, MX and Fedora Resolvers

Adds distribution-specific resolver classes for Linux Mint Xfce, MX Linux Xfce,
and Fedora Workstation. Mint discovers stable versions from the Kernel.org Mint
mirror and reads sha256sum.txt. Fedora discovers release ISO directories and
parses Fedora CHECKSUM syntax. MX uses SourceForge release metadata and fails
closed if the returned latest release is not an Xfce ISO.

The existing UI fallback remains active when a provider changes its metadata or
a compatible direct image cannot be resolved.
