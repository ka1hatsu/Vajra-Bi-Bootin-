#!/usr/bin/env bash

echo "=== RESOLVED DOWNLOAD DIALOG ==="
sed -n '1,320p' vajra/ui/resolved_download_dialog.py

echo
echo "=== DOWNLOAD WORKFLOW FILES ==="
find vajra -maxdepth 3 -type f | grep -E 'download|checksum|verification|flow' | sort

echo
echo "=== CHECKSUM REFERENCES ==="
grep -RniE \
  "sha256|checksum|completed|download_complete|FlashDialog|open_flash" \
  vajra/ui vajra/workflow vajra/downloader 2>/dev/null
