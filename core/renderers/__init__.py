"""Approved page renderer implementations for AI Learning Studio."""

from __future__ import annotations

from core.renderers.landing import render_landing_page
from core.renderers.practice_timeline import render_practice_timeline_page
from core.renderers.prompt_builder import render_prompt_builder_page
from core.renderers.static_prompt import render_static_prompt_page
from core.renderers.markdown_prompt import render_markdown_prompt_page


__all__ = (
    "render_landing_page",
    "render_static_prompt_page",
    "render_markdown_prompt_page",
    "render_prompt_builder_page",
    "render_practice_timeline_page",
)
