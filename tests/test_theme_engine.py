"""Unit tests for theme parser, validation, and generation."""

from pathlib import Path
import shutil
import unittest

from core.theme_generator import build_theme_registry, generate_theme_assets
from core.theme_parser import load_theme_designs


class ThemeEngineTests(unittest.TestCase):
    """Test suite for theme discovery, registry construction, and asset generation."""

    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parent.parent
        self.design_dir = self.repo_root / "design"
        self.test_dist = self.repo_root / ".tmp_theme_test_dist"
        if self.test_dist.exists():
            shutil.rmtree(self.test_dist)

    def tearDown(self) -> None:
        if self.test_dist.exists():
            shutil.rmtree(self.test_dist)

    def test_discover_valid_themes(self) -> None:
        """Ensure all theme JSONs under design/ are valid and discoverable."""
        themes = load_theme_designs(self.design_dir)
        self.assertTrue(len(themes) > 0)

        active_themes = [t for t in themes if t.status == "active"]
        self.assertEqual(len(active_themes), 1, "Exactly one active theme must exist")

    def test_build_theme_registry(self) -> None:
        """Verify theme registry metadata construction."""
        themes = load_theme_designs(self.design_dir)
        registry = build_theme_registry(themes)

        self.assertEqual(registry.version, 1)
        self.assertTrue(any(e.id == registry.active_theme for e in registry.themes))
        reg_dict = registry.to_public_dict()
        self.assertIn("active_theme", reg_dict)
        self.assertIn("themes", reg_dict)

    def test_generate_theme_assets(self) -> None:
        """Verify theme CSS and manifest generation in output directory."""
        themes = load_theme_designs(self.design_dir)
        result = generate_theme_assets(themes, self.test_dist)

        self.assertTrue(len(result.generated_theme_files) > 0)
        self.assertTrue((self.test_dist / "themes" / "themes.json").is_file())


if __name__ == "__main__":
    unittest.main()
