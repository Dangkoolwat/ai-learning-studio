"""Practice-timeline renderer for AI Learning Studio."""

from __future__ import annotations

from html import escape as escape_html

from core.renderer_models import PageRendererContext, PageRendererResult
from core.renderer_validation import parse_timeline_step_block, validate_renderer_result
from core.renderers.base import build_main_html, build_page_intro_html


RENDERER_NAME = "practice-timeline"
RENDERER_VERSION = 1


def render_practice_timeline_page(context: PageRendererContext) -> PageRendererResult:
    """Render a practice timeline page."""

    step_blocks = [parse_timeline_step_block(block) for block in context.control_blocks if block.label == "timeline-step"]
    intro_html = build_page_intro_html(page_title=context.page_title, page_description=context.page_description)
    steps_html = "\n".join(_render_timeline_step(step_number, step_block) for step_number, step_block in enumerate(step_blocks, start=1))
    section_html = (
        '<section class="practice-timeline" aria-label="실습 단계">\n'
        '  <ol class="practice-timeline__list">\n'
        f"{steps_html}\n"
        "  </ol>\n"
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
        rendered_section_count=len(step_blocks),
        warnings=_heading_warning(context),
    )
    validate_renderer_result(context, result)
    return result


def _render_timeline_step(step_number: int, step_block) -> str:
    return (
        f'    <li class="timeline-step" data-step-id="{escape_html(step_block.step_id)}">\n'
        f'      <p class="timeline-step__number">{step_number}</p>\n'
        "      <div class=\"timeline-step__content\">\n"
        f'        <h2 class="timeline-step__title">{escape_html(step_block.title)}</h2>\n'
        f'        <p class="timeline-step__description">{escape_html(step_block.description)}</p>\n'
        '        <p class="timeline-step__result">\n'
        '          <span class="timeline-step__result-label">결과물</span>\n'
        f'          <span class="timeline-step__result-value">{escape_html(step_block.result)}</span>\n'
        "        </p>\n"
        "      </div>\n"
        "    </li>"
    )


def _heading_warning(context: PageRendererContext) -> tuple[str, ...]:
    if not context.heading_structure:
        return ()
    return ("Markdown headings were normalized below the page intro to keep one page-level H1.",)
