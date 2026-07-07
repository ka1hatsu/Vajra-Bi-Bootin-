#!/usr/bin/env bash

echo "=== RECOMMENDATION DOWNLOAD FLOW ==="
sed -n '1,360p' vajra/workflow/recommendation_download.py

echo
echo "=== RESOLVED DOWNLOAD DIALOG ==="
sed -n '1,300p' vajra/ui/resolved_download_dialog.py

echo
echo "=== FLASH DIALOG ==="
sed -n '1,320p' vajra/ui/flash_dialog.py

echo
echo "=== SESSION FILES ==="
find vajra -type f | grep -Ei 'session|workflow|history' | sort

echo
echo "=== IMAGE READY / FLASH HANDOFF ==="
grep -RniE \
'image_ready|FlashDialog|verified|sha256|workflow_state|RecommendationDownloadFlow' \
vajra/ui vajra/workflow vajra/writer
