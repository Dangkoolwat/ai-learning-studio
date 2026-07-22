"""Static-prompt renderer for AI Learning Studio."""

from __future__ import annotations

from core.component_engine import (
    render_page_body_component,
    render_page_intro_component,
    render_prompt_collection_component,
    render_prompt_item_component,
    render_prompt_item_description_fragment,
)
from core.component_models import PageBodyComponent, PageIntroComponent, PromptCollectionComponent, PromptItemComponent
from core.errors import BuildError
from core.renderer_models import PageRendererContext, PageRendererResult
from core.renderer_validation import parse_prompt_block, validate_renderer_result
from core.renderers.base import build_main_html


RENDERER_NAME = "static-prompt"
RENDERER_VERSION = 1


def render_static_prompt_page(context: PageRendererContext) -> PageRendererResult:
    """Render a static prompt page."""

    prompt_blocks = [parse_prompt_block(block) for block in context.control_blocks if block.label == "prompt"]
    if not prompt_blocks:
        raise BuildError(
            "Render page",
            "static-prompt pages require at least one prompt block",
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
    prompt_item_results = [
        render_prompt_item_component(
            PromptItemComponent(
                prompt_title=prompt_block.title,
                prompt_description_html=render_prompt_item_description_fragment(prompt_block.description),
                prompt_body=prompt_block.body,
            ),
            context.component_templates,
        )
        for prompt_block in prompt_blocks
    ]
    prompt_items_html = "\n".join(result.rendered_html for result in prompt_item_results)
    section_result = render_prompt_collection_component(
        PromptCollectionComponent(prompt_items_html=prompt_items_html),
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
        rendered_section_count=len(prompt_blocks),
        component_results=(intro_result, body_result, *prompt_item_results, section_result),
        warnings=_heading_warning(context),
    )
    validate_renderer_result(context, result)
    return result


def _heading_warning(context: PageRendererContext) -> tuple[str, ...]:
    if not context.heading_structure:
        return ()
    return ("Markdown headings were normalized below the page intro to keep one page-level H1.",)
