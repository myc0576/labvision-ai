from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.examples


def test_core_examples_run_and_write_expected_artifacts(tmp_path):
    root = Path(__file__).resolve().parents[2]
    expected = {
        "01_basic_processing.py": ["normalized.npy", "normalized.png", "overlay.png", "triptych.png", "run_manifest.json", "summary.md"],
        "01_basic_processing_zh.py": [
            "normalized_zh.npy",
            "normalized_zh.png",
            "overlay_zh.png",
            "triptych_zh.png",
            "run_manifest.json",
            "summary.md",
        ],
    }

    for script, artifacts in expected.items():
        output_dir = tmp_path / script[:-3]
        subprocess.run([sys.executable, str(root / "examples" / script), "--output-dir", str(output_dir)], cwd=root, check=True)
        for artifact in artifacts:
            path = output_dir / artifact
            assert path.exists(), artifact
            assert path.stat().st_size > 0, artifact
