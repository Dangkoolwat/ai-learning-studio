"""Tests for image assets, sizes, formats, and references."""

from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from core.build_pipeline import MAX_IMAGE_ASSET_BYTES, validate_static_asset
from core.errors import BuildError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
PAGES_DIR = PROJECT_ROOT / "pages"
MARKDOWN_IMAGE_RE = re.compile(r"!\[.*?\]\((/assets/images/[^)\s]+)")


class ImageAssetsValidationTests(unittest.TestCase):
    def test_all_image_assets_under_1mb(self) -> None:
        """Ensure every image asset in assets/images is strictly <= 1MB (LCP guarantee)."""
        oversized: list[str] = []
        for img_path in sorted(ASSETS_IMAGES_DIR.rglob("*")):
            if not img_path.is_file() or img_path.name.startswith("."):
                continue
            if img_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".svg"}:
                size = img_path.stat().st_size
                if size > MAX_IMAGE_ASSET_BYTES:
                    oversized.append(f"{img_path.relative_to(PROJECT_ROOT)}: {size / 1024:.1f}KB")

        self.assertEqual(oversized, [], f"Found oversized images (>1MB): {oversized}")

    def test_preview_images_exist_on_disk(self) -> None:
        """Ensure all image paths referenced in frontmatter 'preview:' exist on disk."""
        missing: list[str] = []
        for md_path in sorted(PAGES_DIR.rglob("*.md")):
            text = md_path.read_text(encoding="utf-8")
            if not text.startswith("---"):
                continue
            parts = text.split("---", 2)
            if len(parts) < 3:
                continue
            front_matter = parts[1]
            for line in front_matter.splitlines():
                if line.startswith("preview:"):
                    raw_val = line.split("preview:", 1)[1].strip()
                    entries = [item.strip() for item in raw_val.split(",") if item.strip()]
                    for entry in entries:
                        clean_path = entry.lstrip("/")
                        disk_path = PROJECT_ROOT / clean_path
                        if not disk_path.exists():
                            missing.append(f"{md_path.name} -> {entry} (not found on disk)")

        self.assertEqual(missing, [], f"Missing preview images: {missing}")

    def test_markdown_inline_images_exist_on_disk(self) -> None:
        """Ensure all image paths referenced in markdown inline images exist on disk."""
        missing: list[str] = []
        for md_path in sorted(PAGES_DIR.rglob("*.md")):
            text = md_path.read_text(encoding="utf-8")
            for match in MARKDOWN_IMAGE_RE.finditer(text):
                img_src = match.group(1).split("#")[0].strip()
                clean_path = img_src.lstrip("/")
                disk_path = PROJECT_ROOT / clean_path
                if not disk_path.exists():
                    missing.append(f"{md_path.name} -> {img_src}")

        self.assertEqual(missing, [], f"Missing inline images: {missing}")

    def test_oversized_image_raises_build_error(self) -> None:
        """Ensure validate_static_asset raises BuildError for images exceeding MAX_IMAGE_ASSET_BYTES."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir) / "huge.webp"
            # Write a dummy file larger than 1MB
            tmp_path.write_bytes(b"\x00" * (MAX_IMAGE_ASSET_BYTES + 1024))
            with self.assertRaises(BuildError) as ctx:
                validate_static_asset(tmp_path)
            self.assertIn("exceeds size limit", ctx.exception.message)


if __name__ == "__main__":
    unittest.main()
