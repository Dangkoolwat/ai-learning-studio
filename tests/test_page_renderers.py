"""Unit tests for page renderers and dispatcher."""

from pathlib import Path
import unittest

from core.build_pipeline import parse_page_source
from core.component_engine import load_approved_component_templates
from core.page_registry import load_page_registry
from core.page_renderers import APPROVED_RENDERER_IDS, RENDERER_REGISTRY, render_page
from core.renderer_models import PageRendererContext
from core.renderer_validation import parse_renderer_source
from core.renderers.base import render_markdown_fragment


class PageRenderersTests(unittest.TestCase):
    """Test suite for page renderers registry and dispatching."""

    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parent.parent
        self.component_templates = load_approved_component_templates(self.repo_root)
        self.registry = load_page_registry(self.repo_root / "data")

    def test_renderer_registry_completeness(self) -> None:
        """Verify all approved renderer IDs are registered."""
        for renderer_id in APPROVED_RENDERER_IDS:
            self.assertIn(renderer_id, RENDERER_REGISTRY)
            self.assertTrue(callable(RENDERER_REGISTRY[renderer_id]))

    def test_render_static_prompt_page(self) -> None:
        """Verify static-prompt page renderer execution."""
        entry = self.registry.page_by_id("ready-to-use")
        if entry:
            source_path = self.repo_root / entry.source
            page_src = parse_page_source(source_path)
            parsed_renderer = parse_renderer_source(page_src.raw_source_text, source_path=source_path)
            rendered_md_html = render_markdown_fragment(parsed_renderer.markdown_body, source_path=source_path)

            ctx = PageRendererContext(
                page_id=entry.id,
                page_type=entry.type,
                page_route=entry.route,
                page_section=entry.section or "",
                page_title=entry.title,
                page_description=entry.description,
                page_lang=entry.lang,
                source_path=source_path,
                raw_markdown_source=page_src.raw_source_text,
                parsed_front_matter=page_src.front_matter,
                markdown_body=parsed_renderer.markdown_body,
                rendered_markdown_html=rendered_md_html,
                heading_structure=parsed_renderer.heading_structure,
                source_heading_count=parsed_renderer.source_heading_count,
                active_theme_id="studio-default",
                control_blocks=parsed_renderer.control_blocks,
                component_templates=self.component_templates,
            )
            result = render_page(ctx)
            self.assertEqual(result.renderer_name, "static-prompt")
            self.assertTrue(len(result.main_html) > 0)
            self.assertTrue(len(result.component_results) > 0)

    def test_render_prompt_builder_page(self) -> None:
        """Verify prompt-builder page renderer execution."""
        entry = self.registry.page_by_id("ai-assistant-language-tutor")
        if entry:
            source_path = self.repo_root / entry.source
            page_src = parse_page_source(source_path)
            parsed_renderer = parse_renderer_source(page_src.raw_source_text, source_path=source_path)
            rendered_md_html = render_markdown_fragment(parsed_renderer.markdown_body, source_path=source_path)

            ctx = PageRendererContext(
                page_id=entry.id,
                page_type=entry.type,
                page_route=entry.route,
                page_section=entry.section or "",
                page_title=entry.title,
                page_description=entry.description,
                page_lang=entry.lang,
                source_path=source_path,
                raw_markdown_source=page_src.raw_source_text,
                parsed_front_matter=page_src.front_matter,
                markdown_body=parsed_renderer.markdown_body,
                rendered_markdown_html=rendered_md_html,
                heading_structure=parsed_renderer.heading_structure,
                source_heading_count=parsed_renderer.source_heading_count,
                active_theme_id="studio-default",
                control_blocks=parsed_renderer.control_blocks,
                component_templates=self.component_templates,
            )
            result = render_page(ctx)
            self.assertEqual(result.renderer_name, "prompt-builder")
            self.assertIn("prompt-builder", result.main_html)

    def test_render_practice_timeline_page(self) -> None:
        """Verify practice-timeline page renderer execution."""
        sample_timeline_md = """---
registry_id: practice-test
title: 실습 타임라인
description: 단계별 프롬프트 실습
---

# 실습 개요

실습 가이드 본문 내용입니다.

```timeline-step
id: step-1
title: 1단계 시작하기
description: 첫 번째 단계 설명
result: 첫 번째 결과물
```

```timeline-step
id: step-2
title: 2단계 완성하기
description: 두 번째 단계 설명
result: 두 번째 결과물
```
"""
        source_path = self.repo_root / "pages" / "sections" / "practice-test.md"
        parsed_renderer = parse_renderer_source(sample_timeline_md, source_path=source_path)
        rendered_md_html = render_markdown_fragment(parsed_renderer.markdown_body, source_path=source_path)

        ctx = PageRendererContext(
            page_id="practice-test",
            page_type="practice-timeline",
            page_route="/practice-test/",
            page_section="practice",
            page_title="실습 타임라인",
            page_description="단계별 프롬프트 실습",
            page_lang="ko",
            source_path=source_path,
            raw_markdown_source=sample_timeline_md,
            parsed_front_matter={"registry_id": "practice-test", "title": "실습 타임라인"},
            markdown_body=parsed_renderer.markdown_body,
            rendered_markdown_html=rendered_md_html,
            heading_structure=parsed_renderer.heading_structure,
            source_heading_count=parsed_renderer.source_heading_count,
            active_theme_id="studio-default",
            control_blocks=parsed_renderer.control_blocks,
            component_templates=self.component_templates,
        )
        result = render_page(ctx)
        self.assertEqual(result.renderer_name, "practice-timeline")
        self.assertIn("practice-timeline", result.main_html)
        self.assertIn("1단계 시작하기", result.main_html)


if __name__ == "__main__":
    unittest.main()

