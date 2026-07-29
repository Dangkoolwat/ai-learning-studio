"""Prompt-builder renderer for AI Learning Studio."""

from __future__ import annotations

from core.component_engine import (
    render_image_slider_component,
    render_page_body_component,
    render_page_intro_component,
    render_prompt_builder_component,
    render_prompt_field_component,
    render_prompt_field_placeholder_fragment,
)
from core.component_models import PageBodyComponent, PageIntroComponent, PromptBuilderComponent, PromptFieldComponent
from core.errors import BuildError
from core.renderer_models import PageRendererContext, PageRendererResult
from core.renderer_validation import parse_prompt_field_block, parse_prompt_template_block, validate_renderer_result, parse_image_slider_block
from core.renderers.base import build_main_html
from core.renderers.static_prompt import _build_ai_badges_and_actions, _parse_preview_blocks, _build_image_slider_component


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
    slider_blocks = _parse_preview_blocks(context) or [
        parse_image_slider_block(block) for block in context.control_blocks if block.label == "image-slider"
    ]
    intro_result = render_page_intro_component(
        PageIntroComponent(page_title=context.page_title, page_description=context.page_description),
        context.component_templates,
    )
    body_result = render_page_body_component(
        PageBodyComponent(body_html=context.rendered_markdown_html),
        context.component_templates,
    )
    slider_results = [
        render_image_slider_component(_build_image_slider_component(block), context.component_templates)
        for block in slider_blocks
    ]
    field_results = [
        render_prompt_field_component(
            PromptFieldComponent(
                field_id=field_block.field_id,
                field_label=field_block.label,
                field_description=field_block.description,
                field_placeholder_html=render_prompt_field_placeholder_fragment(field_block.placeholder),
                field_requirement="필수 항목" if field_block.required else "",
            ),
            context.component_templates,
        )
        for field_block in field_blocks
    ]
    fields_html = "\n".join(result.rendered_html for result in field_results)
    
    template_blocks = [parse_prompt_template_block(block) for block in context.control_blocks if block.label == "prompt-template"]
    prompt_template_html = template_blocks[0].body if template_blocks else ""
    
    page_ai_target_str = context.parsed_front_matter.get("ai_target", "").strip()
    block_targets = [t.strip() for t in page_ai_target_str.split(",") if t.strip()] if page_ai_target_str else []
    ai_badges_block, ai_actions_block = _build_ai_badges_and_actions(block_targets)

    section_result = render_prompt_builder_component(
        PromptBuilderComponent(
            prompt_fields_html=fields_html,
            prompt_template_html=prompt_template_html,
            ai_badges_html=ai_badges_block,
            ai_actions_html=ai_actions_block,
        ),
        context.component_templates,
    )
    top_preview_html = "\n".join(result.rendered_html for result in slider_results)
    result = PageRendererResult(
        page_id=context.page_id,
        page_type=context.page_type,
        page_route=context.page_route,
        renderer_name=RENDERER_NAME,
        renderer_version=RENDERER_VERSION,
        main_html=build_main_html(
            page_type=context.page_type,
            intro_html=intro_result.rendered_html,
            body_html="\n".join(part for part in (top_preview_html, body_result.rendered_html) if part),
            section_html=section_result.rendered_html,
        ),
        source_heading_count=context.source_heading_count,
        rendered_section_count=len(field_blocks) + len(slider_blocks),
        component_results=(intro_result, body_result, *slider_results, *field_results, section_result),
        warnings=_heading_warning(context),
    )
    validate_renderer_result(context, result)
    return result


def _heading_warning(context: PageRendererContext) -> tuple[str, ...]:
    if not context.heading_structure:
        return ()
    return ("Markdown headings were normalized below the page intro to keep one page-level H1.",)
