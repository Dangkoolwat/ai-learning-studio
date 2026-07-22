"""Static-prompt renderer for AI Learning Studio."""

from __future__ import annotations

from html import escape as escape_html

from core.renderer_models import PageRendererContext, PageRendererResult
from core.renderer_validation import parse_prompt_block, validate_renderer_result
from core.renderers.base import build_main_html, build_page_intro_html


RENDERER_NAME = "static-prompt"
RENDERER_VERSION = 1


def render_static_prompt_page(context: PageRendererContext) -> PageRendererResult:
    """Render a static prompt page."""

    prompt_blocks = [parse_prompt_block(block) for block in context.control_blocks if block.label == "prompt"]
    intro_html = build_page_intro_html(page_title=context.page_title, page_description=context.page_description)
    prompt_items_html = "\n".join(_render_prompt_item(prompt_block) for prompt_block in prompt_blocks)
    section_html = (
        '<section class="prompt-collection" aria-label="프롬프트 모음">\n'
        f"{prompt_items_html}\n"
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
        rendered_section_count=len(prompt_blocks),
        warnings=_heading_warning(context),
    )
    validate_renderer_result(context, result)
    return result


def _render_prompt_item(prompt_block) -> str:
    description_html = ""
    if prompt_block.description:
        description_html = f'          <p class="prompt-item__description">{escape_html(prompt_block.description)}</p>\n'
    return (
        "      <article class=\"prompt-item\">\n"
        "        <header class=\"prompt-item__header\">\n"
        f"          <h2 class=\"prompt-item__title\">{escape_html(prompt_block.title)}</h2>\n"
        f"{description_html}"
        "        </header>\n"
        f"        <pre class=\"prompt-item__content\"><code>{escape_html(prompt_block.body)}</code></pre>\n"
        "      </article>"
    )


def _heading_warning(context: PageRendererContext) -> tuple[str, ...]:
    if not context.heading_structure:
        return ()
    return ("Markdown headings were normalized below the page intro to keep one page-level H1.",)
