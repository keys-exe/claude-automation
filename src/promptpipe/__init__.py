"""promptpipe — the machine half of the AI Prompt Engineer Global Standards.

Appendix E made executable. Nothing here changes the craft; it makes the craft
checkable by script so the pipeline stops only at §18 step 6.
"""

from .standards import load, minify, parse  # noqa: F401

__all__ = ["load", "parse", "minify", "__version__"]
__version__ = "0.1.0"
