# Phase 9.0 — Download Reliability Baseline

Adds regression protection for large ISO byte counters and safe active-download
thread shutdown when the dialog closes. This prevents the observed signed
32-bit Qt overflow from returning and reduces QThread destruction crashes.
