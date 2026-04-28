"""LabVision AI public open-core API.

The top-level import is intentionally lightweight and depends only on NumPy.
Optional readers and renderers import their extra dependencies at call time.
"""

from labvision.core.colormap import apply_colormap
from labvision.core.io import ImageStack, read_image, read_stack
from labvision.core.preprocess import normalize, subtract_background, time_average
from labvision.viz.figure import make_triptych
from labvision.viz.overlay import compose_overlay

__all__ = [
    "__version__",
    "ImageStack",
    "apply_colormap",
    "compose_overlay",
    "make_triptych",
    "normalize",
    "read_image",
    "read_stack",
    "subtract_background",
    "time_average",
]

__version__ = "0.1.0"
