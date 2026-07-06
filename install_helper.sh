#!/bin/sh
set -eu

PREFIX="${PREFIX:-/usr/local/libexec/vajra-bi-bootin}"
mkdir -p "$PREFIX"
install -m 0755 vajra/writer/helper.py "$PREFIX/vajra-writer-helper"

echo "Installed helper at $PREFIX/vajra-writer-helper"
echo "Note: Python package import paths and polkit policy packaging must be finalized for distro packages."
