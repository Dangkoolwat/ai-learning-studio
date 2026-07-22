"""Practice-timeline renderer for AI Learning Studio."""

from __future__ import annotations

from core.component_engine import (
    render_page_body_component,
    render_page_intro_component,
    render_practice_timeline_component,
    render_timeline_step_component,
)
from core.component_models import PageBodyComponent, PageIntroComponent, PracticeTimelineComponent, TimelineStepComponent
from core.errors import BuildError
from core.renderer_models import PageRendererContext, PageRendererResult
from core.renderer_validation import parse_timeline_step_block, validate_renderer_result
from core.renderers.base import build_main_html


RENDERER_NAME = "practice-timeline"
RENDERER_VERSION = 1


def render_practice_timeline_page(context: PageRendererContext) -> PageRendererResult:
    """Render a practice timeline page."""

    step_blocks = [parse_timeline_step_block(block) for block in context.control_blocks if block.label == "timeline-step"]
    if len(step_blocks) < 2:
        raise BuildError(
            "Render page",
            "practice-timeline pages require at least two timeline-step blocks",
            path=context.source_path,
            page_id=context.page_id,
            page_type=context.page_type,
            page_route=context.page_route,
            renderer_id=context.page_type,
        )
    if len(step_blocks) > 20:
        raise BuildError(
            "Render page",
            "practice-timeline pages may not declare more than twenty timeline-step blocks",
            path=context.source_path,
            page_id=context.page_id,
            page_type=context.page_type,
            page_route=context.page_route,
            renderer_id=context.page_type,
        )
    intro_result = render_page_intro_component(
        PageIntroComponent(page_title=context.page_title, page_description=context.page_description),
        context.component_templates,
    )
    body_result = render_page_body_component(
        PageBodyComponent(body_html=context.rendered_markdown_html),
        context.component_templates,
    )
    step_results = [
        render_timeline_step_component(
            TimelineStepComponent(
                step_id=step_block.step_id,
                step_number=step_number,
                step_title=step_block.title,
                step_description=step_block.description,
                step_result=step_block.result,
            ),
            context.component_templates,
        )
        for step_number, step_block in enumerate(step_blocks, start=1)
    ]
    steps_html = "\n".join(result.rendered_html for result in step_results)
    section_result = render_practice_timeline_component(
        PracticeTimelineComponent(timeline_steps_html=steps_html),
        context.component_templates,
    )
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
            section_html=section_result.rendered_html,
        ),
        source_heading_count=context.source_heading_count,
        rendered_section_count=len(step_blocks),
        component_results=(intro_result, body_result, *step_results, section_result),
        warnings=_heading_warning(context),
    )
    validate_renderer_result(context, result)
    return result


def _heading_warning(context: PageRendererContext) -> tuple[str, ...]:
    if not context.heading_structure:
        return ()
    return ("Markdown headings were normalized below the page intro to keep one page-level H1.",)
