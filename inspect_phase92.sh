#!/usr/bin/env bash

echo "=== HELPER ==="
sed -n '1,360p' vajra/writer/helper.py

echo
echo "=== PREPARED HELPER ==="
sed -n '1,420p' vajra/boot/prepared_helper.py

echo
echo "=== WINDOWS MEDIA ==="
sed -n '1,320p' vajra/boot/windows_media.py

echo
echo "=== SUBPROCESS USAGE ==="
grep -RniE \
"subprocess|Popen|run\\(|check_call|check_output|terminate|kill|mount|umount|udisksctl" \
vajra/writer \
vajra/boot
