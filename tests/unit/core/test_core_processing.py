from __future__ import annotations

import numpy as np
from numpy.testing import assert_allclose

import labvision as lv
from labvision.core.colormap import percentile_scale
from labvision.core.io import ensure_grayscale_array
from labvision.core.preprocess import normalize_plane, subtract_background, time_average
from labvision.core.roi import crop_plane, crop_stack
from labvision.report.manifest import Manifest, read_manifest, write_manifest
from labvision.report.markdown import render_markdown_summary


def test_top_level_public_api_exports_core_functions():
    expected = {
        "ImageStack",
        "apply_colormap",
        "compose_overlay",
        "make_triptych",
        "normalize",
        "read_image",
        "read_stack",
        "subtract_background",
        "time_average",
    }
    assert expected.issubset(set(lv.__all__))
    for name in expected:
        assert hasattr(lv, name)


def test_io_grayscale_background_average_normalize_roi_and_colormap(tmp_path):
    rgb = np.dstack([np.ones((3, 4)) * 10, np.ones((3, 4)) * 20, np.ones((3, 4)) * 30])
    gray = ensure_grayscale_array(rgb)
    assert gray.shape == (3, 4)
    assert_allclose(gray[0, 0], 18.15, rtol=1e-6)

    image_path = tmp_path / "image.npy"
    np.save(image_path, gray)
    assert lv.read_image(image_path).shape == (3, 4)
    stack_obj = lv.read_stack(image_path)
    assert isinstance(stack_obj, lv.ImageStack)
    assert stack_obj.frames.shape == (1, 3, 4)

    stack = np.stack([np.arange(12, dtype=np.float32).reshape(3, 4), np.arange(12, dtype=np.float32).reshape(3, 4) + 2])
    sub = subtract_background(stack, "global_min")
    assert float(sub.min()) == 0.0
    avg = time_average(sub)
    assert_allclose(avg, np.arange(12, dtype=np.float32).reshape(3, 4))
    norm = normalize_plane(avg, "minmax")
    assert_allclose(lv.normalize(avg), norm)
    assert float(norm.min()) == 0.0 and float(norm.max()) == 1.0
    assert crop_plane(norm, {"x": 1, "y": 1, "width": 2, "height": 2}).shape == (2, 2)
    assert crop_stack(stack, {"x_min": 1, "x_max": 3, "y_min": 0, "y_max": 2}).shape == (2, 2, 2)
    assert percentile_scale(norm).shape == norm.shape
    assert lv.apply_colormap(norm).shape == (3, 4, 3)
    assert lv.compose_overlay(norm, norm).shape == (3, 4, 3)
    assert lv.make_triptych([avg, norm, lv.compose_overlay(norm, norm)]).shape == (3, 20, 3)


def test_manifest_and_markdown_schema(tmp_path):
    manifest = Manifest(run_id="r1", pipeline="unit", outputs={"normalized": "normalized.npy"}, metrics={"coverage": 1.0})
    path = write_manifest(tmp_path / "manifest.json", manifest)
    loaded = read_manifest(path)
    assert loaded["run_id"] == "r1"
    markdown = render_markdown_summary(loaded)
    assert "## Outputs" in markdown
    assert "## Reproducibility" in markdown
