#!/usr/bin/env bash
# Package Vespergard as a standalone game (no Godot needed to PLAY it).
#
# One-time setup on your machine (needs godot 4.7 + internet):
#   godot --headless --install-export-templates            # 4.3+; or:
#   Editor > Manage Export Templates > Download and Install
#
# Then:
#   tools/export.sh            # builds Linux + Windows into build/
#   tools/export.sh Linux      # just one preset
#
# The result is a single self-contained executable per platform (the .pck is
# embedded). Zip it, send it to a friend, they double-click it. Saves land in
# the platform's user:// dir, not next to the exe.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build
presets=("$@")
[ ${#presets[@]} -eq 0 ] && presets=("Linux" "Windows")
for p in "${presets[@]}"; do
  echo "== exporting $p"
  godot --headless --export-release "$p" 2>&1 | tail -3
done
ls -la build/
