#!/bin/sh
set -eu

echo "=== Main window classes and methods ==="
grep -nE '^(class |    def )' vajra/ui/main_window.py || true

echo
echo "=== Recommendation-related lines ==="
grep -nEi 'recommend|distro|linux|download' vajra/ui/main_window.py || true

echo
echo "=== Flash dialog constructor and image field ==="
grep -nE 'class FlashDialog|def __init__|QLineEdit|image|iso' \
  vajra/ui/flash_dialog.py | head -80 || true
