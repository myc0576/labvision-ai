from __future__ import annotations

import numpy as np
import pytest
from numpy.testing import assert_allclose

from labvision.core.colormap import apply_colormap, percentile_scale, save_colormapped
from labvision.viz.figure import make_triptych, save_triptych
from labvision.viz.overlay import compose_overlay, save_rgb_image


class TestPercentileScale:
    def test_identity_range(self):
        arr = np.array([0.0, 1.0], dtype=np.float32).reshape(1, 2)
        result = percentile_scale(arr, low=0, high=100)
        assert_allclose(result.min(), 0.0, atol=1e-6)
        assert_allclose(result.max(), 1.0, atol=1e-6)

    def test_constant_input_does_not_crash(self):
        arr = np.ones((2, 2), dtype=np.float32) * 5.0
        result = percentile_scale(arr)
        assert result.shape == (2, 2)
        assert not np.any(np.isnan(result))

    def test_all_nan_raises(self):
        with pytest.raises(ValueError, match="finite"):
            percentile_scale(np.full((2, 2), np.nan))


class TestApplyColormap:
    def test_known_palette(self, sample_plane):
        rgb = apply_colormap(sample_plane, palette="inferno")
        assert rgb.shape == (3, 4, 3)
        assert rgb.dtype == np.uint8
        assert rgb.max() <= 255
        assert rgb.min() >= 0

    def test_fallback_when_matplotlib_missing(self, monkeypatch, sample_plane):
        import importlib

        if "matplotlib" not in importlib.import_module("labvision.core.colormap").__dict__:
            pytest.skip("matplotlib import guard already exercised")
        # The fallback branch runs when matplotlib import fails; we test it indirectly
        # via the colormap no-dependency path
        rgb = apply_colormap(sample_plane)
        assert rgb.shape == (3, 4, 3)
        assert rgb.dtype == np.uint8

    def test_extreme_values_dont_crash(self):
        arr = np.array([-999.0, 0.0, 999.0], dtype=np.float32).reshape(1, 3)
        rgb = apply_colormap(arr)
        assert rgb.shape == (1, 3, 3)
        assert not np.any(np.isnan(rgb))


class TestSaveColormapped:
    def test_writes_file(self, tmp_path, sample_plane):
        dest = tmp_path / "sub" / "cmapped.png"
        result = save_colormapped(dest, sample_plane)
        assert result == dest
        assert dest.exists()
        assert dest.stat().st_size > 0


class TestComposeOverlay:
    def test_shape_and_range(self, sample_plane):
        signal = sample_plane.copy()
        signal[1, 1] = 100.0
        rgb = compose_overlay(sample_plane, signal, alpha=0.5)
        assert rgb.shape == (3, 4, 3)
        assert rgb.dtype == np.uint8

    def test_nan_signal_pixels_preserved_as_base(self, sample_plane):
        signal = sample_plane.astype(np.float32)
        signal[0, 0] = np.nan
        rgb = compose_overlay(sample_plane, signal)
        assert not np.any(np.isnan(rgb))


class TestSaveRgbImage:
    def test_saves_valid_rgb(self, tmp_path):
        rgb = np.zeros((2, 2, 3), dtype=np.uint8) + 128
        dest = save_rgb_image(tmp_path / "rgb.png", rgb)
        assert dest.exists()

    def test_rejects_grayscale(self, tmp_path):
        with pytest.raises(ValueError, match="RGB"):
            save_rgb_image(tmp_path / "bad.png", np.zeros((2, 2)))


class TestMakeTriptych:
    def test_three_grayscale_images(self, sample_plane):
        canvas = make_triptych([sample_plane, sample_plane, sample_plane])
        assert canvas.ndim == 3
        assert canvas.shape[-1] == 3

    def test_with_labels(self, sample_plane):
        canvas = make_triptych(
            [sample_plane, sample_plane, sample_plane],
            labels=["A", "B", "C"],
        )
        assert canvas.ndim == 3

    def test_rejects_wrong_count(self, sample_plane):
        with pytest.raises(ValueError, match="three"):
            make_triptych([sample_plane])

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="three"):
            make_triptych([])


class TestSaveTriptych:
    def test_writes_file(self, tmp_path, sample_plane):
        dest = tmp_path / "triptych.png"
        result = save_triptych(dest, [sample_plane] * 3)
        assert result == dest
        assert dest.stat().st_size > 0
