# LabVision AI

LabVision AI is a small, installable MIT-licensed core package for reproducible laboratory image processing. The current public release is intentionally non-AI: it provides clean-room image IO, preprocessing, normalization, ROI cropping, colormaps, overlays, triptychs, manifests, and Markdown summaries.

Domain-specific workflows, figure-layout exporters, hosted AI features, paid licensing, and package-index uploads are deferred until their ownership and product boundaries are reviewed separately.

## Install

```powershell
python -m pip install .
python -m pip install .[image,viz]
python -m pip install .[all,dev]
```

Base import is lightweight and depends only on NumPy:

```python
import labvision as lv
```

Optional image readers and visualization output load Pillow, tifffile, or Matplotlib only when the relevant function is called.

## Public API

```python
import labvision as lv

stack = lv.read_stack("path/to/images")
clean = lv.subtract_background(stack.frames, mode="percentile_1")
average = lv.time_average(clean)
normalized = lv.normalize(average, method="minmax")

rgb = lv.apply_colormap(normalized, palette="magma")
overlay = lv.compose_overlay(average, normalized, alpha=0.45)
triptych = lv.make_triptych([average, normalized, overlay], labels=["avg", "norm", "overlay"])
```

Stable top-level exports:

- `read_image`
- `read_stack`
- `ImageStack`
- `subtract_background`
- `time_average`
- `normalize`
- `apply_colormap`
- `compose_overlay`
- `make_triptych`

## Examples

```powershell
python examples/01_basic_processing.py --output-dir examples/_outputs/01_basic_processing
python examples/01_basic_processing_zh.py --output-dir examples/_outputs/01_basic_processing_zh
```

The examples generate deterministic synthetic arrays plus PNG, NPY, JSON manifest, and Markdown summary outputs.

## Verification

```powershell
python -m pip install -e .[all,dev]
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
python -m pytest
python scripts/check_import_boundaries.py
python -m compileall -q src tests examples scripts
powershell -ExecutionPolicy Bypass -File scripts/run_examples.ps1
python -m build
```

## Scope Notes

This repository is prepared for public GitHub browsing, installation, and testing as an open core package. It is not configured for package-index upload in this release.

Historical provenance records are kept under `docs/provenance/` so future maintainers can see which legacy-dependent features were deferred instead of shipped.
