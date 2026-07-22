"""Landing page renderer for AI Learning Studio."""

from __future__ import annotations

from core.component_engine import render_page_body_component, render_page_intro_component
from core.component_models import PageBodyComponent, PageIntroComponent
from core.renderer_models import PageRendererContext, PageRendererResult
from core.renderer_validation import validate_renderer_result
from core.renderers.base import build_main_html


RENDERER_NAME = "landing"
RENDERER_VERSION = 1


def render_landing_page(context: PageRendererContext) -> PageRendererResult:
    """Render the root landing page."""

    intro_component = PageIntroComponent(page_title=context.page_title, page_description=context.page_description)
    body_component = PageBodyComponent(body_html=context.rendered_markdown_html)
    intro_result = render_page_intro_component(intro_component, context.component_templates)
    body_result = render_page_body_component(body_component, context.component_templates)
    warning = _heading_warning(context)
    result = PageRendererResult(
        page_id=context.page_id,
        page_type=context.page_type,
        page_route=context.page_route,
        renderer_name=RENDERER_NAME,
        renderer_version=RENDERER_VERSION,
        main_html=build_main_html(
            page_type=context.page_type,
            intro_html=intro_result.rendered_html,
            body_html=body_result.rendered_html,
        ),
        source_heading_count=context.source_heading_count,
        rendered_section_count=0,
        component_results=(intro_result, body_result),
        warnings=warning,
    )
    validate_renderer_result(context, result)
    return result


def _heading_warning(context: PageRendererContext) -> tuple[str, ...]:
    if not context.heading_structure:
        return ()
    return ("Markdown headings were normalized below the page intro to keep one page-level H1.",)
