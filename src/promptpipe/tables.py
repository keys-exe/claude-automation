"""Appendix E tables, transcribed with their section reference.

These are the only figures this package hard-codes. Each carries the section it
came from so a Standards cut that moves a threshold is traceable to one line.
"""

from __future__ import annotations

# --- E6 duration function (the §28H inverse) ------------------------------

WORDS_PER_DURATION = {
    # pace -> {clip seconds: word ceiling}  (§28H table 1)
    "brisk": {5: 9, 10: 20},
    "unhurried": {5: 8, 10: 18},
}

BROLL_DEFAULT_DURATION = 5          # Higgsfield floor (E6)
MECHANISM_KLING_DIRECT_DURATION = 3  # E6
MECHANISM_MIN_5S = {"ANAT-STRESS-R", "WHOLE-ARC"}  # E6: 5s minimum

# --- §37 character budgets ------------------------------------------------

KLING_DIRECT_CEILING = 2500  # §37 / E1: counted on the minified string

BEAT_BUDGETS = {
    # beat type -> expected total I2V characters (§37 four-column table)
    "TH": 3364,
    "TH-HELD": 3739,
    "BR": 3204,
    "MECH": 3239,
}

NEVER_TRIMMED = [
    # §37 "Never trimmed, at any position"
    "CAP-A", "AUD-A", "SKIN-A", "BREATH-A", "MOUTH-C", "CAM-LOCK",
    "M3-MOTION", "VOICE-OPEN", "SHEET-GRID", "MOUNT-GEOM", "CAP-CCTV",
    "CAM-CCTV", "CCTV-FRAME", "NEG-CCTV", "SKIN-B1", "CAP-FILE",
]

# --- §27B coverage dispositions ------------------------------------------

DISPOSITIONS = ("BR", "TH", "MECH", "MERGED", "BLOCKED")
WITHDRAWN_DISPOSITIONS = ("CUT",)  # §27B: withdrawn as an agent disposition

DEMO_KINDS = (
    "FLEX", "STRETCH", "ANCHOR", "LOAD", "SEAT", "SIDE-BY-SIDE", "TURN",
    "CAPABILITY", "MECHANISM-PAIR", "SENSE", "NONE",
)

# --- E4 act-map row schema ------------------------------------------------

ACT_MAP_FIELDS = [
    "beat_id", "act", "phrase_ids", "type", "register", "rig", "frame_side",
    "framing_step", "energy", "valence", "ownership", "function", "subject",
    "alibi", "location_id", "story_day", "capture_event_id", "sequence_id",
    "geo_line_ref", "wardrobe_ref", "duration", "closure_word", "stress_word",
    "bound_move_word", "product_state", "visibility", "claims", "plant",
    "cover_point", "notes",
]

ACT_MAP_REQUIRED = [
    # E4: story_day and capture_event_id are mandatory on every row
    "beat_id", "act", "phrase_ids", "type", "register", "location_id",
    "story_day", "capture_event_id", "duration", "product_state", "visibility",
]

BEAT_TYPES = ("TH", "BR", "MECH", "PRODUCT", "CTA")
ENERGY = ("calm", "lift", "stab")
VALENCE = ("pos", "neg", "neutral")
OWNERSHIP = ("STORY", "GENERIC")
PRODUCT_STATES = ("absent", "worn", "held", "seated", "demo")
VISIBILITY = ("CONCEALED", "VISIBLE", "REVEAL")

# --- E2 failure taxonomy and retry budgets --------------------------------

FAILURE_CLASSES = {
    "SAFETY_REJECT":    {"budget": 2,  "remedy": "§5 vocabulary swaps, then sibling model"},
    "PRESET_OVERRIDE":  {"budget": 3,  "remedy": "decline with declined_preset_id, resubmit"},
    "COMPLETION_404":   {"budget": 10, "remedy": "wait + re-poll, timeout 10 min"},
    "QUALITY_FAIL":     {"budget": 2,  "remedy": "targeted reroll, then escalation string (§22S ladder)"},
    "CONSISTENCY_FAIL": {"budget": 2,  "remedy": "reroll with full-form lock strings"},
    "SYNC_DRIFT":       {"budget": 1,  "remedy": "constant offset → post slip; drift → reissue"},
    "ALIAS_MISMATCH":   {"budget": 1,  "remedy": "resubmit explicit model string"},
}

GLOBAL_RETRY_CAP = 2  # E2: two automatic rerolls per beat per failure class

# --- E1 QA matrix ---------------------------------------------------------

