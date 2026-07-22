"""Prompt-builder renderer for AI Learning Studio."""

from __future__ import annotations

from core.component_engine import (
    render_page_body_component,
    render_page_intro_component,
    render_prompt_builder_component,
    render_prompt_field_component,
    render_prompt_field_placeholder_fragment,
)
from core.component_models import PageBodyComponent, PageIntroComponent, PromptBuilderComponent, PromptFieldComponent
from core.errors import BuildError
from core.renderer_models import PageRendererContext, PageRendererResult
from core.renderer_validation import parse_prompt_field_block, validate_renderer_result
from core.renderers.base import build_main_html


RENDERER_NAME = "prompt-builder"
RENDERER_VERSION = 1


def render_prompt_builder_page(context: PageRendererContext) -> PageRendererResult:
    """Render a prompt-building worksheet page."""

    field_blocks = [parse_prompt_field_block(block) for block in context.control_blocks if block.label == "prompt-field"]
    if len(field_blocks) < 2:
        raise BuildError(
            "Render page",
            "prompt-builder pages require at least two prompt-field blocks",
            path=context.source_path,
            page_id=context.page_id,
            page_type=context.page_type,
            page_route=context.page_route,
            renderer_id=context.page_type,
        )
    if len(field_blocks) > 12:
        raise BuildError(
            "Render page",
            "prompt-builder pages may not declare more than twelve prompt-field blocks",
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
    field_results = [
        render_prompt_field_component(
            PromptFieldComponent(
                field_id=field_block.field_id,
                field_label=field_block.label,
                field_description=field_block.description,
                field_placeholder_html=render_prompt_field_placeholder_fragment(field_block.placeholder),
                field_requirement="필수 항목" if field_block.required else "선택 항목",
            ),
            context.component_templates,
        )
        for field_block in field_blocks
    ]
    fields_html = "\n".join(result.rendered_html for result in field_results)
    section_result = render_prompt_builder_component(
        PromptBuilderComponent(prompt_fields_html=fields_html),
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
        rendered_section_count=len(field_blocks),
        component_results=(intro_result, body_result, *field_results, section_result),
        warnings=_heading_warning(context),
    )
    validate_renderer_result(context, result)
    return result


def _heading_warning(context: PageRendererContext) -> tuple[str, ...]:
    if not context.heading_structure:
        return ()
    return ("Markdown headings were normalized below the page intro to keep one page-level H1.",)
