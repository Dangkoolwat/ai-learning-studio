"""Landing page renderer for AI Learning Studio."""

from __future__ import annotations

from core.renderer_models import PageRendererContext, PageRendererResult
from core.renderer_validation import validate_renderer_result
from core.renderers.base import build_main_html, build_page_intro_html


RENDERER_NAME = "landing"
RENDERER_VERSION = 1


def render_landing_page(context: PageRendererContext) -> PageRendererResult:
    """Render the root landing page."""

    intro_html = build_page_intro_html(page_title=context.page_title, page_description=context.page_description)
    warning = _heading_warning(context)
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
        ),
        source_heading_count=context.source_heading_count,
        rendered_section_count=0,
        warnings=warning,
    )
    validate_renderer_result(context, result)
    return result


def _heading_warning(context: PageRendererContext) -> tuple[str, ...]:
    if not context.heading_structure:
        return ()
    return ("Markdown headings were normalized below the page intro to keep one page-level H1.",)