QA_CHECKS = [
    # (id, instrument, threshold, class, on_fail)
    ("char_count", "minified length", f"<= {KLING_DIRECT_CEILING} on Kling-direct beats", "AUTO",
     "Trim ladder (§37), recount"),
    ("word_budget", "word count vs §28H table", "5s -> 9/8 · 10s -> 20/18", "AUTO",
     "Raise duration per E7 or cut the line — never squeeze"),
    ("model_run", "logged model vs passed string", "exact match", "AUTO",
     "Re-submit with explicit string; flag alias to phrasing table"),
    ("start_frame_completed", "job status", "completed", "AUTO",
     "Wait; never submit on queued"),
    ("preset_override", "response contains preset offer", "none accepted", "AUTO",
     "Decline loop with declined_preset_id, cap 3, then HUMAN"),
    ("wordmark", "OCR on first frame", "reads the mark verbatim", "AUTO-ASSIST",
     "Reroll on nano_banana_pro; §17 blank-and-post if unrouted"),
    ("feature_span_ratio", "pixel measure, feature span / whole width", "Product Sheet ratio + tolerance", "AUTO",
     "Reroll with the feature-and-whole clauses restated (§8)"),
    ("placement_ratio", "pixel measure, feature rise / whole width", "Product Sheet ratio", "AUTO",
     "Reroll with PLACE-LOCK full form"),
    ("inner_face_fixtures", "first frame, band silhouette", "fixtures visible along inner edge", "HUMAN",
     "Reroll with ORIENT-LOCK full form (§9A-P)"),
    ("entry_latency", "silence detection, -40 dB", "first word <= 0.5s", "AUTO",
     "Reissue with BREATH-A verbatim; §28G"),
    ("tts_gaps", "silence detection", "no silence > 0.4s between phrases", "AUTO",
     "Re-render block"),
    ("closure_sync", "frame-step at closure + stress word", "lips closed while audio speaks it", "HUMAN",
     "§28H triage: constant offset → slip; drift → reissue"),
    ("voice_drift", "pitch median + tempo vs act baseline", "within +/-15%", "AUTO-ASSIST",
     "Flag outliers; HUMAN listen before edit"),
    ("voice_separability", "pitch, tempo, spectral centroid pairwise", "no pair inside +/-10% on all three", "AUTO-ASSIST",
     "Rebuild the closer VOICE-[CHAR] on the further edge of its band"),
    ("scene_hold", "first frame vs Location Sheet", "anchors present, window side, prop states", "HUMAN",
     "Reroll with SCENE-REF + NEG-SCENE"),
    ("subject_hold", "first frame vs reference sheet", "markers present, same person", "HUMAN",
     "Reroll with SUBJ-REF"),
    ("location_tier", "act-map row vs §30C 1a", "PLATED only where beats hold one spot", "AUTO",
     "Strip the plate from traversed beats; add GEO-LINE"),
    ("face_state", "first frame + clip vs header FACE/NOFACE", "FACE resolved / NOFACE absent", "HUMAN",
     "FACE fail: reroll seed with FACE-SEED; NOFACE breach: reissue with NEG-NOFACE"),
    ("geography_axis", "frame vs GEO-LINE", "camera side, travel direction, fixed features", "HUMAN",
     "Rebuild framing; never fix in prose alone"),
    ("mechanism_greyscale", "desaturate one frame-pair", "event legible without colour", "HUMAN",
     "Rebuild with the stress blocks; §12B"),
    ("cycle_rate", "frame-difference periodicity", "~1 Hz +/- 0.25", "AUTO-ASSIST",
     "Reissue with the cadence number restated"),
    ("broll_cut_delta", "luminance delta at cut vs TH baseline", "measurable shift (§15)", "AUTO-ASSIST",
     "Rebuild register, never via white background"),
    ("coverage", "phrase inventory vs beat IDs diff", "uncovered = 0, plants paid", "AUTO",
     "Undelivered act until closed (§27B)"),
    ("avatar_sheet_panels", "the rendered sheet", "§19 panel check, logged sunburst/high/2k", "HUMAN",
     "Reroll the sheet; never attach a failing sheet"),
    ("candid_seed_light", "first frame", "terminator, broken forehead highlight, blown window", "HUMAN",
     "Reroll with LIGHT-EVENT restated"),
    ("face_skin_register", "eyeball", "—", "HUMAN", "§22S escalation ladder"),
]

QA_BY_ID = {check[0]: check for check in QA_CHECKS}

# --- E7 call templates ----------------------------------------------------

