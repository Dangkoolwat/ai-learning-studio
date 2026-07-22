"""Component rendering helpers for AI Learning Studio."""

from __future__ import annotations

from html import escape as escape_html
from pathlib import Path

from core.component_models import (
    COMPONENT_ENGINE_VERSION,
    COMPONENT_VALIDATION_STATUS,
    ComponentRenderResult,
    LoadedComponentTemplates,
    PageBodyComponent,
    PageIntroComponent,
    PracticeTimelineComponent,
    PromptBuilderComponent,
    PromptCollectionComponent,
    PromptFieldComponent,
    PromptItemComponent,
    TimelineStepComponent,
)
from core.component_registry import APPROVED_COMPONENT_BY_ID, APPROVED_COMPONENT_IDS, APPROVED_COMPONENT_SPECS
from core.component_validation import validate_component_registry, validate_component_template_output, validate_component_template_source
from core.errors import BuildError
from core.template_engine import render_placeholder_template


_MODEL_COMPONENT_IDS = {
    PageIntroComponent: "page-intro",
    PageBodyComponent: "page-body",
    PromptCollectionComponent: "prompt-collection",
    PromptItemComponent: "prompt-item",
    PromptBuilderComponent: "prompt-builder",
    PromptFieldComponent: "prompt-field",
    PracticeTimelineComponent: "practice-timeline",
    TimelineStepComponent: "timeline-step",
}

_OUTPUT_ROOTS = {
    "page-intro": ("header", "page-intro"),
    "page-body": ("div", "page-body"),
    "prompt-collection": ("section", "prompt-collection"),
    "prompt-item": ("article", "prompt-item"),
    "prompt-builder": ("section", "prompt-builder"),
    "prompt-field": ("li", "prompt-field"),
    "practice-timeline": ("section", "practice-timeline"),
    "timeline-step": ("li", "timeline-step"),
}


def load_approved_component_templates(repo_root: Path) -> LoadedComponentTemplates:
    """Load and validate the approved component template files."""

    repo_root = repo_root.resolve(strict=False)
    validate_component_registry(APPROVED_COMPONENT_BY_ID)

    templates_by_id: dict[str, str] = {}
    source_files: list[str] = []

    for spec in APPROVED_COMPONENT_SPECS:
        template_path = (repo_root / spec.template_path).resolve(strict=False)
        if repo_root != template_path and repo_root not in template_path.parents:
            raise BuildError("Load components", "component template path escapes the repository root", path=template_path, field=spec.component_id)
        if template_path.suffix != ".html":
            raise BuildError("Load components", "component template files must end in .html", path=template_path, field=spec.component_id)
        if not template_path.is_file():
            raise BuildError("Load components", "required component template file is missing", path=template_path, field=spec.component_id)

        try:
            template_text = template_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise BuildError("Load components", "component template file must be UTF-8 encoded", path=template_path, field=spec.component_id) from exc
        except OSError as exc:
            raise BuildError("Load components", "component template file could not be read", path=template_path, field=spec.component_id) from exc

        validate_component_template_source(template_path, template_text, spec=spec)
        templates_by_id[spec.component_id] = template_text
        source_files.append(spec.template_path.as_posix())

    return LoadedComponentTemplates(
        registry=APPROVED_COMPONENT_SPECS,
        templates_by_id=templates_by_id,
        source_files=tuple(source_files),
    )


def render_component(component: object, templates: LoadedComponentTemplates) -> ComponentRenderResult:
    """Render one validated component model through its template."""

    component_id = _component_id_for_model(component)
    spec = APPROVED_COMPONENT_BY_ID.get(component_id)
    if spec is None:
        raise BuildError("Render component", f"unknown component id: {component_id}", field=component_id)

    template_text = templates.template_by_id(component_id)
    replacements = _component_replacements(component, spec)
    rendered_html = render_placeholder_template(
        template_text,
        template_name=component_id,
        approved_placeholders=spec.placeholders,
        replacements=replacements,
    )
    expected_root = _OUTPUT_ROOTS[component_id]
    validate_component_template_output(
        component_id,
        spec.template_path,
        rendered_html,
        spec=spec,
        expected_root_tag=expected_root[0],
        expected_root_class=expected_root[1],
    )
    return ComponentRenderResult(
        component_id=component_id,
        component_version=spec.version,
        template_logical_path=spec.template_path.as_posix(),
        rendered_html=rendered_html,
        plain_text_field_count=len(spec.plain_text_placeholders),
        trusted_html_field_count=len(spec.trusted_html_placeholders),
        warnings=(),
    )


