from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


@dataclass(slots=True)
class Manifest:
    run_id: str
    pipeline: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, str] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def relative_outputs(outputs: Mapping[str, str | Path], *, root: str | Path) -> dict[str, str]:
    base = Path(root)
    result: dict[str, str] = {}
    for key, value in outputs.items():
        path = Path(value)
        try:
            result[key] = path.relative_to(base).as_posix()
        except ValueError:
            result[key] = path.as_posix()
    return result


def write_manifest(path: str | Path, manifest: Manifest | Mapping[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = manifest.to_dict() if isinstance(manifest, Manifest) else dict(manifest)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target


def read_manifest(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
