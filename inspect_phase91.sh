#!/usr/bin/env bash

echo "=== FLASH DIALOG ==="
sed -n '1,280p' vajra/ui/flash_dialog.py

echo
echo "=== FLASH WRITER ==="
sed -n '1,260p' vajra/writer/flash.py

echo
echo "=== HELPER CLIENT ==="
sed -n '1,260p' vajra/writer/helper_client.py

echo
echo "=== PREFLIGHT ==="
sed -n '1,280p' vajra/writer/preflight.py

echo
echo "=== WRITER FILES ==="
find vajra/writer -maxdepth 2 -type f | sort
