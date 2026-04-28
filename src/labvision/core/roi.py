from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np


@dataclass(frozen=True, slots=True)
class ROI:
    x: int
    y: int
    width: int
    height: int

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ROI":
        if {"x", "y", "width", "height"}.issubset(raw):
            return cls(int(raw["x"]), int(raw["y"]), int(raw["width"]), int(raw["height"]))
        if {"x_min", "x_max", "y_min", "y_max"}.issubset(raw):
            return cls(int(raw["x_min"]), int(raw["y_min"]), int(raw["x_max"]) - int(raw["x_min"]), int(raw["y_max"]) - int(raw["y_min"]))
        raise ValueError(f"Unsupported ROI mapping: {raw}")

    def bounds(self, shape: tuple[int, int]) -> tuple[int, int, int, int]:
        height, width = shape
        x0 = max(0, self.x)
        y0 = max(0, self.y)
        x1 = min(width, x0 + max(0, self.width))
        y1 = min(height, y0 + max(0, self.height))
        if x1 <= x0 or y1 <= y0:
            raise ValueError(f"ROI collapses to an empty crop for image shape {shape}: {self}")
        return x0, x1, y0, y1


def coerce_roi(roi: ROI | Mapping[str, Any] | tuple[int, int, int, int] | None) -> ROI | None:
    if roi is None:
        return None
    if isinstance(roi, ROI):
        return roi
    if isinstance(roi, tuple):
        x0, x1, y0, y1 = roi
        return ROI(x=int(x0), y=int(y0), width=int(x1) - int(x0), height=int(y1) - int(y0))
    return ROI.from_mapping(roi)


def crop_plane(plane: np.ndarray, roi: ROI | Mapping[str, Any] | tuple[int, int, int, int] | None) -> np.ndarray:
    data = np.asarray(plane)
    if data.ndim != 2:
        raise ValueError("crop_plane expects a 2D image")
    parsed = coerce_roi(roi)
    if parsed is None:
        return data
    x0, x1, y0, y1 = parsed.bounds((int(data.shape[0]), int(data.shape[1])))
    return data[y0:y1, x0:x1]


def crop_stack(stack: np.ndarray, roi: ROI | Mapping[str, Any] | tuple[int, int, int, int] | None) -> np.ndarray:
    data = np.asarray(stack)
    if data.ndim != 3:
        raise ValueError("crop_stack expects shape (n, height, width)")
    parsed = coerce_roi(roi)
    if parsed is None:
        return data
    x0, x1, y0, y1 = parsed.bounds((int(data.shape[1]), int(data.shape[2])))
    return data[:, y0:y1, x0:x1]
