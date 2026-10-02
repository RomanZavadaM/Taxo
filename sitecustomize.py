"""Taxo repository bootstrap: expose internal source modules without polluting root."""
from pathlib import Path
import sys

_SRC = Path(__file__).resolve().parent / "src" / "taxo"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
