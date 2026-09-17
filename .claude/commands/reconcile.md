---
description: §27B coverage audit and the reconciliation line for the current build
---
Run `pe coverage`.

Print the reconciliation line exactly as the tool produces it — phrase range → beat count,
merges by ID, TH-carried by ID, uncovered count, blocked count, unpaid plants.

Uncovered must read zero. If it does not, the act is undelivered: say so and list the
uncovered phrase IDs. Blocked rows are reported, never resolved.
