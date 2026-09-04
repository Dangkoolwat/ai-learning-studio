"""Unit tests for static build pipeline core functions."""

from pathlib import Path
import unittest

from core.build_pipeline import (
    build_json_ld_script_html,
    build_robots_txt,
    build_sitemap_xml,
    build_social_meta_html,
    calculate_asset_hash,
    discover_approved_assets,
    discover_page_sources,
    render_markdown,
    resolve_site_base_url,
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

    def test_resolve_site_base_url_platform_agnostic(self) -> None:
        """Verify multi-platform base URL resolution hierarchy."""
        import os
        from unittest.mock import patch

        # 1. Explicit CLI argument takes absolute precedence
        with patch.dict(os.environ, {"AI_STUDIO_SITE_URL": "https://env.com", "CF_PAGES_URL": "https://cf.com"}):
            self.assertEqual(resolve_site_base_url("https://cli.com/"), "https://cli.com")

        # 2. General environment variable (AI_STUDIO_SITE_URL)
        with patch.dict(os.environ, {"AI_STUDIO_SITE_URL": "https://studio.example.org/"}, clear=True):
            self.assertEqual(resolve_site_base_url(), "https://studio.example.org")

        # 3. Cloudflare Pages (CF_PAGES_URL)
        with patch.dict(os.environ, {"CF_PAGES_URL": "https://cf-test.pages.dev"}, clear=True):
            self.assertEqual(resolve_site_base_url(), "https://cf-test.pages.dev")

        # 4. Netlify (URL)
        with patch.dict(os.environ, {"URL": "https://netlify-test.netlify.app"}, clear=True):
            self.assertEqual(resolve_site_base_url(), "https://netlify-test.netlify.app")

        # 5. Vercel (VERCEL_PROJECT_PRODUCTION_URL)
        with patch.dict(os.environ, {"VERCEL_PROJECT_PRODUCTION_URL": "custom.vercel.app"}, clear=True):
            self.assertEqual(resolve_site_base_url(), "https://custom.vercel.app")

        # 6. Unset returns None for offline local builds
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(resolve_site_base_url())

    def test_build_social_meta_html(self) -> None:
        """Verify Open Graph and Twitter Card social metadata generation."""
        meta_with_url = build_social_meta_html(
            site_base_url="https://example.com",
            page_title="테스트 페이지",
            page_description="테스트 설명문",
            route="/ai-practice/",
        )
        self.assertIn('property="og:url" content="https://example.com/ai-practice/"', meta_with_url)
        self.assertIn('property="og:image" content="https://example.com/assets/images/og-cover.png"', meta_with_url)
        self.assertIn('name="twitter:card" content="summary_large_image"', meta_with_url)
        self.assertIn('name="twitter:title" content="테스트 페이지"', meta_with_url)
        self.assertIn('name="twitter:image" content="https://example.com/assets/images/og-cover.png"', meta_with_url)

        meta_without_url = build_social_meta_html(
            site_base_url=None,
            page_title="로컬 페이지",
            page_description="로컬 설명",
            route="/",
        )
        self.assertIn('name="twitter:card" content="summary_large_image"', meta_without_url)
        self.assertIn('name="twitter:title" content="로컬 페이지"', meta_without_url)
        self.assertNotIn('property="og:url"', meta_without_url)
        self.assertNotIn('property="og:image"', meta_without_url)

    def test_calculate_asset_hash(self) -> None:
        """Verify content-based 8-character hex hash calculation."""
        css_file = self.repo_root / "assets" / "css" / "site.css"
        css_hash = calculate_asset_hash(css_file)
        self.assertEqual(len(css_hash), 8)
        self.assertTrue(all(c in "0123456789abcdef" for c in css_hash))

        # Missing file fallback
        missing_file = self.repo_root / "assets" / "non-existent-file.css"
        self.assertEqual(calculate_asset_hash(missing_file), "1")

    def test_build_json_ld_script_html(self) -> None:
        """Verify Schema.org JSON-LD structured data for home and subpages."""
        from core.navigation import load_navigation

        navigation = load_navigation(self.repo_root / "data")
        registry = load_page_registry(self.repo_root / "data")

        # 1. Root page has WebSite schema
        root_page = next(p for p in registry.pages if p.route == "/")
        root_json_ld = build_json_ld_script_html(
            site_base_url="https://example.com",
            page=root_page,
            navigation=navigation,
        )
        self.assertIn('"@type": "WebSite"', root_json_ld)
        self.assertIn('"url": "https://example.com/"', root_json_ld)

        # 2. Subpage has BreadcrumbList and LearningResource schemas
        subpage = next(p for p in registry.pages if p.route == "/ai-practice/vacation-plan-basic/")
        subpage_json_ld = build_json_ld_script_html(
            site_base_url="https://example.com",
            page=subpage,
            navigation=navigation,
        )
        self.assertIn('"@type": "BreadcrumbList"', subpage_json_ld)
        self.assertIn('"@type": "LearningResource"', subpage_json_ld)
        self.assertIn('"url": "https://example.com/ai-practice/vacation-plan-basic/"', subpage_json_ld)


if __name__ == "__main__":
    unittest.main()
