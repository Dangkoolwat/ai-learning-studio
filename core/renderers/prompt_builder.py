"""Prompt-builder renderer for AI Learning Studio."""

from __future__ import annotations

from html import escape as escape_html

from core.renderer_models import PageRendererContext, PageRendererResult
from core.renderer_validation import parse_prompt_field_block, validate_renderer_result
from core.renderers.base import build_main_html, build_page_intro_html


RENDERER_NAME = "prompt-builder"
RENDERER_VERSION = 1


def render_prompt_builder_page(context: PageRendererContext) -> PageRendererResult:
    """Render a prompt-building worksheet page."""

    field_blocks = [parse_prompt_field_block(block) for block in context.control_blocks if block.label == "prompt-field"]
    intro_html = build_page_intro_html(page_title=context.page_title, page_description=context.page_description)
    fields_html = "\n".join(_render_prompt_field(field_block) for field_block in field_blocks)
    section_html = (
        '<section class="prompt-builder" aria-label="프롬프트 작성 항목">\n'
        f'  <ol class="prompt-builder__fields">\n{fields_html}\n  </ol>\n'
        "</section>"
    )
    result = PageRendererResult(
        page_id=context.page_id,
        page_type=context.page_type,
        page_route=context.page_route,
        renderer_name=RENDERER_NAME,
        renderer_version=RENDERER_VERSION,
        main_html=build_main_html(
            page_type=context.page_type,
            intro_html=intro_html,
            body_html=context.rendered_markdown_html,
            section_html=section_html,
        ),
        source_heading_count=context.source_heading_count,
        rendered_section_count=len(field_blocks),
        warnings=_heading_warning(context),
    )
    validate_renderer_result(context, result)
    return result


def _render_prompt_field(field_block) -> str:
    placeholder_html = ""
    if field_block.placeholder:
        placeholder_html = f'          <p class="prompt-field__placeholder">예시: {escape_html(field_block.placeholder)}</p>\n'
    requirement_text = "필수 항목" if field_block.required else "선택 항목"
    return (
        f'    <li class="prompt-field" data-field-id="{escape_html(field_block.field_id)}">\n'
        f'      <h2 class="prompt-field__label">{escape_html(field_block.label)}</h2>\n'
        f'      <p class="prompt-field__description">{escape_html(field_block.description)}</p>\n'
        f"{placeholder_html}"
        f'      <p class="prompt-field__requirement">{requirement_text}</p>\n'
        "    </li>"
    )


def _heading_warning(context: PageRendererContext) -> tuple[str, ...]:
    if not context.heading_structure:
        return ()
    return ("Markdown headings were normalized below the page intro to keep one page-level H1.",)
