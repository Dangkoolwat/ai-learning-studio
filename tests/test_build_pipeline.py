"""Unit tests for static build pipeline core functions."""

from pathlib import Path
import unittest

from core.build_pipeline import (
    build_robots_txt,
    build_sitemap_xml,
    discover_approved_assets,
    discover_page_sources,
    render_markdown,
    route_to_output_path,
)
from core.page_registry import load_page_registry


class BuildPipelineTests(unittest.TestCase):
    """Test suite for build pipeline utility functions and generation stages."""

    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parent.parent
        self.pages_dir = self.repo_root / "pages"
        self.assets_dir = self.repo_root / "assets"
        self.registry = load_page_registry(self.repo_root / "data")

    def test_discover_page_sources(self) -> None:
        """Verify markdown page source discovery."""
        sources = discover_page_sources(self.pages_dir)
        self.assertTrue(len(sources) > 0)
        self.assertTrue(all(p.suffix == ".md" for p in sources))

    def test_discover_approved_assets(self) -> None:
        """Verify static asset discovery."""
        assets = discover_approved_assets(self.assets_dir)
        self.assertTrue(len(assets) > 0)

    def test_render_markdown(self) -> None:
        """Verify markdown rendering into semantic HTML."""
        sample_md = "# 제목\n\n이것은 **강조된** 본문입니다.\n\n- 항목 1\n- 항목 2"
        html = render_markdown(sample_md, source_path=Path("sample.md"))
        self.assertIn("<h1>제목</h1>", html)
        self.assertIn("<strong>강조된</strong>", html)
        self.assertIn("<ul>", html)
        self.assertIn("<li>항목 1</li>", html)

    def test_route_to_output_path(self) -> None:
        """Verify route translation to filesystem index.html paths."""
        dist = self.repo_root / "dist"
        out_root = route_to_output_path("/", dist)
        self.assertEqual(out_root, dist / "index.html")

        out_sub = route_to_output_path("/image-ai/typography/", dist)
        self.assertEqual(out_sub, dist / "image-ai" / "typography" / "index.html")

    def test_build_sitemap_and_robots(self) -> None:
        """Verify sitemap.xml and robots.txt generation."""
        published = self.registry.published_pages()
        sitemap = build_sitemap_xml(published, site_base_url="https://example.com")
        self.assertIn("<urlset", sitemap)
        self.assertIn("https://example.com/", sitemap)

        robots = build_robots_txt(site_base_url="https://example.com")
        self.assertIn("User-agent: *", robots)
        self.assertIn("Sitemap: https://example.com/sitemap.xml", robots)


if __name__ == "__main__":
    unittest.main()
