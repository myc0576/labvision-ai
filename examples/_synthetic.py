from __future__ import annotations

from pathlib import Path

import numpy as np


def synthetic_pair(shape: tuple[int, int] = (64, 80)) -> tuple[np.ndarray, np.ndarray]:
    y, x = np.indices(shape, dtype=np.float32)
    blob = np.exp(-(((x - 38) ** 2) / 190.0 + ((y - 30) ** 2) / 130.0))
    mie = 20 + 180 * blob + 10 * np.sin(x / 8.0)
    lif = 15 + 140 * np.exp(-(((x - 35) ** 2) / 210.0 + ((y - 28) ** 2) / 145.0))
    lif[:5, :] += 80
    return lif.astype(np.float32), mie.astype(np.float32)


def save_gray_png(path: str | Path, image: np.ndarray) -> Path:
    from PIL import Image
    data = np.asarray(image, dtype=np.float32)
    scaled = (255 * (data - data.min()) / max(float(data.max() - data.min()), 1e-6)).round().astype(np.uint8)
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(scaled, mode="L").save(target)
    return target
