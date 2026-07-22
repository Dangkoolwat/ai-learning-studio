"""Component validation helpers for AI Learning Studio."""

from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
import re
from pathlib import Path

from core.component_models import ComponentSpec
from core.component_registry import APPROVED_COMPONENT_BY_ID, APPROVED_COMPONENT_IDS, APPROVED_COMPONENT_SPECS
from core.errors import BuildError
from core.template_validation import extract_placeholders


PLACEHOLDER_RENDER_RE = re.compile(r"{{\s*[a-z0-9_]+\s*}}")
INLINE_HANDLER_RE = re.compile(r"\son[a-z0-9_-]+\s*=", re.IGNORECASE)
ABSOLUTE_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])(?:/Users/|/private/|/var/|/tmp/)")
DOCUMENT_TAG_RE = re.compile(r"<(?:html|head|body|main)(?:\s|>)", re.IGNORECASE)


class ComponentHTMLInspector(HTMLParser):
    """Collect a simple structural summary for component HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.start_tags: list[tuple[str, dict[str, str]]] = []
        self.end_tags: list[str] = []
        self.text_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.start_tags.append((tag, {name: value or "" for name, value in attrs}))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        self.end_tags.append(tag)

    def handle_data(self, data: str) -> None:
        if data:
            self.text_chunks.append(data)


def validate_component_registry(component_registry: dict[str, ComponentSpec]) -> None:
    """Validate the authoritative component registry."""

    registry_ids = tuple(component_registry)
    if len(registry_ids) != len(set(registry_ids)):
        raise BuildError("Register components", "duplicate component id was registered")

    approved_ids = set(APPROVED_COMPONENT_IDS)
    registry_id_set = set(registry_ids)
    missing = sorted(approved_ids - registry_id_set)
    extra = sorted(registry_id_set - approved_ids)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing components: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected components: {', '.join(extra)}")
        raise BuildError(
            "Register components",
            "component registry does not match the approved component ids"
            + (" (" + "; ".join(details) + ")" if details else ""),
        )

    seen_paths: set[str] = set()
    for spec in APPROVED_COMPONENT_SPECS:
        if spec.version <= 0:
            raise BuildError("Register components", "component version must be a positive integer", path=spec.template_path, field="version")
        if spec.template_path.as_posix() in seen_paths:
            raise BuildError("Register components", f"duplicate component template path: {spec.template_path}", path=spec.template_path)
        seen_paths.add(spec.template_path.as_posix())


def validate_component_template_source(template_path: Path, template_text: str, *, spec: ComponentSpec) -> None:
    """Validate the raw source for one component template."""

    if template_path.suffix != ".html":
        raise BuildError("Load components", "component template files must end in .html", path=template_path)
    if not template_text.strip():
        raise BuildError("Load components", "component template file must not be empty", path=template_path)

    lower_text = template_text.lower()
    if DOCUMENT_TAG_RE.search(template_text):
        raise BuildError("Load components", "component template must not contain document-level tags", path=template_path)
    if "<header class=\"site-header\"" in lower_text or "<nav class=\"site-navigation\"" in lower_text or "<footer class=\"site-footer\"" in lower_text:
        raise BuildError("Load components", "component template must not contain shared shell chrome", path=template_path)
    if "<script" in lower_text:
        raise BuildError("Load components", "component template must not contain script tags", path=template_path)
    if "<style" in lower_text:
        raise BuildError("Load components", "component template must not contain style tags", path=template_path)
    if INLINE_HANDLER_RE.search(template_text):
        raise BuildError("Load components", "component template must not contain inline event handlers", path=template_path)
    if re.search(r"\sstyle\s*=", lower_text):
        raise BuildError("Load components", "component template must not contain inline style attributes", path=template_path)
    if "http://" in lower_text or "https://" in lower_text or "://" in lower_text:
        raise BuildError("Load components", "component template must not contain external URLs", path=template_path)
    if "{%" in template_text or "{#" in template_text or "{{{" in template_text or "}}}" in template_text:
        raise BuildError("Load components", "component template contains unsupported template syntax", path=template_path)
    if "<form" in lower_text or "<input" in lower_text or "<textarea" in lower_text or "<select" in lower_text:
        raise BuildError("Load components", "component template must not contain form controls", path=template_path)
    if "<button" in lower_text and spec.component_id != "prompt-item":
        raise BuildError("Load components", "component template must not contain buttons", path=template_path)

    placeholders = extract_placeholders(template_text, template_path=template_path)
    placeholder_counts = Counter(placeholders)
    allowed_placeholders = tuple(spec.placeholders)
    allowed_set = set(allowed_placeholders)

    unexpected_placeholders = sorted(name for name in placeholder_counts if name not in allowed_set)
    if unexpected_placeholders:
        raise BuildError(
            "Load components",
            f"unknown placeholder: {unexpected_placeholders[0]}",
            path=template_path,
            field=unexpected_placeholders[0],
        )

    missing_placeholders = [name for name in spec.required_placeholders if placeholder_counts.get(name, 0) == 0]
    if missing_placeholders:
        raise BuildError(
            "Load components",
            f"missing required placeholder: {missing_placeholders[0]}",
            path=template_path,
            field=missing_placeholders[0],
        )

    duplicated_required_placeholders = [name for name in spec.required_placeholders if placeholder_counts.get(name, 0) != 1]
    if duplicated_required_placeholders:
        raise BuildError(
            "Load components",
            f"required placeholder must appear exactly once: {duplicated_required_placeholders[0]}",
            path=template_path,
            field=duplicated_required_placeholders[0],
        )


def validate_component_template_output(
    component_id: str,
    template_path: Path,
    html_text: str,
    *,
    spec: ComponentSpec,
    expected_root_tag: str,
    expected_root_class: str,
) -> None:
    """Validate rendered component HTML."""

    if not html_text.strip():
        raise BuildError("Render component", "rendered component HTML must not be empty", path=template_path, field=component_id)
    if PLACEHOLDER_RENDER_RE.search(html_text):
        raise BuildError("Render component", "unresolved component placeholder remains", path=template_path, field=component_id)
    if DOCUMENT_TAG_RE.search(html_text):
        raise BuildError("Render component", "component output must not contain document-level tags", path=template_path, field=component_id)
    if "<script" in html_text.lower():
        raise BuildError("Render component", "script tags are not allowed in component output", path=template_path, field=component_id)
    if "<style" in html_text.lower():
        raise BuildError("Render component", "style tags are not allowed in component output", path=template_path, field=component_id)
    if re.search(r"\sstyle\s*=", html_text, flags=re.IGNORECASE):
        raise BuildError("Render component", "inline style attributes are not allowed in component output", path=template_path, field=component_id)
    if INLINE_HANDLER_RE.search(html_text):
        raise BuildError("Render component", "inline event handlers are not allowed in component output", path=template_path, field=component_id)
    if "http://" in html_text.lower() or "https://" in html_text.lower() or "://" in html_text:
        raise BuildError("Render component", "external URLs are not allowed in component output", path=template_path, field=component_id)
    if ABSOLUTE_PATH_RE.search(html_text):
        raise BuildError("Render component", "component output contains an absolute filesystem path", path=template_path, field=component_id)

    inspector = ComponentHTMLInspector()
    inspector.feed(html_text)
    if not inspector.start_tags:
        raise BuildError("Render component", "component output does not contain a root element", path=template_path, field=component_id)
    root_tag, root_attrs = inspector.start_tags[0]
    if root_tag != expected_root_tag:
        raise BuildError(
            "Render component",
            f"invalid root element for {component_id}",
            path=template_path,
            field=component_id,
        )
    root_class = root_attrs.get("class", "")
    if expected_root_class not in root_class.split():
        raise BuildError(
            "Render component",
            f"invalid root element class for {component_id}",
            path=template_path,
            field=component_id,
        )

    if component_id == "page-intro":
        _validate_page_intro_output(inspector, component_id=component_id, template_path=template_path)
    elif component_id == "page-body":
        _validate_page_body_output(inspector, component_id=component_id, template_path=template_path)
    elif component_id == "prompt-item":
        _validate_prompt_item_output(inspector, component_id=component_id, template_path=template_path)
    elif component_id == "prompt-collection":
        _validate_prompt_collection_output(inspector, component_id=component_id, template_path=template_path)
    elif component_id == "prompt-field":
        _validate_prompt_field_output(inspector, component_id=component_id, template_path=template_path)
    elif component_id == "prompt-builder":
        _validate_prompt_builder_output(inspector, component_id=component_id, template_path=template_path)
    elif component_id == "timeline-step":
        _validate_timeline_step_output(inspector, component_id=component_id, template_path=template_path)
    elif component_id == "practice-timeline":
        _validate_practice_timeline_output(inspector, component_id=component_id, template_path=template_path)


def _validate_page_intro_output(inspector: ComponentHTMLInspector, *, component_id: str, template_path: Path) -> None:
    if sum(tag == "header" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "page intro must contain exactly one header", path=template_path, field=component_id)
    if sum(tag == "h1" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "page intro must contain exactly one h1", path=template_path, field=component_id)
    if sum(tag == "p" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "page intro must contain exactly one description paragraph", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "h1", "page-title"):
        raise BuildError("Render component", "page intro title class is missing", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "p", "page-description"):
        raise BuildError("Render component", "page intro description class is missing", path=template_path, field=component_id)


def _validate_page_body_output(inspector: ComponentHTMLInspector, *, component_id: str, template_path: Path) -> None:
    if sum(tag == "div" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "page body must contain exactly one wrapper", path=template_path, field=component_id)


def _validate_prompt_item_output(inspector: ComponentHTMLInspector, *, component_id: str, template_path: Path) -> None:
    if sum(tag == "article" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "prompt item must contain exactly one article", path=template_path, field=component_id)
    if sum(tag == "header" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "prompt item must contain exactly one header", path=template_path, field=component_id)
    if sum(tag == "h2" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "prompt item must contain exactly one h2", path=template_path, field=component_id)
    if sum(tag == "pre" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "prompt item must contain exactly one pre", path=template_path, field=component_id)
    if sum(tag == "code" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "prompt item must contain exactly one code", path=template_path, field=component_id)
    if sum(tag == "footer" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "prompt item must contain exactly one footer", path=template_path, field=component_id)
    if sum(tag == "p" for tag, _ in inspector.start_tags) not in {0, 1}:
        raise BuildError("Render component", "prompt item description is invalid", path=template_path, field=component_id)
    if sum(tag == "button" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "prompt item must contain exactly one button", path=template_path, field=component_id)
    if sum(tag == "span" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "prompt item must contain exactly one status span", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "h2", "prompt-item__title"):
        raise BuildError("Render component", "prompt item title class is missing", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "article", "prompt-item"):
        raise BuildError("Render component", "prompt item article class is missing", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "pre", "prompt-item__content"):
        raise BuildError("Render component", "prompt item content class is missing", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "footer", "prompt-item__actions"):
        raise BuildError("Render component", "prompt item actions footer class is missing", path=template_path, field=component_id)
    if any(tag == "p" for tag, _ in inspector.start_tags) and not _has_tag_class(inspector, "p", "prompt-item__description"):
        raise BuildError("Render component", "prompt item description class is missing", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "button", "prompt-item__copy-button"):
        raise BuildError("Render component", "prompt item copy button class is missing", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "span", "prompt-item__copy-status"):
        raise BuildError("Render component", "prompt item copy status class is missing", path=template_path, field=component_id)


def _validate_prompt_collection_output(inspector: ComponentHTMLInspector, *, component_id: str, template_path: Path) -> None:
    if sum(tag == "section" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "prompt collection must contain exactly one section", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "section", "prompt-collection"):
        raise BuildError("Render component", "prompt collection class is missing", path=template_path, field=component_id)


def _validate_prompt_field_output(inspector: ComponentHTMLInspector, *, component_id: str, template_path: Path) -> None:
    if sum(tag == "li" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "prompt field must contain exactly one list item", path=template_path, field=component_id)
    if sum(tag == "h2" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "prompt field must contain exactly one label heading", path=template_path, field=component_id)
    if sum(tag == "p" for tag, _ in inspector.start_tags) not in {2, 3}:
        raise BuildError("Render component", "prompt field must contain two or three paragraphs", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "li", "prompt-field"):
        raise BuildError("Render component", "prompt field class is missing", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "h2", "prompt-field__label"):
        raise BuildError("Render component", "prompt field label class is missing", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "p", "prompt-field__description"):
        raise BuildError("Render component", "prompt field description class is missing", path=template_path, field=component_id)
    if sum(tag == "p" for tag, _ in inspector.start_tags) == 3 and not _has_tag_class(inspector, "p", "prompt-field__placeholder"):
        raise BuildError("Render component", "prompt field placeholder class is missing", path=template_path, field=component_id)
    root_attrs = inspector.start_tags[0][1]
    if "data-field-id" not in root_attrs:
        raise BuildError("Render component", "prompt field data-field-id attribute is missing", path=template_path, field=component_id)


def _validate_prompt_builder_output(inspector: ComponentHTMLInspector, *, component_id: str, template_path: Path) -> None:
    if sum(tag == "section" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "prompt builder must contain exactly one section", path=template_path, field=component_id)
    if sum(tag == "ol" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "prompt builder must contain exactly one ordered list", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "section", "prompt-builder"):
        raise BuildError("Render component", "prompt builder class is missing", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "ol", "prompt-builder__fields"):
        raise BuildError("Render component", "prompt builder field list class is missing", path=template_path, field=component_id)


def _validate_timeline_step_output(inspector: ComponentHTMLInspector, *, component_id: str, template_path: Path) -> None:
    if sum(tag == "li" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "timeline step must contain exactly one list item", path=template_path, field=component_id)
    if sum(tag == "h2" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "timeline step must contain exactly one title", path=template_path, field=component_id)
    if sum(tag == "span" for tag, _ in inspector.start_tags) != 2:
        raise BuildError("Render component", "timeline step must contain exactly two spans", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "li", "timeline-step"):
        raise BuildError("Render component", "timeline step class is missing", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "p", "timeline-step__number"):
        raise BuildError("Render component", "timeline step number class is missing", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "div", "timeline-step__content"):
        raise BuildError("Render component", "timeline step content class is missing", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "h2", "timeline-step__title"):
        raise BuildError("Render component", "timeline step title class is missing", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "p", "timeline-step__description"):
        raise BuildError("Render component", "timeline step description class is missing", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "p", "timeline-step__result"):
        raise BuildError("Render component", "timeline step result class is missing", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "span", "timeline-step__result-label"):
        raise BuildError("Render component", "timeline step result label class is missing", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "span", "timeline-step__result-value"):
        raise BuildError("Render component", "timeline step result value class is missing", path=template_path, field=component_id)
    root_attrs = inspector.start_tags[0][1]
    if "data-step-id" not in root_attrs:
        raise BuildError("Render component", "timeline step data-step-id attribute is missing", path=template_path, field=component_id)


def _validate_practice_timeline_output(inspector: ComponentHTMLInspector, *, component_id: str, template_path: Path) -> None:
    if sum(tag == "section" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "practice timeline must contain exactly one section", path=template_path, field=component_id)
    if sum(tag == "ol" for tag, _ in inspector.start_tags) != 1:
        raise BuildError("Render component", "practice timeline must contain exactly one ordered list", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "section", "practice-timeline"):
        raise BuildError("Render component", "practice timeline class is missing", path=template_path, field=component_id)
    if not _has_tag_class(inspector, "ol", "practice-timeline__list"):
        raise BuildError("Render component", "practice timeline list class is missing", path=template_path, field=component_id)


def _has_tag_class(inspector: ComponentHTMLInspector, tag_name: str, class_name: str) -> bool:
    for tag, attrs in inspector.start_tags:
        if tag != tag_name:
            continue
        class_value = attrs.get("class", "")
        if class_name in class_value.split():
            return True
    return False
