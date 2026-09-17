#!/bin/bash
# Make `pe` available in a fresh Claude Code on the web container.
# The container is ephemeral and the repo is cloned fresh each session, so the
# editable install has to happen here or every `pe` command fails.
set -euo pipefail

# Local machines keep their own environment; only the remote container needs this.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

python3 -m pip install --quiet --root-user-action=ignore -e . pytest

# `pe` reads the Standards from the repo unless the user points it elsewhere.
echo "export PROMPTPIPE_STANDARDS=\"$CLAUDE_PROJECT_DIR/standards/CURRENT.md\"" >> "$CLAUDE_ENV_FILE"

echo "promptpipe installed — \`pe status\`, \`pe lint\`, \`pe check <BEAT-ID>\` are ready."
