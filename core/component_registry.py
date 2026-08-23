"""Approved component registry for AI Learning Studio."""

from __future__ import annotations

from pathlib import Path

from core.component_models import ComponentSpec


APPROVED_COMPONENT_SPECS = (
    ComponentSpec(
        component_id="page-intro",
        template_path=Path("components/page-intro.html"),
        placeholders=("page_title", "page_description"),
        plain_text_placeholders=("page_title", "page_description"),
        trusted_html_placeholders=(),
        required_placeholders=("page_title", "page_description"),
        version=1,
    ),
    ComponentSpec(
        component_id="page-body",
        template_path=Path("components/page-body.html"),
        placeholders=("body_html",),
        plain_text_placeholders=(),
        trusted_html_placeholders=("body_html",),
        required_placeholders=("body_html",),
        version=1,
    ),
    ComponentSpec(
        component_id="prompt-collection",
        template_path=Path("components/prompt-collection.html"),
        placeholders=("prompt_items_html",),
        plain_text_placeholders=(),
        trusted_html_placeholders=("prompt_items_html",),
        required_placeholders=("prompt_items_html",),
        version=1,
    ),
    ComponentSpec(
        component_id="prompt-item",
        template_path=Path("components/prompt-item.html"),
        placeholders=("prompt_title", "prompt_description_html", "prompt_body_html", "prompt_actions_html", "prompt_preview_html", "prompt_badges_html", "prompt_source_html"),
        plain_text_placeholders=("prompt_title",),
        trusted_html_placeholders=("prompt_description_html", "prompt_body_html", "prompt_actions_html", "prompt_preview_html", "prompt_badges_html", "prompt_source_html"),
        required_placeholders=("prompt_title", "prompt_description_html", "prompt_body_html"),
        version=1,
    ),
    ComponentSpec(
        component_id="prompt-builder",
        template_path=Path("components/prompt-builder.html"),
        placeholders=("prompt_fields_html", "prompt_template_html", "ai_badges_html", "ai_actions_html", "prompt_source_html"),
        plain_text_placeholders=("prompt_template_html",),
        trusted_html_placeholders=("prompt_fields_html", "ai_badges_html", "ai_actions_html", "prompt_source_html"),
        required_placeholders=("prompt_fields_html", "prompt_template_html"),
        version=1,
    ),
    ComponentSpec(
        component_id="prompt-field",
        template_path=Path("components/prompt-field.html"),
        placeholders=(
            "field_id",
            "field_label",
            "field_description",
            "field_placeholder_html",
            "field_requirement",
        ),
        plain_text_placeholders=("field_id", "field_label", "field_description", "field_requirement"),
        trusted_html_placeholders=("field_placeholder_html",),
        required_placeholders=(
            "field_id",
            "field_label",
            "field_description",
            "field_placeholder_html",
            "field_requirement",
        ),
        version=1,
    ),
    ComponentSpec(
        component_id="practice-timeline",
        template_path=Path("components/practice-timeline.html"),
        placeholders=("timeline_steps_html",),
        plain_text_placeholders=(),
        trusted_html_placeholders=("timeline_steps_html",),
        required_placeholders=("timeline_steps_html",),
        version=1,
    ),
    ComponentSpec(
        component_id="timeline-step",
        template_path=Path("components/timeline-step.html"),
        placeholders=("step_id", "step_number", "step_title", "step_description", "step_result"),
        plain_text_placeholders=("step_id", "step_number", "step_title", "step_description", "step_result"),
        trusted_html_placeholders=(),
        required_placeholders=("step_id", "step_number", "step_title", "step_description", "step_result"),
        version=1,
    ),
    ComponentSpec(
        component_id="image-slider",
        template_path=Path("components/image-slider.html"),
        placeholders=("slider_title", "slider_description", "slider_slides_html"),
        plain_text_placeholders=("slider_title", "slider_description"),
        trusted_html_placeholders=("slider_slides_html",),
        required_placeholders=("slider_title", "slider_description", "slider_slides_html"),
        version=1,
    ),
)

APPROVED_COMPONENT_IDS = tuple(spec.component_id for spec in APPROVED_COMPONENT_SPECS)
APPROVED_COMPONENT_PATHS = tuple(spec.template_path.as_posix() for spec in APPROVED_COMPONENT_SPECS)
APPROVED_COMPONENT_BY_ID = {spec.component_id: spec for spec in APPROVED_COMPONENT_SPECS}
