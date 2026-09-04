"""Unit tests for composite and indented list parsing in render_markdown_fragment."""

from pathlib import Path
import unittest

from core.renderers.base import render_markdown_fragment


class CompositeListParserTests(unittest.TestCase):
    """Test suite for indented composite lists (code blocks, paragraphs, nested lists)."""

    def setUp(self) -> None:
        self.dummy_path = Path("test.md")

    def test_flat_ordered_and_unordered_lists(self) -> None:
        """Verify flat lists still render backward-compatibly."""
        md = "- Item A\n- Item B\n\n1. Number 1\n2. Number 2"
        html = render_markdown_fragment(md, source_path=self.dummy_path)
        self.assertIn("<ul><li>Item A</li><li>Item B</li></ul>", html)
        self.assertIn("<ol><li>Number 1</li><li>Number 2</li></ol>", html)

    def test_ordered_list_with_indented_paragraphs(self) -> None:
        """Verify ordered list items with indented paragraphs maintain single <ol>."""
        md = (
            "1. 첫 번째 단계\n"
            "   이것은 첫 번째 단계의 상세 설명입니다.\n"
            "2. 두 번째 단계\n"
            "   이것은 두 번째 단계의 상세 설명입니다.\n"
        )
        html = render_markdown_fragment(md, source_path=self.dummy_path)
        # Should be a single <ol> tag, not two separate <ol> tags
        self.assertEqual(html.count("<ol>"), 1)
        self.assertEqual(html.count("</ol>"), 1)
        self.assertIn("첫 번째 단계", html)
        self.assertIn("첫 번째 단계의 상세 설명입니다", html)
        self.assertIn("두 번째 단계", html)

    def test_ordered_list_with_indented_code_blocks(self) -> None:
        """Verify ordered list items with indented code blocks do not fragment <ol>."""
        md = (
            "1. 터미널에서 도구 설치:\n"
            "   ```bash\n"
            "   npm install -D vitest\n"
            "   ```\n"
            "2. 설정 파일 수정:\n"
            "   ```json\n"
            "   {\"test\": \"vitest\"}\n"
            "   ```\n"
        )
        html = render_markdown_fragment(md, source_path=self.dummy_path)
        # Single <ol> wrapper
        self.assertEqual(html.count("<ol>"), 1)
        self.assertEqual(html.count("</ol>"), 1)
        self.assertIn("<pre><code>", html)
        self.assertIn("npm install -D vitest", html)
        self.assertIn("&quot;test&quot;: &quot;vitest&quot;", html)

    def test_nested_list_inside_list_item(self) -> None:
        """Verify nested unordered list inside ordered list."""
        md = (
            "1. 첫 번째 주제\n"
            "   - 세부 항목 1\n"
            "   - 세부 항목 2\n"
            "2. 두 번째 주제\n"
        )
        html = render_markdown_fragment(md, source_path=self.dummy_path)
        self.assertEqual(html.count("<ol>"), 1)
        self.assertIn("<ul>", html)
        self.assertIn("<li>세부 항목 1</li>", html)


if __name__ == "__main__":
    unittest.main()
