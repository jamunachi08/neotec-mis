"""
Compatibility shim for environments that still expect the module path:
    neotec_mis.neotec_mis

Do NOT remove. This prevents install failures if Frappe Cloud caches an older modules.txt.
"""
from .neotec_mis_builder import *  # noqa: F401,F403
