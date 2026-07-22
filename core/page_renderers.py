"""Central renderer registry and dispatch for AI Learning Studio."""

from __future__ import annotations

from collections.abc import Callable

from core.errors import BuildError
from core.renderer_models import APPROVED_RENDERER_IDS, PageRendererContext, PageRendererResult
from core.renderer_validation import validate_renderer_context, validate_renderer_registry, validate_renderer_result
from core.renderers import (
    render_landing_page,
    render_practice_timeline_page,
    render_prompt_builder_page,
    render_static_prompt_page,
)


RendererFunction = Callable[[PageRendererContext], PageRendererResult]
RENDERER_REGISTRY: dict[str, RendererFunction] = {}


def register_renderer(renderer_id: str, renderer: RendererFunction) -> None:
    """Register an approved renderer exactly once."""

    if renderer_id not in APPROVED_RENDERER_IDS:
        raise BuildError("Register page renderers", f"unknown renderer id: {renderer_id}", renderer_id=renderer_id)
    if renderer_id in RENDERER_REGISTRY:
        raise BuildError("Register page renderers", f"duplicate renderer id: {renderer_id}", renderer_id=renderer_id)
    RENDERER_REGISTRY[renderer_id] = renderer


register_renderer("landing", render_landing_page)
register_renderer("static-prompt", render_static_prompt_page)
register_renderer("prompt-builder", render_prompt_builder_page)
register_renderer("practice-timeline", render_practice_timeline_page)
validate_renderer_registry(RENDERER_REGISTRY)


def render_page(context: PageRendererContext) -> PageRendererResult:
    """Dispatch a page to exactly one approved renderer."""

    validate_renderer_context(context)
    renderer = RENDERER_REGISTRY.get(context.page_type)
    if renderer is None:
        raise BuildError(
            "Render page",
            f"missing renderer for page type: {context.page_type}",
            path=context.source_path,
            page_id=context.page_id,
            page_type=context.page_type,
            page_route=context.page_route,
            renderer_id=context.page_type,
        )
    result = renderer(context)
    validate_renderer_result(context, result)
    return result
