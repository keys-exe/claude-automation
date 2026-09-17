#!/usr/bin/env bash
# Gate any beat prompt the moment it is written (§37, §28H, E1, E5).
# Reads the PostToolUse payload on stdin; stays silent unless a beat file changed.
set -uo pipefail

payload=$(cat)
path=$(printf '%s' "$payload" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
tool = data.get("tool_input") or {}
print(tool.get("file_path") or "")
' 2>/dev/null)

case "$path" in
  */beats/*.t2i.txt|*/beats/*.i2v.json) ;;
  *) exit 0 ;;
esac

build_dir=$(dirname "$(dirname "$path")")
beat_id=$(basename "$path" | sed -E 's/\.(t2i\.txt|i2v\.json)$//')

command -v pe >/dev/null 2>&1 || exit 0
output=$(pe --build "$build_dir" check "$beat_id" 2>&1) || {
  printf 'Beat gates failed for %s (§18 step 7 — fix before generating):\n%s\n' "$beat_id" "$output" >&2
  exit 2
}
exit 0
