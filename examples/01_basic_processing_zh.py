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
    for index in range(3):
        gradient = 15.0 + 1.2 * x + 0.4 * y + index * 2.0
        spot = 75.0 * np.exp(-(((x - 28.0) ** 2) / 120.0 + ((y - 26.0) ** 2) / 80.0))
        frames.append(gradient + spot)
    return np.stack(frames, axis=0).astype(np.float32)


def main() -> None:
    parser = argparse.ArgumentParser(description="LabVision AI 核心图像处理示例")
    parser.add_argument("--output-dir", default="examples/_outputs/01_basic_processing_zh")
    args = parser.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    stack = build_synthetic_stack()
    averaged = lv.time_average(lv.subtract_background(stack, mode="global_min"))
    normalized = lv.normalize(averaged, method="minmax")
    colored = lv.apply_colormap(normalized, palette="viridis")
    overlay = lv.compose_overlay(averaged, normalized, alpha=0.45, palette="magma")
    triptych = lv.make_triptych([averaged, normalized, overlay], labels=["avg", "norm", "overlay"])

    np.save(out / "normalized_zh.npy", normalized)
    save_rgb_image(out / "normalized_zh.png", colored)
    save_rgb_image(out / "overlay_zh.png", overlay)
    save_rgb_image(out / "triptych_zh.png", triptych)

    manifest = Manifest(
        run_id="basic-processing-zh",
        pipeline="core-basic-processing",
        inputs={"frames": int(stack.shape[0]), "shape": list(stack.shape[1:])},
        outputs={
            "normalized": "normalized_zh.npy",
            "normalized_png": "normalized_zh.png",
            "overlay": "overlay_zh.png",
            "triptych": "triptych_zh.png",
        },
        parameters={"background": "global_min", "normalization": "minmax"},
        metrics={"min": float(normalized.min()), "max": float(normalized.max())},
        provenance={"status": "clean-room-core"},
    )
    write_manifest(out / "run_manifest.json", manifest)
    write_markdown_summary(out / "summary.md", manifest.to_dict(), title="LabVision AI 核心示例")
    print(f"输出目录: {out.resolve()}")


if __name__ == "__main__":
    main()
