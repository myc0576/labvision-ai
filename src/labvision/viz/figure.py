from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np

from labvision.core.colormap import apply_colormap
from labvision.viz.overlay import save_rgb_image


def make_triptych(images: Sequence[np.ndarray], *, labels: Sequence[str] | None = None, palette: str = "magma") -> np.ndarray:
    if len(images) != 3:
        raise ValueError("Triptych requires exactly three images")
    rendered = [apply_colormap(image, palette=palette) if image.ndim == 2 else image.astype(np.uint8) for image in images]
    height = min(item.shape[0] for item in rendered)
    width = min(item.shape[1] for item in rendered)
    panels = [item[:height, :width, :3] for item in rendered]
    gap = np.full((height, 4, 3), 255, dtype=np.uint8)
    canvas = np.concatenate([panels[0], gap, panels[1], gap, panels[2]], axis=1)
    if labels:
        try:
            from PIL import Image, ImageDraw
        except Exception:
            return canvas
        image = Image.fromarray(canvas, mode="RGB")
        draw = ImageDraw.Draw(image)
        offsets = [0, width + 4, 2 * (width + 4)]
        for label, x in zip(labels, offsets, strict=False):
            draw.rectangle((x + 2, 2, x + min(width - 2, 160), 20), fill=(255, 255, 255))
            draw.text((x + 5, 5), str(label), fill=(0, 0, 0))
        return np.asarray(image)
    return canvas


def save_triptych(path: str | Path, images: Sequence[np.ndarray], *, labels: Sequence[str] | None = None, palette: str = "magma") -> Path:
    return save_rgb_image(path, make_triptych(images, labels=labels, palette=palette))
