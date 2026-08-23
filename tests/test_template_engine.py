"""Unit tests for template loading, context building, and page rendering."""

from pathlib import Path
import unittest

from core.navigation import load_navigation
from core.page_registry import load_page_registry
from core.template_engine import (
    build_body_class,
    load_approved_templates,
    render_placeholder_template,
    route_href_for_output,
)


class TemplateEngineTests(unittest.TestCase):
    """Test suite for HTML template engine operations."""

    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parent.parent
        self.templates = load_approved_templates(self.repo_root)
        self.nav_data = load_navigation(self.repo_root / "data")
        self.registry = load_page_registry(self.repo_root / "data")

    def test_load_approved_templates(self) -> None:
        """Verify all approved templates are properly loaded and cached."""
        self.assertTrue(len(self.templates.base_html) > 0)
        self.assertTrue(len(self.templates.head_html) > 0)
        self.assertTrue(len(self.templates.site_header_html) > 0)
        self.assertTrue(len(self.templates.navigation_html) > 0)
        self.assertTrue(len(self.templates.footer_html) > 0)

    def test_build_body_class(self) -> None:
        """Verify body class name resolution."""
        body_class = build_body_class("image-ai", "static-prompt", "image-ai")
        self.assertIn("page-id-image-ai", body_class)
        self.assertIn("page-section-image-ai", body_class)

    def test_route_href_for_output(self) -> None:
        """Verify relative href link generation across paths."""
        dist_root = self.repo_root / "dist"
        cur = dist_root / "ai-assistant" / "language-tutor-guide" / "index.html"
        href = route_href_for_output(cur, "/image-ai/typography/", dist_root)
        self.assertEqual(href, "../../image-ai/typography/")

    def test_render_placeholder_template(self) -> None:
        """Verify simple placeholder replacement."""
        tpl = "Hello {{ title }}!"
        rendered = render_placeholder_template(
            tpl,
            template_name="test",
            approved_placeholders=("title",),
            replacements={"title": "World"},
        )
        self.assertEqual(rendered, "Hello World!")


if __name__ == "__main__":
    unittest.main()
