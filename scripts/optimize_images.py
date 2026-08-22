#!/usr/bin/env python3
"""Image optimization utility for AI Learning Studio.

Converts PNG/JPG images in assets/images to WebP with high quality (85)
and resizes dimensions exceeding 1600px width/height.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required to run this script (pip install Pillow).", file=sys.stderr)
    sys.exit(1)


ASSETS_IMAGES_DIR = Path(__file__).resolve().parent.parent / "assets" / "images"
MAX_DIMENSION = 1600
WEBP_QUALITY = 85


def optimize_image(image_path: Path, delete_source: bool = False) -> Path | None:
    suffix = image_path.suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg"}:
        return None

    webp_path = image_path.with_suffix(".webp")

    with Image.open(image_path) as im:
        if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
            im = im.convert("RGBA")
        else:
            im = im.convert("RGB")

        orig_w, orig_h = im.size
        if orig_w > MAX_DIMENSION or orig_h > MAX_DIMENSION:
            if orig_w >= orig_h:
                new_w = MAX_DIMENSION
                new_h = int(orig_h * MAX_DIMENSION / orig_w)
            else:
                new_h = MAX_DIMENSION
                new_w = int(orig_w * MAX_DIMENSION / orig_h)
            im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)

        webp_path.parent.mkdir(parents=True, exist_ok=True)
        im.save(webp_path, "WEBP", quality=WEBP_QUALITY, method=6)

    orig_size = image_path.stat().st_size
    webp_size = webp_path.stat().st_size
    print(f"Optimized: {image_path.name} ({orig_size / 1024:.1f}KB) -> {webp_path.name} ({webp_size / 1024:.1f}KB, {webp_size / orig_size * 100:.1f}%)")

    if delete_source and image_path != webp_path and image_path.exists():
        image_path.unlink()

    return webp_path


def main() -> int:
    delete_source = "--replace" in sys.argv or "--delete-source" in sys.argv
    if not ASSETS_IMAGES_DIR.exists():
        print(f"Error: {ASSETS_IMAGES_DIR} does not exist.", file=sys.stderr)
        return 1

    targets: list[Path] = []
    for root, _, files in os.walk(ASSETS_IMAGES_DIR):
        for f in files:
            p = Path(root) / f
            if p.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                targets.append(p)

    if not targets:
        print("No PNG/JPG images found to optimize.")
        return 0

    print(f"Found {len(targets)} images to optimize...")
    total_orig = sum(p.stat().st_size for p in targets)
    optimized_paths: list[Path] = []

    for path in sorted(targets):
        res = optimize_image(path, delete_source=delete_source)
        if res:
            optimized_paths.append(res)

    total_webp = sum(p.stat().st_size for p in optimized_paths)
    print("---")
    print(f"Total: {total_orig / 1024 / 1024:.2f}MB -> {total_webp / 1024 / 1024:.2f}MB (Saved: {(1 - total_webp / total_orig) * 100:.1f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
