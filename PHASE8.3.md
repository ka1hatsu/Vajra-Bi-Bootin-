# Phase 8.3 — Dynamic Official ISO Resolver

This phase adds a network resolver layer rather than hard-coded release URLs.

Features:
- architecture normalization (amd64/i386/arm64 aliases);
- resolver registry;
- dynamic Lubuntu release discovery from Ubuntu cdimage indexes;
- SHA256SUMS parsing and checksum attachment;
- conservative official-page ISO discovery adapters;
- HTTPS and download-host validation;
- bounded network responses and timeouts;
- one-hour resolver cache;
- background Qt resolver worker;
- unit tests for architecture, checksums, and source security.

The Lubuntu resolver is fully dynamic. Generic page adapters deliberately fail
closed when an official page does not expose a direct compatible ISO link.
They do not guess filenames or convert HTML pages into ISO URLs.

Run inspect_phase83.py after installation. The next UI patch should use the
actual hardware architecture field and catalog IDs printed by that script.
