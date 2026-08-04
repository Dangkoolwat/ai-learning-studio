"""Renderer data models for AI Learning Studio."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.component_models import ComponentRenderResult, LoadedComponentTemplates


RENDERER_ENGINE_VERSION = 1
APPROVED_RENDERER_IDS = ("landing", "static-prompt", "prompt-builder", "practice-timeline", "markdown-prompt")
APPROVED_CONTROL_BLOCK_LABELS = ("prompt", "prompt-field", "timeline-step", "image-slider", "prompt-template")
RENDERER_VALIDATION_STATUS = "validated"


@dataclass(slots=True, frozen=True)
class RendererHeading:
    """A heading discovered in the Markdown source."""

    level: int
    text: str


@dataclass(slots=True, frozen=True)
class RendererControlBlock:
    """A parsed machine-readable fenced block."""

    label: str
    index: int
    metadata: dict[str, str]
    body: str


@dataclass(slots=True, frozen=True)
class ParsedRendererSource:
    """The parsed renderer-specific Markdown source."""

    markdown_body: str
    heading_structure: tuple[RendererHeading, ...]
    source_heading_count: int
    control_blocks: tuple[RendererControlBlock, ...]


@dataclass(slots=True, frozen=True)
class PromptBlock:
    """A validated prompt block."""

    title: str
    description: str | None
    body: str
    index: int
    ai_target: str | None = None


@dataclass(slots=True, frozen=True)
class PromptFieldBlock:
    """A validated prompt-field block."""

    field_id: str
    label: str
    description: str
    placeholder: str | None
    required: bool
    index: int


@dataclass(slots=True, frozen=True)
class PromptTemplateBlock:
    """A validated prompt-template block."""

    body: str
    index: int


@dataclass(slots=True, frozen=True)
class TimelineStepBlock:
    """A validated timeline-step block."""

    step_id: str
    title: str
    description: str
    result: str
    index: int


@dataclass(slots=True, frozen=True)
class ImageSliderSlide:
    """One slide entry for an image slider block."""

    slide_id: str
    image_src: str
    image_alt: str
    title: str
    caption: str


@dataclass(slots=True, frozen=True)
class ImageSliderBlock:
    """A validated image-slider control block."""

    title: str
    description: str | None
    slides: tuple[ImageSliderSlide, ...]
    index: int


@dataclass(slots=True, frozen=True)
class PageRendererContext:
    """Validated build-time data passed to a page renderer."""

    page_id: str
    page_type: str
    page_route: str
    page_section: str
    page_title: str
    page_description: str
    page_lang: str
    source_path: Path
    raw_markdown_source: str
    parsed_front_matter: dict[str, str]
    markdown_body: str
    rendered_markdown_html: str
    heading_structure: tuple[RendererHeading, ...]
    source_heading_count: int
    active_theme_id: str
    control_blocks: tuple[RendererControlBlock, ...]
    component_templates: LoadedComponentTemplates


@dataclass(slots=True, frozen=True)
class PageRendererResult:
    """Validated HTML returned by a page renderer."""

    page_id: str
    page_type: str
    page_route: str
    renderer_name: str
    renderer_version: int
    main_html: str
    source_heading_count: int
    rendered_section_count: int
    component_results: tuple[ComponentRenderResult, ...]
    warnings: tuple[str, ...]
