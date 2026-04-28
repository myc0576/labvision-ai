from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".npy"}

__all__ = [
    "ImageStack",
    "discover_image_files",
    "ensure_grayscale_array",
    "load_image_array",
    "load_image_stack",
    "read_image",
    "read_stack",
]


@dataclass(frozen=True, slots=True)
class ImageStack:
    frames: np.ndarray
    source_path: Path
    files: tuple[Path, ...]

    @property
    def frame_count(self) -> int:
        return int(self.frames.shape[0])


def _missing_extra(feature: str, extra: str, error: Exception) -> ImportError:
    exc = ImportError(f"{feature} requires optional extra '[{extra}]'. Install with: python -m pip install .[{extra}]")
    exc.__cause__ = error
    return exc


def ensure_grayscale_array(image: np.ndarray) -> np.ndarray:
    data = np.asarray(image)
    if data.ndim == 2:
        return data.astype(np.float32, copy=False)
    if data.ndim == 3:
        if data.shape[-1] < 3:
            return data[..., 0].astype(np.float32, copy=False)
        rgb = data[..., :3].astype(np.float32, copy=False)
        return (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]).astype(np.float32)
    raise ValueError(f"Expected a 2D grayscale or 3D RGB image, got shape {data.shape}")


def discover_image_files(path: str | Path, *, suffixes: Iterable[str] | None = None) -> tuple[Path, ...]:
    root = Path(path)
    allowed = {s.lower() for s in (suffixes or _IMAGE_SUFFIXES)}
    if root.is_file():
        if root.suffix.lower() not in allowed:
            raise ValueError(f"Unsupported image suffix for {root}")
        return (root,)
    if not root.exists():
        raise FileNotFoundError(root)
    files = tuple(sorted(p for p in root.iterdir() if p.is_file() and p.suffix.lower() in allowed))
    if not files:
        raise ValueError(f"No image files found under {root}")
    return files


def load_image_array(path: str | Path) -> np.ndarray:
    source = Path(path)
    if source.suffix.lower() == ".npy":
        return ensure_grayscale_array(np.load(source))
    if source.suffix.lower() in {".tif", ".tiff"}:
        try:
            import tifffile
        except Exception as exc:  # pragma: no cover
            raise _missing_extra("TIFF loading", "image", exc)
        return ensure_grayscale_array(tifffile.imread(source))
    try:
        from PIL import Image
    except Exception as exc:  # pragma: no cover
        raise _missing_extra("Image loading", "image", exc)
    with Image.open(source) as img:
        return ensure_grayscale_array(np.asarray(img))


def load_image_stack(path: str | Path) -> ImageStack:
    files = discover_image_files(path)
    frames = [load_image_array(file) for file in files]
    min_height = min(int(frame.shape[0]) for frame in frames)
    min_width = min(int(frame.shape[1]) for frame in frames)
    stack = np.stack([frame[:min_height, :min_width] for frame in frames], axis=0).astype(np.float32, copy=False)
    return ImageStack(frames=stack, source_path=Path(path), files=files)


def read_image(path: str | Path) -> np.ndarray:
    """Read a single image-like file as a float32 grayscale array."""
    return load_image_array(path)


def read_stack(path: str | Path) -> ImageStack:
    """Read one image file or a directory of image files as an ImageStack."""
    return load_image_stack(path)
