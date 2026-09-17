"""Machine half of the Product Sheet for Demo Support Band (Appendix B, V7.36).

Step 2 of §18 absorbs this file. Appendix E5 consumes SLOTS.
Every count check here fails loudly rather than shipping a long prompt.
"""

NAME = "Demo Support Band"

# --- E5 slot fills, verbatim -------------------------------------------------
SLOTS = {
    "SITE": "",
    "LANDMARK": "",
    "OFFSET": "",
    "REGION": "",
    "STACK": "",
    "BONES": "",
    "TARGET": "",
    "BAND-MATERIAL": "",
    "HARDWARE": "",
    "BAND-INNER": "",
    "CONTACT": "",
    "NAMED-ASYMMETRIES": "",
    "REAR-PATH": "",
    "BAND-HEIGHT-RATIO": "",
    "LOAD-CADENCE": "",
    "FEATURE": "",
    "FRACTION": "",
}

# --- Measured ratios, with tolerance (V7.47) ---------------------------------
RATIOS = {
    # "feature_span_over_whole_width": (value, tolerance),
}

# --- Locked strings, filled from the Standards patterns ----------------------
PLACE_LOCK = ""
ORIENT_LOCK = ""
NEG_PLACE = ""

# --- Verification checklist as assertions (§18 step 2) -----------------------
def verify():
    """Raises on anything that would invalidate every beat built against it."""
    missing = [name for name, value in SLOTS.items() if not value]
    assert not missing, f"unfilled Product Sheet slots: {missing}"
    for name, spec in RATIOS.items():
        assert len(spec) == 2, f"{name} needs (value, tolerance), not an adjective"


if __name__ == "__main__":
    verify()
    print(f"{NAME}: product sheet verified")
