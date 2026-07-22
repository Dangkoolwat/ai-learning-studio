"""Template validation helpers for AI Learning Studio."""

from __future__ import annotations

from collections import Counter
import re
from pathlib import Path

from core.errors import BuildError
from core.template_models import TemplateSpec


PLACEHOLDER_NAME_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
PLACEHOLDER_RE = re.compile(r"{{\s*([a-z0-9_]+)\s*}}")
INLINE_HANDLER_RE = re.compile(r"\son[a-z0-9_-]+\s*=", re.IGNORECASE)


def validate_template_source(template_path: Path, template_text: str, *, spec: TemplateSpec) -> None:
    """Validate the raw source for one approved template file."""

    if template_path.suffix != ".html":
        raise BuildError(
            "Load templates",
            "template files must end in .html",
            path=template_path,
        )
    if not template_text.strip():
        raise BuildError("Load templates", "template file must not be empty", path=template_path)

    lower_text = template_text.lower()
    if "<script" in lower_text:
        raise BuildError("Load templates", "template file must not contain script tags", path=template_path)
    if "<style" in lower_text:
        raise BuildError("Load templates", "template file must not contain style tags", path=template_path)
    if INLINE_HANDLER_RE.search(template_text):
        raise BuildError("Load templates", "template file must not contain inline event handlers", path=template_path)
    if re.search(r"\sstyle\s*=", lower_text):
        raise BuildError("Load templates", "template file must not contain inline style attributes", path=template_path)
    if "http://" in lower_text or "https://" in lower_text or "://" in lower_text:
        raise BuildError("Load templates", "template file must not contain external URLs", path=template_path)
    if "{%" in template_text or "{#" in template_text or "{{{" in template_text or "}}}" in template_text:
        raise BuildError("Load templates", "template file contains unsupported template syntax", path=template_path)

    placeholders = extract_placeholders(template_text, template_path=template_path)
    placeholder_counts = Counter(placeholders)
    allowed_placeholders = tuple(spec.placeholders)
    allowed_placeholders_set = set(allowed_placeholders)

    unexpected_placeholders = sorted(name for name in placeholder_counts if name not in allowed_placeholders_set)
    if unexpected_placeholders:
        raise BuildError(
            "Load templates",
            f"unknown placeholder: {unexpected_placeholders[0]}",
            path=template_path,
            field=unexpected_placeholders[0],
        )

    missing_placeholders = [name for name in allowed_placeholders if placeholder_counts.get(name, 0) == 0]
    if missing_placeholders:
        raise BuildError(
            "Load templates",
            f"missing required placeholder: {missing_placeholders[0]}",
            path=template_path,
            field=missing_placeholders[0],
        )

    repeated_placeholders = [name for name in allowed_placeholders if placeholder_counts[name] != 1]
    if repeated_placeholders:
        raise BuildError(
            "Load templates",
            f"placeholder must appear exactly once: {repeated_placeholders[0]}",
            path=template_path,
            field=repeated_placeholders[0],
        )


def extract_placeholders(template_text: str, *, template_path: Path) -> list[str]:
    """Extract placeholder names and reject malformed syntax."""

    placeholders: list[str] = []
    index = 0
    text_length = len(template_text)

    while index < text_length:
        if template_text.startswith("{{", index):
            end_index = template_text.find("}}", index + 2)
            if end_index == -1:
                raise BuildError("Load templates", "unclosed placeholder", path=template_path)

            raw_placeholder = template_text[index + 2 : end_index]
            if "{{" in raw_placeholder or "}}" in raw_placeholder:
                raise BuildError("Load templates", "nested placeholder is not allowed", path=template_path)

            placeholder_name = raw_placeholder.strip()
            if not placeholder_name or not PLACEHOLDER_NAME_RE.fullmatch(placeholder_name):
                raise BuildError("Load templates", "malformed placeholder", path=template_path)

            placeholders.append(placeholder_name)
            index = end_index + 2
            continue

        if template_text.startswith("}}", index):
            raise BuildError("Load templates", "unexpected closing placeholder", path=template_path)

        index += 1

    return placeholders