def render_page_intro_component(component: PageIntroComponent, templates: LoadedComponentTemplates) -> ComponentRenderResult:
    return render_component(component, templates)


def render_page_body_component(component: PageBodyComponent, templates: LoadedComponentTemplates) -> ComponentRenderResult:
    return render_component(component, templates)


def render_prompt_collection_component(component: PromptCollectionComponent, templates: LoadedComponentTemplates) -> ComponentRenderResult:
    return render_component(component, templates)


def render_prompt_item_component(component: PromptItemComponent, templates: LoadedComponentTemplates) -> ComponentRenderResult:
    return render_component(component, templates)


def render_prompt_builder_component(component: PromptBuilderComponent, templates: LoadedComponentTemplates) -> ComponentRenderResult:
    return render_component(component, templates)


def render_prompt_field_component(component: PromptFieldComponent, templates: LoadedComponentTemplates) -> ComponentRenderResult:
    return render_component(component, templates)


def render_practice_timeline_component(component: PracticeTimelineComponent, templates: LoadedComponentTemplates) -> ComponentRenderResult:
    return render_component(component, templates)


def render_timeline_step_component(component: TimelineStepComponent, templates: LoadedComponentTemplates) -> ComponentRenderResult:
    return render_component(component, templates)


def render_prompt_item_description_fragment(description: str | None) -> str:
    if not description:
        return ""
    return f'<p class="prompt-item__description">{escape_html(description)}</p>'


def render_prompt_field_placeholder_fragment(placeholder: str | None) -> str:
    if not placeholder:
        return ""
    return f'<p class="prompt-field__placeholder">{escape_html(placeholder)}</p>'


def _component_id_for_model(component: object) -> str:
    for model_type, component_id in _MODEL_COMPONENT_IDS.items():
        if isinstance(component, model_type):
            return component_id
    raise BuildError("Render component", f"unsupported component model: {type(component).__name__}")


def _component_replacements(component: object, spec) -> dict[str, str]:
    if isinstance(component, PageIntroComponent):
        return {
            "page_title": escape_html(component.page_title),
            "page_description": escape_html(component.page_description),
        }
    if isinstance(component, PageBodyComponent):
        return {"body_html": component.body_html}
    if isinstance(component, PromptCollectionComponent):
        return {"prompt_items_html": component.prompt_items_html}
    if isinstance(component, PromptItemComponent):
        return {
            "prompt_title": escape_html(component.prompt_title),
            "prompt_description_html": component.prompt_description_html,
            "prompt_body": escape_html(component.prompt_body),
        }
    if isinstance(component, PromptBuilderComponent):
        return {"prompt_fields_html": component.prompt_fields_html}
    if isinstance(component, PromptFieldComponent):
        return {
            "field_id": escape_html(component.field_id),
            "field_label": escape_html(component.field_label),
            "field_description": escape_html(component.field_description),
            "field_placeholder_html": component.field_placeholder_html,
            "field_requirement": escape_html(component.field_requirement),
        }
    if isinstance(component, PracticeTimelineComponent):
        return {"timeline_steps_html": component.timeline_steps_html}
    if isinstance(component, TimelineStepComponent):
        return {
            "step_id": escape_html(component.step_id),
            "step_number": escape_html(str(component.step_number)),
            "step_title": escape_html(component.step_title),
            "step_description": escape_html(component.step_description),
            "step_result": escape_html(component.step_result),
        }
    raise BuildError("Render component", f"unsupported component model: {type(component).__name__}")

