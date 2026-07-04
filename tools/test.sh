#!/usr/bin/env bash
# Headless test runner. Runs every in-game test (tools/test/*_test.tscn)
# through the real boot path so autoloads and physics are live.
set -uo pipefail
cd "$(dirname "$0")/.."
FILTER="${1:-}"
overall=0
# refresh imports + global class cache (new class_name scripts)
timeout 300 godot --headless --path . --import >/dev/null 2>&1
for scene in tools/test/*_test.tscn; do
  name="$(basename "$scene" _test.tscn)"
  if [ -n "$FILTER" ] && [ "$name" != "$FILTER" ]; then continue; fi
  echo "=== test: $name"
  timeout 300 godot --headless --path . -- "--test=$name" 2>&1 \
    | grep -vE "ALSA|snd_|libpulse|Condition \"status|dummy driver|Godot Engine|^\s*$" \
    | grep -vE "at: (init_output_device|push_warning)"
  code=${PIPESTATUS[0]}
  if [ "$code" -ne 0 ]; then
    echo "!!! $name exited $code"
    overall=1
  fi
done
exit $overall