CALL_TEMPLATES = {
    "t2i.nano_banana_pro": {
        "tool": "generate_image_batch",
        "params": {"model": "nano_banana_pro", "aspect_ratio": "9:16", "resolution": "2k"},
        "media_role": "image",
    },
    "t2i.nano_banana_2": {
        "tool": "generate_image_batch",
        "params": {"model": "nano_banana_2", "aspect_ratio": "9:16", "resolution": "2k"},
        "media_role": "image",
    },
    "t2i.gpt_image_2_5": {
        "tool": "generate_image_batch",
        "params": {
            "model": "gpt_image_2_5", "variant": "sunburst", "quality": "high",
            "resolution": "2k", "aspect_ratio": "9:16",
        },
        "media_role": "image_references",
        "note": "Never omit quality or resolution — both default low (§19).",
    },
    "t2i.gpt_image_2": {
        "tool": "generate_image_batch",
        "params": {"model": "gpt_image_2", "quality": "high", "resolution": "2k", "aspect_ratio": "9:16"},
        "media_role": "image",
    },
    "i2v.kling3_0": {
        "tool": "generate_video_batch",
        "params": {"model": "kling3_0", "resolution": "1080p"},
        "media_role": "start_image",
        "note": "declined_preset_id mandatory on dark-field and any preset-matched beat (§5).",
    },
    "i2v.wan_references": {
        "tool": "generate_video_batch",
        "params": {
            "resolution": "1080p", "aspect_ratio": "9:16",
            "enable_prompt_expansion": False, "thinking_mode": False,
        },
        "media_role": "images",
        "note": "References mode is the default on Wan 3.0 (§4). Never video references.",
    },
    "i2v.seedance_omni": {
        "tool": "generate_video_batch",
        "params": {"resolution": "1080p", "aspect_ratio": "9:16"},
        "media_role": "images_list",
        "note": "duration never 'auto'. Audio generated regardless and discarded on B-roll.",
    },
}

# --- E5 slot-fill manifest ------------------------------------------------

SLOT_SOURCES = {
    "SITE": "product_sheet.field5", "LANDMARK": "product_sheet.field7",
    "OFFSET": "product_sheet.field7", "REGION": "product_sheet.field5",
    "STACK": "product_sheet.field5", "BONES": "product_sheet.field5",
    "TARGET": "product_sheet.field5", "TARGET JOINT": "product_sheet.field5",
    "BAND-MATERIAL": "product_sheet.field7", "HARDWARE": "product_sheet.field7",
    "BAND-INNER": "product_sheet.field7", "CONTACT": "product_sheet.field7",
    "SIDE": "act_map.declared.side",
    "RIGID": "product_sheet.pattern_fills", "LIMB": "product_sheet.pattern_fills",
    "JOINT": "product_sheet.pattern_fills", "SEGMENT-BEYOND": "product_sheet.pattern_fills",
    "FEATURE": "product_sheet.pattern_fills", "FRACTION": "product_sheet.pattern_fills",
    "NAMED-ASYMMETRIES": "product_sheet.pattern_fills",
    "REAR-PATH": "product_sheet.pattern_fills",
    "BAND-HEIGHT-RATIO": "product_sheet.pattern_fills",
    "LOAD-CADENCE": "product_sheet.pattern_fills",
    "GARMENT": "wardrobe_map", "AGE-FEATURES": "character_sheet",
    "FOREHEAD-LINES": "character_sheet", "HAIR-SPEC": "character_sheet",
    "MOUTH-CORNER": "constraint_sheet", "VOICE-CHAR": "constraint_sheet",
    "CLOSURE-WORD": "beat.dialogue", "STRESS-WORD": "act_map.row",
    "BOUND-MOVE-WORD": "act_map.row", "LOCATION": "location_sheet",
    "SUBJ-MARKERS": "subject_registry",
}

# Slots that are mandatory on particular beat classes (E5).
SLOT_REQUIREMENTS = {
    "rear_or_turning": ["BAND-INNER", "REAR-PATH"],
    "stress_register": ["LOAD-CADENCE"],
    "worn": ["SITE", "SIDE"],
}

# --- E9 build directory layout -------------------------------------------

BUILD_TREE = [
    "product_sheet.md", "product_sheet.py", "absorption_sheet.md",
    "build_sheet.md", "act_map.json", "phrase_inventory.json",
    "wardrobe_map.json", "location_sheets/", "registries/roster.json",
    "registries/voice.json", "registries/scene.json", "registries/subject.json",
    "run_ledger.json", "beats/", "capcut_block.md",
]

# --- §18 eight-step build order ------------------------------------------

BUILD_STEPS = [
    (1, "Absorb the inspo video", "DET", "§42 seven-part protocol -> Absorption Sheet"),
    (2, "Absorb script, product, Product Sheet", "DET",
     "md+py pair, §43A claims pass, phrase inventory, every lock resolved"),
    (3, "Cast — everyone who recurs", "DET", "§19 sheets + panel check; §20 + VOICE for speakers"),
    (4, "Location maps", "DET", "§30C derivation pass, five-part sheets, plates for PLATED only"),
    (5, "Act map and wardrobe map, together", "DET", "coverage ledger, story-day pass, six-slot rows"),
    (6, "Hooks, one by one", "HG", "THE ONLY GATE: deliver -> generate -> first-frame check -> confirm"),
    (7, "B-roll and body acts", "DET", "§30E assembly order, reconciliation line per act"),
    (8, "CapCut block", "DET", "cover points, J-cuts, silences, sync triage, motion graphics"),
]
