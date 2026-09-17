"""Export the Appendix A string library as JSON for the web console.

The console cannot run Python, so the strings ship with it. This script is the
only thing that writes web/strings.json — regenerate it after a Standards cut,
never hand-edit it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from promptpipe import standards  # noqa: E402
from promptpipe.tables import NEVER_TRIMMED, SLOT_SOURCES  # noqa: E402


def main() -> int:
    doc = standards.parse()
    payload = {
        "version": doc.version,
        "source": doc.path.name,
        "slotSources": SLOT_SOURCES,
        "neverTrimmed": NEVER_TRIMMED,
        "strings": [
            {
                "id": block.id,
                "section": block.section,
                "description": block.description,
                "declared": block.declared_lo,
                "declaredHi": block.declared_hi,
                "note": block.note,
                "actual": block.actual,
                "countOk": block.count_ok(),
                "isPattern": block.is_pattern,
                "slots": block.slots,
                "body": block.body,
            }
            for block in sorted(doc.blocks.values(), key=lambda b: b.id)
        ],
    }
    target = Path(__file__).resolve().parents[1] / "web" / "strings.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                      encoding="utf-8")
    print(f"{len(payload['strings'])} strings -> {target} "
          f"({target.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
