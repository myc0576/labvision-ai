"""Generate Douyin image-text assets from labvision-ai synthetic data."""
from __future__ import annotations

from pathlib import Path

import numpy as np

import labvision as lv
from labvision.core.colormap import apply_colormap, percentile_scale
from labvision.viz.overlay import save_rgb_image

OUT = Path("G:/projects/labvision-ai/douyin_assets")


def cell_like_stack(n_frames: int = 8) -> np.ndarray:
    """Synthetic microscopy-like frames with bright spots and noise."""
    rng = np.random.default_rng(42)
    shape = (200, 300)
    frames = []
    for i in range(n_frames):
        y, x = np.indices(shape, dtype=np.float32)
        bg = 8.0 + 0.5 * np.sin(x / 40.0) * np.cos(y / 30.0)
        # scattered bright spots
        for cx, cy, r, a in [(90, 60, 12, 180), (200, 140, 9, 150), (150, 100, 7, 120), (60, 130, 10, 160)]:
            spot = a * np.exp(-(((x - cx) ** 2) / (2 * r**2) + ((y - cy) ** 2) / (2 * r**2)))
            bg += spot * (1.0 + 0.1 * i)
        bg += rng.normal(0, 2.5, shape)
        frames.append(bg.astype(np.float32))
    return np.stack(frames, axis=0)


def particle_like_stack(n_frames: int = 6) -> np.ndarray:
    """Synthetic spray/particle-like frames with streaks."""
    rng = np.random.default_rng(99)
    shape = (240, 320)
    frames = []
    for i in range(n_frames):
        y, x = np.indices(shape, dtype=np.float32)
        bg = np.full(shape, 5.0, dtype=np.float32)
        for _ in range(25):
            cx, cy = rng.uniform(20, 300), rng.uniform(20, 220)
            streak_len = rng.uniform(3, 18)
            angle = rng.uniform(0, 2 * np.pi)
            tail = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            head = (x - cx) * np.cos(angle) + (y - cy) * np.sin(angle)
            streak = tail < streak_len
            bg[streak] += rng.uniform(30, 80)
        frames.append(bg)
    return np.stack(frames, axis=0)


def noise_pattern_stack(n_frames: int = 5) -> np.ndarray:
    """Synthetic noisy signal frames like spectrometer output."""
    rng = np.random.default_rng(77)
    shape = (180, 280)
    frames = []
    for i in range(n_frames):
        y, x = np.indices(shape, dtype=np.float32)
        # Horizontal bands pattern
        bands = 15.0 + 8.0 * np.sin(y / 12.0 + i * 0.6) * np.cos(x / 25.0)
        bands += rng.normal(0, 3.0, shape)
        # Bright rectangular ROI
        mask = (y > 60) & (y < 120) & (x > 80) & (x < 200)
        bands[mask] += 40 + i * 4
        frames.append(bands.astype(np.float32))
    return np.stack(frames, axis=0)


def make_before_after(original: np.ndarray, processed: np.ndarray, label: str, out_dir: Path) -> None:
    """Create side-by-side before/after comparison image."""
    # Ensure both are 2D
    if original.ndim == 3:
        original = lv.time_average(original)
    if processed.ndim == 3:
        processed = lv.time_average(processed)

    color_orig = apply_colormap(original, palette="gray")
    color_proc = apply_colormap(processed, palette="magma")

    # Pad to same height
    h = max(color_orig.shape[0], color_proc.shape[0])
    w_orig = color_orig.shape[1]
    w_proc = color_proc.shape[1]

    gap = np.full((h, 8, 3), 255, dtype=np.uint8)
    canvas = np.concatenate([color_orig, gap, color_proc], axis=1)
    save_rgb_image(out_dir / f"{label}_before_after.png", canvas)


