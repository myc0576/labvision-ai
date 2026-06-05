# LabVision AI

[![CI](https://github.com/YOUR_USERNAME/labvision-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/labvision-ai/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/labvision-ai.svg)](https://pypi.org/project/labvision-ai/)
[![Python 3.10+](https://img.shields.io/pypi/pyversions/labvision-ai.svg)](https://pypi.org/project/labvision-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight, MIT-licensed Python package for reproducible laboratory image processing.
Clean-room design: no AI, no network calls, no vendor lock-in — just fast, auditable image pipelines.

## Why LabVision AI?

- **Minimal dependencies**: Base install requires only NumPy. Image readers and visualization load their extras at call time.
- **Clean API**: 9 functions + 2 dataclasses. Learn in 5 minutes.
- **Reproducible**: Every pipeline emits a JSON manifest and Markdown summary.
- **MIT licensed**: Use it anywhere — academic, commercial, embedded.

## Install

```bash
pip install labvision-ai              # base (NumPy only)
pip install labvision-ai[image]       # + Pillow, tifffile
pip install labvision-ai[viz]         # + matplotlib, Pillow
pip install labvision-ai[all,dev]     # everything + test tooling
```

## Quick Start

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

## Public API

| Function | Description |
|----------|-------------|
| `read_image(path)` | Read a single image as float32 grayscale array |
| `read_stack(path)` | Read a file or directory as `ImageStack` |
| `ImageStack` | Named tuple: `.frames`, `.source_path`, `.files`, `.frame_count` |
| `subtract_background(stack, mode)` | Background subtraction (`"none"`, `"min"`, `"percentile_N"`) |
| `time_average(stack)` | Temporal mean across frames |
| `normalize(plane, method)` | Normalize 2D plane (`"minmax"`, `"mean"`, `"max"`, `"percentile_NN"`) |
| `apply_colormap(image, palette)` | Apply matplotlib colormap with graceful fallback |
| `compose_overlay(base, signal, alpha)` | Blend grayscale base with colormapped signal |
| `make_triptych(images, labels)` | 3-panel horizontal figure with optional labels |

## Verification

```bash
git clone https://github.com/YOUR_USERNAME/labvision-ai.git
cd labvision-ai
python -m pip install -e ".[all,dev]"
python -m pytest -v
python scripts/check_import_boundaries.py
```

## Scope

This is the **open core** — image I/O, preprocessing, colormaps, overlays, triptychs, manifests.
Domain-specific workflows, hosted AI features, and paid integrations are intentionally deferred.

See `docs/provenance/` for historical decisions on what was deferred and why.

## License

MIT — see [LICENSE](./LICENSE).
