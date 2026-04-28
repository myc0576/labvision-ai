from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

import labvision as lv
from labvision.report import Manifest, write_manifest, write_markdown_summary
from labvision.viz.overlay import save_rgb_image


def build_synthetic_stack() -> np.ndarray:
    y, x = np.indices((48, 64), dtype=np.float32)
    frames = []
    for index in range(4):
        signal = 20.0 + 0.8 * x + 0.5 * y + index * 3.0
        feature = 90.0 * np.exp(-(((x - 36.0) ** 2) / 150.0 + ((y - 24.0) ** 2) / 95.0))
        frames.append(signal + feature)
    return np.stack(frames, axis=0).astype(np.float32)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="examples/_outputs/01_basic_processing")
    args = parser.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    stack = build_synthetic_stack()
    cleaned = lv.subtract_background(stack, mode="percentile_1")
    averaged = lv.time_average(cleaned)
    normalized = lv.normalize(averaged, method="minmax")
    colored = lv.apply_colormap(normalized, palette="magma")
    overlay = lv.compose_overlay(averaged, normalized, alpha=0.5, palette="viridis")
    triptych = lv.make_triptych([averaged, normalized, overlay], labels=["average", "normalized", "overlay"])

    np.save(out / "normalized.npy", normalized)
    save_rgb_image(out / "normalized.png", colored)
    save_rgb_image(out / "overlay.png", overlay)
    save_rgb_image(out / "triptych.png", triptych)

    manifest = Manifest(
        run_id="basic-processing",
        pipeline="core-basic-processing",
        inputs={"frames": int(stack.shape[0]), "shape": list(stack.shape[1:])},
        outputs={
            "normalized": "normalized.npy",
            "normalized_png": "normalized.png",
            "overlay": "overlay.png",
            "triptych": "triptych.png",
        },
        parameters={"background": "percentile_1", "normalization": "minmax"},
        metrics={"min": float(normalized.min()), "max": float(normalized.max())},
        provenance={"status": "clean-room-core"},
    )
    write_manifest(out / "run_manifest.json", manifest)
    write_markdown_summary(out / "summary.md", manifest.to_dict(), title="LabVision AI Core Example")
    print(out.resolve())


if __name__ == "__main__":
    main()
