from __future__ import annotations

from pathlib import Path

import numpy as np


def percentile_scale(image: np.ndarray, *, low: float = 1.0, high: float = 99.0) -> np.ndarray:
    data = np.asarray(image, dtype=np.float32)
    finite = data[np.isfinite(data)]
    if finite.size == 0:
        raise ValueError("Image contains no finite pixels")
    lo = float(np.percentile(finite, low))
    hi = float(np.percentile(finite, high))
    if hi <= lo:
        hi = lo + 1.0
    return np.clip((data - lo) / (hi - lo), 0.0, 1.0).astype(np.float32)


def apply_colormap(image: np.ndarray, *, low: float = 1.0, high: float = 99.0, palette: str = "magma") -> np.ndarray:
    scaled = np.nan_to_num(percentile_scale(image, low=low, high=high), nan=0.0, posinf=1.0, neginf=0.0)
    try:
        import matplotlib.colormaps as colormaps
        cmap = colormaps[palette]
        return (cmap(scaled)[..., :3] * 255).round().astype(np.uint8)
    except Exception:
        r = np.clip((scaled - 0.35) / 0.65, 0.0, 1.0)
        g = np.clip(scaled * 1.3, 0.0, 1.0)
        b = np.clip(1.0 - scaled * 0.9, 0.0, 1.0)
        return (np.stack([r, g, b], axis=-1) * 255).round().astype(np.uint8)


def save_colormapped(path: str | Path, image: np.ndarray, *, palette: str = "magma") -> Path:
    try:
        from PIL import Image
    except Exception as exc:  # pragma: no cover
        raise ImportError("Saving colormapped images requires optional extra '[viz]' or '[image]'") from exc
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(apply_colormap(image, palette=palette), mode="RGB").save(target)
    return target
