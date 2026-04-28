# Source Responsibility Mapping

This public core release keeps only small, clean-room image-processing primitives. Legacy-dependent domain workflows and layout exporters are deferred instead of shipped.

| Responsibility | Target |
|---|---|
| Image discovery/loading/grayscale | `labvision.core.io` |
| Background subtraction, averaging, normalization | `labvision.core.preprocess` |
| ROI crop | `labvision.core.roi` |
| Percentile scale and palette output | `labvision.core.colormap` |
| Overlay and triptych primitives | `labvision.viz.overlay`, `labvision.viz.figure` |
| Manifest and Markdown summaries | `labvision.report.*` |

## Deferred Boundaries

- Domain-specific scientific workflows require separate ownership review or clean-room redesign.
- Publication-layout/export features require separate ownership review or clean-room redesign.
- Package-index upload automation is out of scope for this GitHub-only release.
