# Dependency and Extras Contract

Base installation requires only `numpy` and supports `import labvision`.

| Extra | Dependencies | Import rule |
|---|---|---|
| `image` | Pillow, tifffile | Imported inside image reader functions only. |
| `viz` | matplotlib, Pillow | Imported only when rendering or saving visual artifacts. |
| `dev` | pytest, build | Local verification only. |
| `all` | image and viz dependencies | Convenience profile for examples and tests. |

Use `scripts/check_import_boundaries.py` to enforce the public core boundary.