def make_multi_step(images: list[np.ndarray], labels: list[str], filename: str, out_dir: Path) -> None:
    """Create multi-step processing pipeline showcase."""
    rendered = []
    for img, label in zip(images, labels):
        if img.ndim == 3:
            img = lv.time_average(img)
        rgb = apply_colormap(img, palette="magma")
        rendered.append(rgb)

    h = 200
    panels = []
    for rgb in rendered:
        # Resize to standard height
        scale = h / rgb.shape[0]
        w = int(rgb.shape[1] * scale)
        from PIL import Image
        pil = Image.fromarray(rgb).resize((w, h), Image.LANCZOS)
        panels.append(np.asarray(pil))

    gap = np.full((h, 6, 3), 255, dtype=np.uint8)
    canvas = panels[0]
    for p in panels[1:]:
        canvas = np.concatenate([canvas, gap, p], axis=1)
    save_rgb_image(out_dir / filename, canvas)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # 1. Cell-like microscopy simulation
    print("Generating cell-like microscopy assets...")
    cell_stack = cell_like_stack(8)
    cell_cleaned = lv.subtract_background(cell_stack, mode="percentile_1")
    cell_avg = lv.time_average(cell_cleaned)
    cell_norm = lv.normalize(cell_avg, "minmax")
    cell_overlay = lv.compose_overlay(cell_avg, cell_norm, alpha=0.5)

    make_before_after(cell_stack[0], cell_norm, "01_cell", OUT)
    save_rgb_image(OUT / "01_cell_overlay.png", cell_overlay)

    triptych1 = lv.make_triptych(
        [cell_avg, cell_norm, cell_overlay],
        labels=["Raw Avg", "Normalized", "Overlay"],
    )
    save_rgb_image(OUT / "01_cell_triptych.png", triptych1)

    # 2. Particle/spray simulation
    print("Generating particle/spray assets...")
    part_stack = particle_like_stack(6)
    part_cleaned = lv.subtract_background(part_stack, mode="percentile_1")
    part_avg = lv.time_average(part_cleaned)
    part_norm = lv.normalize(part_avg, "minmax")
    part_overlay = lv.compose_overlay(part_avg, part_norm, alpha=0.45)

    make_before_after(part_stack[0], part_norm, "02_particle", OUT)
    save_rgb_image(OUT / "02_particle_overlay.png", part_overlay)

    # 3. Spectrometer noise pattern
    print("Generating spectrometer assets...")
    noise_stack = noise_pattern_stack(5)
    noise_cleaned = lv.subtract_background(noise_stack, mode="min")
    noise_avg = lv.time_average(noise_cleaned)
    noise_norm = lv.normalize(noise_avg, "minmax")

    make_before_after(noise_stack[0], noise_norm, "03_spectrometer", OUT)

    # 4. Multi-colormap showcase
    print("Generating colormap showcase...")
    palettes = ["magma", "viridis", "inferno", "plasma", "cividis"]
    cmap_images = [apply_colormap(cell_norm, palette=p) for p in palettes]

    h, w = 180, cell_norm.shape[1] * 180 // cell_norm.shape[0]
    from PIL import Image
    resized = []
    for img in cmap_images:
        pil = Image.fromarray(img).resize((w, h), Image.LANCZOS)
        resized.append(np.asarray(pil))

    gap_v = np.full((4, resized[0].shape[1], 3), 255, dtype=np.uint8)
    try:
        canvas = np.vstack([resized[0], gap_v, resized[1], gap_v, resized[2]])
    except ValueError:
        canvas = np.hstack(resized[:3])

    if canvas.ndim == 3 and canvas.shape[-1] == 3:
        save_rgb_image(OUT / "04_colormap_showcase.png", canvas)

    # 5. Code snippet card (text-based, white bg)
    print("Generating code snippet cards...")
    code_snippet = (
        "import labvision as lv\n\n"
        "# Read your experiment images\n"
        "stack = lv.read_stack('data/')\n\n"
        "# Subtract background (auto!)\n"
        "clean = lv.subtract_background(\n"
        "    stack.frames, mode='percentile_1'\n"
        ")\n\n"
        "# Time average & normalize\n"
        "avg = lv.time_average(clean)\n"
        "norm = lv.normalize(avg)\n\n"
        "# Color map & save\n"
        "rgb = lv.apply_colormap(norm)\n\n"
        "# pip install labvision-ai\n"
        "# GitHub: myc0576/labvision-ai"
    )

    print(f"\nDone! Assets saved to {OUT.resolve()}")
    print(f"Files: {sorted(p.name for p in OUT.glob('*.png'))}")


if __name__ == "__main__":
    main()
