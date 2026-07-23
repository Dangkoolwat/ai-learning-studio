"""Component data models and constants for AI Learning Studio."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar


COMPONENT_ENGINE_VERSION = 1
COMPONENT_VALIDATION_STATUS = "validated"
COMPONENT_TEMPLATE_ROOT = Path("components")
OPTIONAL_COMPONENT_IDS = ("notice",)


@dataclass(slots=True, frozen=True)
class ComponentSpec:
    """An approved human-authored component template."""

    component_id: str
    template_path: Path
    placeholders: tuple[str, ...]
    plain_text_placeholders: tuple[str, ...]
    trusted_html_placeholders: tuple[str, ...]
    required_placeholders: tuple[str, ...]
    version: int

    def placeholder_count(self) -> int:
        return len(self.placeholders)


@dataclass(slots=True, frozen=True)
class LoadedComponentTemplates:
    """Validated component template source loaded from disk."""

    registry: tuple[ComponentSpec, ...]
    templates_by_id: dict[str, str]
    source_files: tuple[str, ...]

    def file_count(self) -> int:
        return len(self.source_files)

    def template_by_id(self, component_id: str) -> str:
        try:
            return self.templates_by_id[component_id]
        except KeyError as exc:  # pragma: no cover - defensive guard
            raise KeyError(component_id) from exc


@dataclass(slots=True, frozen=True)
class PageIntroComponent:
    page_title: str
    page_description: str
    component_id: ClassVar[str] = "page-intro"


@dataclass(slots=True, frozen=True)
class PageBodyComponent:
    body_html: str
    component_id: ClassVar[str] = "page-body"


@dataclass(slots=True, frozen=True)
class PromptCollectionComponent:
    prompt_items_html: str
    component_id: ClassVar[str] = "prompt-collection"


@dataclass(slots=True, frozen=True)
class PromptItemComponent:
    prompt_title: str
    prompt_description_html: str
    prompt_body_html: str
    component_id: ClassVar[str] = "prompt-item"


@dataclass(slots=True, frozen=True)
class PromptBuilderComponent:
    prompt_fields_html: str
    component_id: ClassVar[str] = "prompt-builder"


@dataclass(slots=True, frozen=True)
class PromptFieldComponent:
    field_id: str
    field_label: str
    field_description: str
    field_placeholder_html: str
    field_requirement: str
    component_id: ClassVar[str] = "prompt-field"


@dataclass(slots=True, frozen=True)
class PracticeTimelineComponent:
    timeline_steps_html: str
    component_id: ClassVar[str] = "practice-timeline"


@dataclass(slots=True, frozen=True)
class TimelineStepComponent:
    step_id: str
    step_number: int
    step_title: str
    step_description: str
    step_result: str
    component_id: ClassVar[str] = "timeline-step"


@dataclass(slots=True, frozen=True)
class ComponentRenderResult:
    """Rendered component HTML and its validation summary."""

    component_id: str
    component_version: int
    template_logical_path: str
    rendered_html: str
    plain_text_field_count: int
    trusted_html_field_count: int
    warnings: tuple[str, ...] = field(default_factory=tuple)

