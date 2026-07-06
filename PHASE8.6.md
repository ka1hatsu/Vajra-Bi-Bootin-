# Phase 8.6 — Trusted Checksum Policy

This phase:

- resolves MX Linux Xfce's published `.iso.sha256` companion;
- rejects malformed or absent MX SHA-256 metadata;
- adds a central verification policy;
- distinguishes verified, pending, mismatch, malformed-metadata, and untrusted states;
- provides `require_verified_download()` as the gate for automatic flash handoff.

The policy intentionally fails closed. A locally calculated digest alone is not
treated as trusted verification unless it matches an upstream SHA-256 value.

The next UI wiring step can call `require_verified_download(expected, actual)`
before opening FlashDialog for an automatically downloaded image.
