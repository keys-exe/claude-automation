---
description: Look up locked strings from Appendix A
argument-hint: [STRING-ID or search term]
---
If $1 is a string ID, run `pe string $1` and print it verbatim in a fenced block with its
declared and filled character counts.

Otherwise run `pe strings` and filter for $1, showing ID, section, count and description.
Never paraphrase a NORMATIVE block — paste it.
