# Phase 6.3
Connects the unprivileged GUI to the independently validating writer helper through pkexec and QProcess JSON-line progress events. Development uses the repository helper path. Production packaging should use fixed root-owned paths and a restrictive polkit policy. Never make the helper setuid.
