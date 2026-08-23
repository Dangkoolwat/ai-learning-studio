"""Unit tests for UI component engine and template rendering."""

from pathlib import Path
import unittest

from core.component_engine import (
    load_approved_component_templates,
    render_component,
)
from core.component_models import (
    PageIntroComponent,
    PromptBuilderComponent,
    PromptItemComponent,
)
from core.component_registry import APPROVED_COMPONENT_BY_ID
from core.component_validation import validate_component_registry


class ComponentEngineTests(unittest.TestCase):
    """Test suite for component loading and model-to-HTML rendering."""

    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parent.parent
        self.component_templates = load_approved_component_templates(self.repo_root)

    def test_component_registry_integrity(self) -> None:
        """Validate all registered component definitions."""
        validate_component_registry(APPROVED_COMPONENT_BY_ID)
        self.assertIn("prompt-item", APPROVED_COMPONENT_BY_ID)
        self.assertIn("prompt-builder", APPROVED_COMPONENT_BY_ID)
        self.assertIn("page-intro", APPROVED_COMPONENT_BY_ID)

    def test_render_page_intro_component(self) -> None:
        """Verify PageIntro component HTML structure."""
        comp = PageIntroComponent(
            page_title="테스트 제목",
            page_description="테스트 설명글입니다.",
        )
        res = render_component(comp, self.component_templates)
        self.assertEqual(res.component_id, "page-intro")
        self.assertIn("테스트 제목", res.rendered_html)
        self.assertIn("테스트 설명글입니다.", res.rendered_html)

    def test_render_prompt_item_component(self) -> None:
        """Verify PromptItem component HTML structure."""
        comp = PromptItemComponent(
            prompt_title="기본 프롬프트",
            prompt_description_html='<p class="prompt-item__description">프롬프트 설명</p>',
            prompt_body_html="프롬프트 본문 내용",
            prompt_actions_html='<footer class="prompt-item__actions"><button type="button" class="prompt-item__copy-button" data-prompt-copy>복사</button><span class="prompt-item__copy-status"></span></footer>',
            prompt_source_html="<span>출처: Gemini</span>",
        )
        res = render_component(comp, self.component_templates)
        self.assertEqual(res.component_id, "prompt-item")
        self.assertIn("기본 프롬프트", res.rendered_html)
        self.assertIn("프롬프트 본문 내용", res.rendered_html)

    def test_render_prompt_builder_component(self) -> None:
        """Verify PromptBuilder component HTML structure."""
        comp = PromptBuilderComponent(
            prompt_fields_html="<li class='prompt-field'>Field</li>",
            prompt_template_html="주제: [[topic]]",
            prompt_source_html="<span>출처: ChatGPT</span>",
        )
        res = render_component(comp, self.component_templates)
        self.assertEqual(res.component_id, "prompt-builder")
        self.assertIn("prompt-builder", res.rendered_html)
        self.assertIn("주제: [[topic]]", res.rendered_html)


if __name__ == "__main__":
    unittest.main()
