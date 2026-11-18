# Puts plugins/anvil/bin on sys.path so tests can import anvil_cli under python -I.
import sys
from pathlib import Path

_BIN = Path(__file__).resolve().parents[2] / "plugins" / "anvil" / "bin"
if str(_BIN) not in sys.path:
    sys.path.insert(0, str(_BIN))
