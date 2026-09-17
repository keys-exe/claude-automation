"""Parse the Global Standards document into machine-readable form.

The Standards are the source of truth (Order of Authority, §0). Nothing in this
package restates a rule; every threshold is read off the document or off the
Appendix E tables reproduced in `tables.py` with their section reference.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

HEADER_RE = re.compile(r"^\*\*`(?P<id>[A-Z0-9][A-Z0-9\-]*(?:\[[A-Z\-]+\])?)`\*\*(?P<rest>.*)$")
FENCE_RE = re.compile(r"^```")
PAREN_RE = re.compile(r"\(([^()]*)\)")
COUNT_RE = re.compile(r"^(?P<lo>[0-9][0-9,]*)(?:\s*[–-]\s*(?P<hi>[0-9][0-9,]*))?(?P<note>.*)$")
SLOT_RE = re.compile(r"\[(?P<slot>[A-Z][A-Z0-9 \-/]*)\]")
HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*$")
VERSION_RE = re.compile(r"\*\*Version\s+(?P<version>[0-9][0-9.]*)\b")


def _int(text: str) -> int:
    return int(text.replace(",", ""))


@dataclass(frozen=True)
class Block:
    """One Appendix A string: an ID, its declared count, and its body."""

    id: str
    body: str
    declared_lo: int
    declared_hi: int
    note: str
    section: str
    line: int
    description: str

    @property
    def is_pattern(self) -> bool:
        """A PATTERN carries slot tokens; its count is 'as template'."""
        return bool(SLOT_RE.search(self.body)) or "template" in self.note

    @property
    def slots(self) -> list[str]:
        seen: list[str] = []
        for match in SLOT_RE.finditer(self.body):
            slot = match.group("slot")
            if slot not in seen:
                seen.append(slot)
        return seen

    @property
    def actual(self) -> int:
        """Counts are measured on the minified string (§37)."""
        return len(minify(self.body))

    def count_ok(self) -> bool:
        """Declared count matches the body as written (§E10 doc-lint)."""
        if self.declared_hi != self.declared_lo:
            return self.declared_lo <= self.actual <= self.declared_hi
        return self.actual == self.declared_lo


@dataclass
class Section:
    number: str
    title: str
    line: int
    level: int


@dataclass
class Standards:
    path: Path
    version: str
    text: str
    blocks: dict[str, Block] = field(default_factory=dict)
    sections: list[Section] = field(default_factory=list)

    def block(self, block_id: str) -> Block:
        try:
            return self.blocks[block_id]
        except KeyError:
            raise KeyError(
                f"no Appendix A string {block_id!r} in {self.path.name} "
                f"(v{self.version}); if a rule is not here, it does not exist"
            ) from None

    def block_ids(self) -> list[str]:
        return sorted(self.blocks)

    def has_section(self, number: str) -> bool:
        return any(s.number == number for s in self.sections)


def minify(text: str) -> str:
    """Counts are measured on the minified string — newlines count (§37)."""
    return " ".join(text.split())


def default_path() -> Path:
    """The vendored Standards, or $PROMPTPIPE_STANDARDS if the user points elsewhere."""
    override = os.environ.get("PROMPTPIPE_STANDARDS")
    if override:
        return Path(override).expanduser().resolve()
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "standards" / "CURRENT.md"
        if candidate.exists():
            return candidate.resolve()
    raise FileNotFoundError("no standards/CURRENT.md found; set PROMPTPIPE_STANDARDS")


def parse(path: Path | str | None = None) -> Standards:
    path = Path(path) if path else default_path()
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    version_match = VERSION_RE.search(text)
    standards = Standards(
        path=path,
        version=version_match.group("version") if version_match else "unknown",
        text=text,
    )

    current_section = ""
    index = 0
    while index < len(lines):
        line = lines[index]

        heading = HEADING_RE.match(line)
        if heading and not line.startswith("#####"):
            title = heading.group("title")
            number = _section_number(title)
            standards.sections.append(
                Section(
                    number=number,
                    title=_strip_markup(title),
                    line=index + 1,
                    level=len(heading.group("hashes")),
                )
            )
            if number:
                current_section = number

        header = HEADER_RE.match(line)
        if header:
            block, consumed = _read_block(lines, index, header, current_section)
            if block is not None:
                # A repeated ID is a doc-lint failure, not a silent overwrite.
                if block.id in standards.blocks:
                    standards.blocks[block.id] = standards.blocks[block.id]
                else:
                    standards.blocks[block.id] = block
                index += consumed
                continue

        index += 1

    return standards


def _read_block(
    lines: list[str], index: int, header: re.Match, section: str
) -> tuple[Block | None, int]:
    rest = header.group("rest")
    parentheticals = PAREN_RE.findall(rest)
    count = None
    for body in reversed(parentheticals):
        match = COUNT_RE.match(body.strip())
        if match:
            count = match
            break
    if count is None:
        return None, 1

    cursor = index + 1
    # The fenced body follows the header, possibly after prose lines.
    while cursor < len(lines):
        line = lines[cursor]
        if FENCE_RE.match(line):
            break
        if HEADER_RE.match(line) or HEADING_RE.match(line):
            return None, 1
        cursor += 1
    if cursor >= len(lines):
        return None, 1

    body_start = cursor + 1
    cursor = body_start
    while cursor < len(lines) and not FENCE_RE.match(lines[cursor]):
        cursor += 1
    body = "\n".join(lines[body_start:cursor])

    lo = _int(count.group("lo"))
    hi = _int(count.group("hi")) if count.group("hi") else lo
    block = Block(
        id=header.group("id"),
        body=body,
        declared_lo=lo,
        declared_hi=hi,
        note=count.group("note").strip(),
        section=section,
        line=index + 1,
        description=_strip_markup(rest.lstrip(" —-")),
    )
    return block, (cursor + 1) - index


def _section_number(title: str) -> str:
    match = re.match(r"^(?P<num>[0-9]+[A-Z]?)\.\s", title)
    if match:
        return match.group("num")
    appendix = re.match(r"^APPENDIX\s+(?P<letter>[A-Z])\b", title)
    if appendix:
        return f"App.{appendix.group('letter')}"
    return ""


def _strip_markup(text: str) -> str:
    text = re.sub(r"\*\(([^)]*)\)\*", r"(\1)", text)
    text = text.replace("**", "").replace("`", "")
    return text.strip()


@lru_cache(maxsize=4)
def load(path: str | None = None) -> Standards:
    """Cached parse — the Standards do not change inside one run."""
    return parse(path)
