from __future__ import annotations

import math
import re

import numpy as np

__all__ = [
    "normalize",
    "normalize_plane",
    "prepare_average",
    "subtract_background",
    "time_average",
]


def _parse_percentile(method: str, *, default: float) -> float:
    match = re.search(r"(\d+(?:\.\d+)?)", method)
    return float(match.group(1)) if match else default


def subtract_background(stack: np.ndarray, mode: str | None = "none") -> np.ndarray:
    data = np.asarray(stack, dtype=np.float32)
    normalized = (mode or "none").casefold().replace("-", "_").replace(" ", "_")
    if normalized in {"none", "raw", "identity"}:
        return data
    if data.ndim not in {2, 3}:
        raise ValueError("Background subtraction expects a 2D plane or 3D stack")
    axes = (-2, -1)
    if normalized in {"min", "global_min"} or "global_min" in normalized:
        baseline = np.min(data, axis=axes, keepdims=True)
    elif "percentile" in normalized:
        baseline = np.percentile(data, _parse_percentile(normalized, default=1.0), axis=axes, keepdims=True)
    else:
        raise ValueError(f"Unsupported background subtraction mode: {mode}")
    return np.clip(data - baseline, 0.0, None).astype(np.float32, copy=False)


def time_average(stack: np.ndarray) -> np.ndarray:
    data = np.asarray(stack, dtype=np.float32)
    if data.ndim != 3:
        raise ValueError("Expected stack shape (n, height, width)")
    return data.mean(axis=0, dtype=np.float32).astype(np.float32, copy=False)


def normalize_plane(plane: np.ndarray, method: str = "minmax") -> np.ndarray:
    data = np.asarray(plane, dtype=np.float32)
    finite = np.isfinite(data)
    if not finite.any():
        raise ValueError("Normalization input contains no finite pixels")
    values = data[finite]
    normalized = method.casefold().replace("-", "_").replace(" ", "_")
    if normalized in {"none", "raw", "identity"}:
        return data
    if "minmax" in normalized:
        lo = float(values.min())
        hi = float(values.max())
        if hi <= lo:
            return np.zeros_like(data, dtype=np.float32)
        return ((data - lo) / (hi - lo)).astype(np.float32, copy=False)
    if "mean" in normalized:
        denom = float(values.mean())
    elif "max" in normalized:
        denom = float(values.max())
    elif "percentile" in normalized:
        denom = float(np.percentile(values, _parse_percentile(normalized, default=99.0)))
    else:
        raise ValueError(f"Unsupported normalization method: {method}")
    if denom <= 0 or not math.isfinite(denom):
        raise ValueError(f"Normalization denominator must be positive and finite, got {denom}")
    return (data / denom).astype(np.float32, copy=False)


def normalize(plane: np.ndarray, method: str = "minmax") -> np.ndarray:
    """Normalize a 2D image plane using a named strategy."""
    return normalize_plane(plane, method)


def prepare_average(stack: np.ndarray, *, background: str | None = "none", normalization: str = "minmax") -> np.ndarray:
    return normalize_plane(time_average(subtract_background(stack, background)), normalization)
