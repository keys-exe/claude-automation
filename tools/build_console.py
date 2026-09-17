"""Inline strings.json into the console source.

The published page must be self-contained — the Artifact CSP blocks runtime fetches — so
the string library is injected at build time rather than loaded. Edit `console.src.html`;
`console.html` is generated and overwritten.
"""

from __future__ import annotations

from pathlib import Path

PLACEHOLDER = "/*STRINGS_JSON*/null"


def main() -> int:
    web = Path(__file__).resolve().parents[1] / "web"
    source = (web / "console.src.html").read_text(encoding="utf-8")
    if PLACEHOLDER not in source:
        raise SystemExit(f"{PLACEHOLDER} not found in console.src.html")
    data = (web / "strings.json").read_text(encoding="utf-8").strip()
    output = source.replace(PLACEHOLDER, data)
    target = web / "console.html"
    target.write_text(output, encoding="utf-8")
    print(f"{target} ({target.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
