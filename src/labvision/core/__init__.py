"""Reusable clean-room image-processing primitives."""

from labvision.core.colormap import apply_colormap
from labvision.core.io import ImageStack, read_image, read_stack
from labvision.core.preprocess import normalize, subtract_background, time_average
from labvision.core.roi import ROI, coerce_roi, crop_plane, crop_stack

__all__ = [
    "ImageStack",
    "ROI",
    "apply_colormap",
    "coerce_roi",
    "crop_plane",
    "crop_stack",
    "normalize",
    "read_image",
    "read_stack",
    "subtract_background",
    "time_average",
]
