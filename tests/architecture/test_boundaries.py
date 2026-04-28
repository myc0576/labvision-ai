from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_import_boundaries_script_passes():
    root = Path(__file__).resolve().parents[2]
    subprocess.run([sys.executable, str(root / "scripts" / "check_import_boundaries.py")], cwd=root, check=True)
