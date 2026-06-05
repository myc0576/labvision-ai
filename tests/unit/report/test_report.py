from __future__ import annotations

import json

import numpy as np

from labvision.report.manifest import Manifest, read_manifest, relative_outputs, write_manifest
from labvision.report.markdown import render_markdown_summary, write_markdown_summary


class TestManifest:
    def test_default_values(self):
        m = Manifest(run_id="r0", pipeline="test")
        assert m.metrics == {}
        assert m.outputs == {}
        assert m.to_dict()["run_id"] == "r0"

    def test_custom_fields(self):
        m = Manifest(
            run_id="r1",
            pipeline="p",
            metrics={"acc": 0.99},
            parameters={"lr": 0.001},
        )
        d = m.to_dict()
        assert d["metrics"]["acc"] == 0.99
        assert d["parameters"]["lr"] == 0.001

    def test_created_at_is_iso_format(self):
        m = Manifest(run_id="r2", pipeline="p")
        assert "T" in m.created_at or "+" in m.created_at

    def test_write_read_roundtrip(self, tmp_path):
        m = Manifest(
            run_id="roundtrip",
            pipeline="test",
            outputs={"a": "out/a.npy"},
            metrics={"mse": 0.01},
        )
        path = write_manifest(tmp_path / "manifest.json", m)
        loaded = read_manifest(path)
        assert loaded["run_id"] == "roundtrip"
        assert loaded["metrics"]["mse"] == 0.01

    def test_write_from_dict(self, tmp_path):
        path = write_manifest(tmp_path / "dict.json", {"run_id": "d1", "pipeline": "test"})
        assert json.loads(path.read_text())["run_id"] == "d1"


class TestRelativeOutputs:
    def test_relative_paths(self):
        outputs = {"img": "/home/user/project/out/img.png", "log": "/home/user/project/out/log.txt"}
        rel = relative_outputs(outputs, root="/home/user/project")
        assert rel["img"] == "out/img.png"

    def test_unrelated_path_stays_absolute(self):
        outputs = {"img": "/tmp/other/npy.npy"}
        rel = relative_outputs(outputs, root="/home/user")
        assert rel["img"] == "/tmp/other/npy.npy"


class TestMarkdownSummary:
    def test_renders_all_sections(self):
        md = render_markdown_summary({
            "run_id": "r1",
            "outputs": {"img": "out.png"},
            "metrics": {"coverage": 1.0},
        })
        assert "# LabVision AI Report" in md
        assert "## Outputs" in md
        assert "## Metrics" in md
        assert "## Reproducibility" in md

    def test_empty_outputs_and_metrics(self):
        md = render_markdown_summary({"run_id": "r1"})
        assert "No outputs recorded" in md
        assert "No metrics recorded" in md

    def test_custom_title(self):
        md = render_markdown_summary({"run_id": "r1"}, title="Custom Title")
        assert "# Custom Title" in md

    def test_writes_file(self, tmp_path):
        dest = write_markdown_summary(tmp_path / "summary.md", {"run_id": "r1"})
        assert dest.exists()
        assert dest.stat().st_size > 0
