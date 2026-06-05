from __future__ import annotations

from pathlib import Path

import numpy as np

from labvision.core.colormap import apply_colormap, percentile_scale


def compose_overlay(base: np.ndarray, signal: np.ndarray, *, alpha: float = 0.45, palette: str = "magma") -> np.ndarray:
    base_scaled = (percentile_scale(base) * 255).round().astype(np.uint8)
    base_rgb = np.repeat(base_scaled[..., None], 3, axis=-1)
    color = apply_colormap(signal, palette=palette)
    mask = np.isfinite(signal)
    blended = base_rgb.astype(np.float32)
    blended[mask] = (1.0 - alpha) * blended[mask] + alpha * color[mask].astype(np.float32)
    return np.clip(blended, 0, 255).round().astype(np.uint8)


def save_rgb_image(path: str | Path, rgb: np.ndarray) -> Path:
    try:
        from PIL import Image
    except Exception as exc:  # pragma: no cover
        raise ImportError("Saving RGB images requires optional extra '[viz]' or '[image]'") from exc
    data = np.asarray(rgb)
    if data.ndim != 3 or data.shape[-1] != 3:
        raise ValueError("Expected RGB image shape (height, width, 3)")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(data.astype(np.uint8)).save(target)
    return target
