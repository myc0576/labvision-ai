from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping


def render_markdown_summary(manifest: Mapping[str, Any], *, title: str = "LabVision AI Report") -> str:
    outputs = manifest.get("outputs", {}) or {}
    metrics = manifest.get("metrics", {}) or {}
    lines = [f"# {title}", "", f"Run ID: `{manifest.get('run_id', 'unknown')}`", "", "## Outputs"]
    if outputs:
        for key, value in sorted(outputs.items()):
            lines.append(f"- **{key}**: `{value}`")
    else:
        lines.append("- No outputs recorded.")
    lines.extend(["", "## Metrics"])
    if metrics:
        for key, value in sorted(metrics.items()):
            lines.append(f"- **{key}**: {value}")
    else:
        lines.append("- No metrics recorded.")
    lines.extend(["", "## Reproducibility", "This Phase 1 report is generated locally from recorded inputs and parameters.", ""])
    return "\n".join(lines)


def write_markdown_summary(path: str | Path, manifest: Mapping[str, Any], *, title: str = "LabVision AI Report") -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_markdown_summary(manifest, title=title), encoding="utf-8")
    return target
