"""Validation helpers for AI Learning Studio page renderers."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import re
from pathlib import Path

from core.component_registry import APPROVED_COMPONENT_IDS
from core.errors import BuildError
from core.renderer_models import (
    APPROVED_CONTROL_BLOCK_LABELS,
    APPROVED_RENDERER_IDS,
    ParsedRendererSource,
    PageRendererContext,
    PageRendererResult,
    PromptBlock,
    PromptFieldBlock,
    RendererControlBlock,
    RendererHeading,
    TimelineStepBlock,
)


KABAB_CASE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CONTROL_FENCE_RE = re.compile(r"^```(prompt|prompt-field|timeline-step)$")
UNRESOLVED_PLACEHOLDER_RE = re.compile(r"{{\s*[a-z0-9_]+\s*}}")


@dataclass(slots=True, frozen=True)
class _ParsedMetadata:
    metadata: dict[str, str]
    body: str | None


def validate_renderer_registry(renderer_registry: dict[str, Callable[[PageRendererContext], PageRendererResult]]) -> None:
    """Validate the central renderer registry."""

    registry_ids = tuple(renderer_registry)
    if len(registry_ids) != len(set(registry_ids)):
        raise BuildError("Register page renderers", "duplicate renderer id was registered")

    approved_ids = set(APPROVED_RENDERER_IDS)
    registry_id_set = set(registry_ids)
    missing = sorted(approved_ids - registry_id_set)
    extra = sorted(registry_id_set - approved_ids)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing renderers: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected renderers: {', '.join(extra)}")
        raise BuildError(
            "Register page renderers",
            "renderer registry does not match the approved renderer ids"
            + (" (" + "; ".join(details) + ")" if details else ""),
        )


def parse_renderer_source(source_text: str, *, source_path: Path) -> ParsedRendererSource:
    """Parse renderer control blocks out of a Markdown source file."""

    lines = source_text.splitlines()
    markdown_lines: list[str] = []
    control_blocks: list[RendererControlBlock] = []
    block_index = 0
    line_index = 0
    in_code_fence = False

    while line_index < len(lines):
        line = lines[line_index]
        stripped = line.strip()

        if in_code_fence:
            markdown_lines.append(line)
            if stripped == "```":
                in_code_fence = False
            line_index += 1
            continue

        if stripped in {f"```{label}" for label in APPROVED_CONTROL_BLOCK_LABELS}:
            label = stripped[3:]
            body_lines: list[str] = []
            line_index += 1
            closed = False
            while line_index < len(lines):
                inner_line = lines[line_index]
                inner_stripped = inner_line.strip()
                if inner_stripped == "```":
                    closed = True
                    break
                if inner_stripped.startswith("```"):
                    raise BuildError(
                        "Parse renderer source",
                        "nested renderer control fences are not allowed",
                        path=source_path,
                        control_block_type=label,
                        control_block_index=block_index,
                    )
                body_lines.append(inner_line)
                line_index += 1
            if not closed:
                raise BuildError(
                    "Parse renderer source",
                    "renderer control fence is not closed",
                    path=source_path,
                    control_block_type=label,
                    control_block_index=block_index,
                )

            body = "\n".join(body_lines)
            if not body.strip():
                raise BuildError(
                    "Parse renderer source",
                    "renderer control block is empty",
                    path=source_path,
                    control_block_type=label,
                    control_block_index=block_index,
                )

            control_blocks.append(RendererControlBlock(label=label, index=block_index, metadata={}, body=body))
            block_index += 1
            line_index += 1
            continue

        if any(stripped.startswith(f"```{label}") for label in APPROVED_CONTROL_BLOCK_LABELS):
            raise BuildError(
                "Parse renderer source",
                "malformed renderer control fence",
                path=source_path,
                control_block_index=block_index,
            )

        if stripped.startswith("```"):
            markdown_lines.append(line)
            in_code_fence = True
            line_index += 1
            continue

        markdown_lines.append(line)
        line_index += 1

    markdown_body = "\n".join(markdown_lines)
    headings = _extract_heading_structure(markdown_body)
    return ParsedRendererSource(
        markdown_body=markdown_body,
        heading_structure=headings,
        source_heading_count=len(headings),
        control_blocks=tuple(control_blocks),
    )


def validate_renderer_context(context: PageRendererContext) -> None:
    """Validate the build-time renderer context."""

    if context.page_type not in APPROVED_RENDERER_IDS:
        raise BuildError(
            "Register page renderers",
            f"unsupported page type: {context.page_type}",
            path=context.source_path,
            page_id=context.page_id,
            page_type=context.page_type,
            page_route=context.page_route,
        )
    if context.page_route == "/" and context.page_type != "landing":
        raise BuildError(
            "Register page renderers",
            "the root route must use the landing renderer",
            path=context.source_path,
            page_id=context.page_id,
            page_type=context.page_type,
            page_route=context.page_route,
            renderer_id=context.page_type,
        )
    if context.page_route != "/" and context.page_type == "landing":
        raise BuildError(
            "Register page renderers",
            "the landing renderer may only be used for the root route",
            path=context.source_path,
            page_id=context.page_id,
            page_type=context.page_type,
            page_route=context.page_route,
            renderer_id=context.page_type,
        )
    if not context.page_title.strip():
        raise BuildError("Register page renderers", "page title must be non-empty", path=context.source_path, page_id=context.page_id)
    if not context.page_description.strip():
        raise BuildError(
            "Register page renderers",
            "page description must be non-empty",
            path=context.source_path,
            page_id=context.page_id,
        )
    if not context.raw_markdown_source.strip():
        raise BuildError("Register page renderers", "page source must not be empty", path=context.source_path, page_id=context.page_id)
    if not context.rendered_markdown_html.strip():
        raise BuildError("Register page renderers", "rendered Markdown HTML must not be empty", path=context.source_path, page_id=context.page_id)
    if not context.markdown_body.strip():
        raise BuildError("Register page renderers", "parsed Markdown body must not be empty", path=context.source_path, page_id=context.page_id)
    if context.page_type != "landing" and not context.page_section.strip():
        raise BuildError(
            "Register page renderers",
            "section pages must declare a page section",
            path=context.source_path,
            page_id=context.page_id,
            page_type=context.page_type,
        )


def validate_renderer_result(context: PageRendererContext, result: PageRendererResult) -> None:
    """Validate renderer output before it reaches the template engine."""

    if result.page_id != context.page_id:
        raise BuildError(
            "Render page",
            "renderer result page id does not match the input context",
            path=context.source_path,
            page_id=context.page_id,
            renderer_id=result.renderer_name,
        )
    if result.page_type != context.page_type:
        raise BuildError(
            "Render page",
            "renderer result page type does not match the input context",
            path=context.source_path,
            page_id=context.page_id,
            page_type=context.page_type,
            renderer_id=result.renderer_name,
        )
    if result.page_route != context.page_route:
        raise BuildError(
            "Render page",
            "renderer result page route does not match the input context",
            path=context.source_path,
            page_id=context.page_id,
            page_type=context.page_type,
            page_route=context.page_route,
            renderer_id=result.renderer_name,
        )
    if result.renderer_name != context.page_type:
        raise BuildError(
            "Render page",
            "renderer result name does not match the page type",
            path=context.source_path,
            page_id=context.page_id,
            page_type=context.page_type,
            page_route=context.page_route,
            renderer_id=result.renderer_name,
        )
    if result.renderer_version != 1:
        raise BuildError(
            "Render page",
            "renderer version must be 1 in this phase",
            path=context.source_path,
            page_id=context.page_id,
            renderer_id=result.renderer_name,
        )
    if result.source_heading_count != context.source_heading_count:
        raise BuildError(
            "Render page",
            "renderer result heading count does not match the parsed source",
            path=context.source_path,
            page_id=context.page_id,
            renderer_id=result.renderer_name,
        )
    if not result.main_html.strip():
        raise BuildError(
            "Render page",
            "renderer result main HTML must not be empty",
            path=context.source_path,
            page_id=context.page_id,
            renderer_id=result.renderer_name,
        )
    if len(result.component_results) < 2:
        raise BuildError(
            "Render page",
            "renderer result must include at least page-intro and page-body component results",
            path=context.source_path,
            page_id=context.page_id,
            renderer_id=result.renderer_name,
        )
    if result.component_results[0].component_id != "page-intro" or result.component_results[1].component_id != "page-body":
        raise BuildError(
            "Render page",
            "renderer result must begin with page-intro and page-body components",
            path=context.source_path,
            page_id=context.page_id,
            renderer_id=result.renderer_name,
        )
    for component_result in result.component_results:
        if component_result.component_id not in APPROVED_COMPONENT_IDS:
            raise BuildError(
                "Render page",
                f"renderer result includes an unknown component: {component_result.component_id}",
                path=context.source_path,
                page_id=context.page_id,
                renderer_id=result.renderer_name,
            )
    _validate_main_html(context, result)


def parse_prompt_block(block: RendererControlBlock) -> PromptBlock:
    """Parse a prompt control block."""

    parsed = _split_key_value_block(block.body, block=block, allowed_keys={"title", "description"}, required_keys={"title"})
    title = parsed.metadata.get("title", "").strip()
    description = parsed.metadata.get("description")
    if not title:
        raise BuildError(
            "Parse renderer source",
            "prompt title must be non-empty",
            control_block_type=block.label,
            control_block_index=block.index,
            control_block_id=title or None,
            invalid_key="title",
        )
    body_lines = parsed.body.splitlines() if parsed.body is not None else []
    body = "\n".join(body_lines)
    if not body.strip():
        raise BuildError(
            "Parse renderer source",
            "prompt body must be non-empty",
            control_block_type=block.label,
            control_block_index=block.index,
            invalid_key="body",
        )
    return PromptBlock(
        title=title,
        description=description.strip() if description is not None and description.strip() else None,
        body=body,
        index=block.index,
    )


def parse_prompt_field_block(block: RendererControlBlock) -> PromptFieldBlock:
    """Parse a prompt-field control block."""

    parsed = _split_key_value_block(
        block.body,
        block=block,
        allowed_keys={"id", "label", "description", "placeholder", "required"},
        required_keys={"id", "label", "description", "required"},
    )
    field_id = parsed.metadata.get("id", "").strip()
    label = parsed.metadata.get("label", "").strip()
    description = parsed.metadata.get("description", "").strip()
    placeholder = parsed.metadata.get("placeholder")
    required_text = parsed.metadata.get("required", "").strip()

    if not field_id:
        raise BuildError(
            "Parse renderer source",
            "prompt field id must be non-empty",
            control_block_type=block.label,
            control_block_index=block.index,
            invalid_key="id",
        )
    if not KABAB_CASE_RE.fullmatch(field_id):
        raise BuildError(
            "Parse renderer source",
            "prompt field id must use lowercase kebab-case",
            control_block_type=block.label,
            control_block_index=block.index,
            control_block_id=field_id,
            invalid_key="id",
        )
    if not label:
        raise BuildError(
            "Parse renderer source",
            "prompt field label must be non-empty",
            control_block_type=block.label,
            control_block_index=block.index,
            control_block_id=field_id,
            invalid_key="label",
        )
    if not description:
        raise BuildError(
            "Parse renderer source",
            "prompt field description must be non-empty",
            control_block_type=block.label,
            control_block_index=block.index,
            control_block_id=field_id,
            invalid_key="description",
        )
    if required_text not in {"true", "false"}:
        raise BuildError(
            "Parse renderer source",
            "prompt field required must be true or false",
            control_block_type=block.label,
            control_block_index=block.index,
            control_block_id=field_id,
            invalid_key="required",
        )
    if placeholder is not None and not placeholder.strip():
        raise BuildError(
            "Parse renderer source",
            "prompt field placeholder must be non-empty when provided",
            control_block_type=block.label,
            control_block_index=block.index,
            control_block_id=field_id,
            invalid_key="placeholder",
        )

    return PromptFieldBlock(
        field_id=field_id,
        label=label,
        description=description,
        placeholder=placeholder.strip() if placeholder is not None else None,
        required=required_text == "true",
        index=block.index,
    )


def parse_timeline_step_block(block: RendererControlBlock) -> TimelineStepBlock:
    """Parse a timeline-step control block."""

    parsed = _split_key_value_block(
        block.body,
        block=block,
        allowed_keys={"id", "title", "description", "result"},
        required_keys={"id", "title", "description", "result"},
    )
    step_id = parsed.metadata.get("id", "").strip()
    title = parsed.metadata.get("title", "").strip()
    description = parsed.metadata.get("description", "").strip()
    result = parsed.metadata.get("result", "").strip()

    if not step_id:
        raise BuildError(
            "Parse renderer source",
            "timeline step id must be non-empty",
            control_block_type=block.label,
            control_block_index=block.index,
            invalid_key="id",
        )
    if not KABAB_CASE_RE.fullmatch(step_id):
        raise BuildError(
            "Parse renderer source",
            "timeline step id must use lowercase kebab-case",
            control_block_type=block.label,
            control_block_index=block.index,
            control_block_id=step_id,
            invalid_key="id",
        )
    if not title:
        raise BuildError(
            "Parse renderer source",
            "timeline step title must be non-empty",
            control_block_type=block.label,
            control_block_index=block.index,
            control_block_id=step_id,
            invalid_key="title",
        )
    if not description:
        raise BuildError(
            "Parse renderer source",
            "timeline step description must be non-empty",
            control_block_type=block.label,
            control_block_index=block.index,
            control_block_id=step_id,
            invalid_key="description",
        )
    if not result:
        raise BuildError(
            "Parse renderer source",
            "timeline step result must be non-empty",
            control_block_type=block.label,
            control_block_index=block.index,
            control_block_id=step_id,
            invalid_key="result",
        )

    return TimelineStepBlock(
        step_id=step_id,
        title=title,
        description=description,
        result=result,
        index=block.index,
    )


def _split_key_value_block(
    body: str,
    *,
    block: RendererControlBlock,
    allowed_keys: set[str],
    required_keys: set[str],
) -> _ParsedMetadata:
    lines = body.splitlines()
    metadata_lines: list[str] = []
    payload_lines: list[str] = []
    separator_seen = False

    for line in lines:
        if block.label == "prompt" and not separator_seen and line.strip() == "---":
            separator_seen = True
            continue
        if separator_seen:
            payload_lines.append(line)
        else:
            metadata_lines.append(line)

    if block.label == "prompt" and not separator_seen:
        raise BuildError(
            "Parse renderer source",
            "prompt block is missing the required separator",
            control_block_type=block.label,
            control_block_index=block.index,
        )
    if block.label == "prompt" and not payload_lines:
        raise BuildError(
            "Parse renderer source",
            "prompt block body must be non-empty",
            control_block_type=block.label,
            control_block_index=block.index,
        )

    metadata = _parse_metadata_lines(
        metadata_lines if block.label == "prompt" else lines,
        block=block,
        allowed_keys=allowed_keys,
        required_keys=required_keys,
    )
    return _ParsedMetadata(metadata=metadata, body="\n".join(payload_lines) if block.label == "prompt" else None)


def _parse_metadata_lines(
    lines: list[str],
    *,
    block: RendererControlBlock,
    allowed_keys: set[str],
    required_keys: set[str],
) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for raw_line in lines:
        if not raw_line.strip():
            raise BuildError(
                "Parse renderer source",
                "blank lines are not allowed in renderer control blocks",
                control_block_type=block.label,
                control_block_index=block.index,
            )
        if ":" not in raw_line:
            raise BuildError(
                "Parse renderer source",
                "renderer control block lines must use key: value format",
                control_block_type=block.label,
                control_block_index=block.index,
            )
        key, _, value = raw_line.partition(":")
        key = key.strip()
        value = value.strip()
        if key not in allowed_keys:
            raise BuildError(
                "Parse renderer source",
                f"unknown renderer control key: {key}",
                control_block_type=block.label,
                control_block_index=block.index,
                invalid_key=key,
            )
        if key in metadata:
            raise BuildError(
                "Parse renderer source",
                f"duplicate renderer control key: {key}",
                control_block_type=block.label,
                control_block_index=block.index,
                invalid_key=key,
            )
        metadata[key] = value

    missing_keys = required_keys - set(metadata)
    if missing_keys:
        missing = sorted(missing_keys)[0]
        raise BuildError(
            "Parse renderer source",
            f"missing required renderer control key: {missing}",
            control_block_type=block.label,
            control_block_index=block.index,
            invalid_key=missing,
        )
    return metadata


def _extract_heading_structure(markdown_text: str) -> tuple[RendererHeading, ...]:
    headings: list[RendererHeading] = []
    in_code_block = False

    for raw_line in markdown_text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if not stripped.startswith("#"):
            continue
        match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if match is None:
            continue
        headings.append(RendererHeading(level=len(match.group(1)), text=match.group(2).strip()))

    return tuple(headings)


def _validate_main_html(context: PageRendererContext, result: PageRendererResult) -> None:
    main_html = result.main_html
    expected_article_class = f'page-content page-content--{context.page_type}'
    expected_section_count = {
        "landing": 0,
        "static-prompt": len([block for block in context.control_blocks if block.label == "prompt"]),
        "prompt-builder": len([block for block in context.control_blocks if block.label == "prompt-field"]),
        "practice-timeline": len([block for block in context.control_blocks if block.label == "timeline-step"]),
    }[context.page_type]

    if main_html.count("<main class=\"site-main\" id=\"main-content\">") != 1:
        raise BuildError(
            "Render page",
            "renderer output must contain exactly one main region",
            path=context.source_path,
            page_id=context.page_id,
            renderer_id=result.renderer_name,
        )
    if main_html.count(f'<article class="{expected_article_class}">') != 1:
        raise BuildError(
            "Render page",
            "renderer output must contain the expected article class",
            path=context.source_path,
            page_id=context.page_id,
            renderer_id=result.renderer_name,
        )
    if main_html.count('<header class="page-intro">') != 1:
        raise BuildError("Render page", "renderer output must contain one page intro", path=context.source_path, page_id=context.page_id, renderer_id=result.renderer_name)
    if main_html.count('<div class="page-body">') != 1:
        raise BuildError("Render page", "renderer output must contain one page body", path=context.source_path, page_id=context.page_id, renderer_id=result.renderer_name)
    if main_html.count('<h1 class="page-title">') != 1:
        raise BuildError("Render page", "renderer output must contain exactly one page-level H1", path=context.source_path, page_id=context.page_id, renderer_id=result.renderer_name)
    if re.search(r"<html\b", main_html, flags=re.IGNORECASE) or re.search(r"<head\b", main_html, flags=re.IGNORECASE) or re.search(r"<body\b", main_html, flags=re.IGNORECASE):
        raise BuildError("Render page", "renderer output must not include shared shell elements", path=context.source_path, page_id=context.page_id, renderer_id=result.renderer_name)
    if "<script" in main_html.lower():
        raise BuildError("Render page", "renderer output must not contain script tags", path=context.source_path, page_id=context.page_id, renderer_id=result.renderer_name)
    if "<style" in main_html.lower():
        raise BuildError("Render page", "renderer output must not contain style tags", path=context.source_path, page_id=context.page_id, renderer_id=result.renderer_name)
    if re.search(r"\sstyle\s*=", main_html, flags=re.IGNORECASE):
        raise BuildError("Render page", "renderer output must not contain inline styles", path=context.source_path, page_id=context.page_id, renderer_id=result.renderer_name)
    if re.search(r"\son[a-z0-9_-]+\s*=", main_html, flags=re.IGNORECASE):
        raise BuildError("Render page", "renderer output must not contain inline event handlers", path=context.source_path, page_id=context.page_id, renderer_id=result.renderer_name)
    if "http://" in main_html.lower() or "https://" in main_html.lower() or "://" in main_html:
        raise BuildError("Render page", "renderer output must not contain external URLs", path=context.source_path, page_id=context.page_id, renderer_id=result.renderer_name)
    if contains_absolute_filesystem_path(main_html):
        raise BuildError("Render page", "renderer output must not contain absolute filesystem paths", path=context.source_path, page_id=context.page_id, renderer_id=result.renderer_name)
    if UNRESOLVED_PLACEHOLDER_RE.search(main_html):
        raise BuildError("Render page", "renderer output must not contain unresolved template placeholders", path=context.source_path, page_id=context.page_id, renderer_id=result.renderer_name)
    if "```prompt" in main_html or "```prompt-field" in main_html or "```timeline-step" in main_html:
        raise BuildError("Render page", "renderer control fences must not remain in the output", path=context.source_path, page_id=context.page_id, renderer_id=result.renderer_name)
    if result.rendered_section_count != expected_section_count:
        raise BuildError(
            "Render page",
            "renderer result section count does not match the parsed control blocks",
            path=context.source_path,
            page_id=context.page_id,
            renderer_id=result.renderer_name,
        )


def contains_absolute_filesystem_path(text: str) -> bool:
    return any(token in text for token in ("/Users/", "/private/", "/var/", "/tmp/"))
