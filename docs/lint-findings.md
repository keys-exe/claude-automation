# E10 doc-lint findings — V7.49.8

Computed by `pe lint` against `standards/CURRENT.md`. E10 says a cut failing lint does
not ship; these are the findings the shipped cut carries. They are reported, not fixed —
a count is corrected to the block it measures, and only its author knows whether the
block or the count is the one that drifted (§34).

**39 fail · 24 warn — a cut failing lint does not ship: this cut DOES NOT SHIP**

## Character-count drift (FAIL)

Every Appendix A string must carry a count that matches its block, measured on the
minified string (§37). These do not.

| line | string | declared | measured | delta |
|---|---|---|---|---|
| 4649 | `MOUNT-GEOM` | 806 | 805 | -1 |
| 4654 | `MOUNT-CLEAN` | 341 | 319 | -22 |
| 4659 | `MOUNT-PERSON` | 437 | 434 | -3 |
| 4664 | `NEG-MOUNT` | 492 | 442 | -50 |
| 4673 | `CAM-CCTV` | 348 | 362 | +14 |
| 4678 | `CAP-CCTV` | 613 | 614 | +1 |
| 4683 | `CCTV-FRAME` | 461 | 433 | -28 |
| 4688 | `CCTV-CORNER` | 398 | 387 | -11 |
| 4693 | `CCTV-DOOR` | 389 | 375 | -14 |
| 4698 | `CCTV-OVER` | 281 | 286 | +5 |
| 4703 | `CCTV-EAVE` | 349 | 334 | -15 |
| 4708 | `CCTV-BELL` | 392 | 386 | -6 |
| 4713 | `CCTV-NIGHT` | 327 | 323 | -4 |
| 4718 | `RIG-R7` | 556 | 536 | -20 |
| 4723 | `NEG-CCTV` | 735 | 656 | -79 |
| 5271 | `NEG-STRESS` | 486 | 528 | +42 |
| 5361 | `WARD-LINE` | 118 | 111 | -7 |
| 5426 | `SEAT-LOCK` | 818 | 820 | +2 |
| 5500 | `NEG-PHYS` | 513 | 472 | -41 |
| 5508 | `PHYS-FALL` | 412 | 343 | -69 |
| 5513 | `BREAK-CERAMIC` | 587 | 572 | -15 |
| 5518 | `BREAK-GLASS` | 520 | 458 | -62 |
| 5523 | `BREAK-PLASTIC` | 398 | 341 | -57 |
| 5528 | `BREAK-SOFT` | 377 | 326 | -51 |
| 5533 | `PHYS-SPILL` | 472 | 425 | -47 |
| 5538 | `PHYS-BREAK` | 566 | 446 | -120 |
| 5543 | `PHYS-BREAK-C` | 304 | 281 | -23 |
| 5548 | `HOLD-BREAK` | 479 | 458 | -21 |
| 5553 | `NEG-WARP-B` | 199 | 169 | -30 |
| 5559 | `NEG-BREAK` | 619 | 521 | -98 |
| 5615 | `MOUTH-A` | 706 | 700 | -6 |
| 5661 | `BREATH-A` | 178 | 176 | -2 |
| 5667 | `PACE-A` | 155 | 153 | -2 |
| 5681 | `SCENE-REF` | 355 | 351 | -4 |
| 5705 | `STAIR-DOWN` | 200 | 198 | -2 |
| 5711 | `STAIR-UP` | 183 | 181 | -2 |
| 5717 | `STAIR-EASE` | 386 | 384 | -2 |
| 5725 | `AFTER-EASE` | 211 | 209 | -2 |
| 5753 | `SUBJ-REF` | 230 | 226 | -4 |

## Slot tokens absent from the E5 manifest (WARN)

E10 requires every slot token to appear in the E5 slot-fill manifest, so that each has a
named source and a procedure. These tokens are live in Appendix A strings and have neither.

| string | token |
|---|---|
| `AVATAR-SHEET` | `[WOMAN/MAN]` |
| `AVATAR-SHEET` | `[WALL COLOUR]` |
| `AVATAR-SHEET` | `[FLOOR]` |
| `ANAT-ARC-SC` | `[PAIN BEHAVIOUR]` |
| `ANAT-ARC-SC` | `[RELIEF BEHAVIOUR]` |
| `WARD-LINE` | `[BASE]` |
| `WARD-LINE` | `[LOWER]` |
| `WARD-LINE` | `[FOOT]` |
| `DRAWER-FRAME` | `[CABINET FACE]` |
| `DRAWER-FRAME` | `[WORKTOP OR TOP]` |
| `DRAWER-HOME` | `[CABINET FACE]` |
| `PHYS-FALL` | `[SURFACE]` |
| `PHYS-FALL` | `[NAMED PART]` |
| `BREAK-CERAMIC` | `[NAMED PART]` |
| `PHYS-BREAK` | `[NAMED PART]` |
| `PHYS-BREAK` | `[SURFACE]` |
| `PHYS-BREAK-C` | `[NAMED PART]` |
| `PHYS-BREAK-C` | `[SURFACE]` |
| `PHYS-BREAK-C` | `[MATERIAL FAILURE]` |
| `HOLD-BREAK` | `[OBJECT]` |
| `VOICE-PATTERN` | `[VOICE-OPEN]` |
| `REF-MANIFEST` | `[MARKERS]` |
| `REF-MANIFEST` | `[ANCHORS]` |
| `M5-PUPPET` | `[NAMED SCULPT ASYMMETRIES]` |

## Reproduce

```bash
pe lint
```
