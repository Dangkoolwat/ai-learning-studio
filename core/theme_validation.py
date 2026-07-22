"""Theme design validation helpers for AI Learning Studio."""

from __future__ import annotations

from collections import OrderedDict
import re
from pathlib import Path

from core.errors import BuildError
from core.theme_models import (
    THEME_CATEGORY_ORDER,
    THEME_SECTION_ORDER,
    ThemeDesign,
    ThemeToken,
)


EXPECTED_THEME_ID = "studio-default"
EXPECTED_THEME_NAME = "AI Learning Studio Default"
EXPECTED_THEME_DESCRIPTION = "AI Learning Studio의 기본 교육용 테마"
EXPECTED_THEME_VERSION = 1
EXPECTED_THEME_STATUS = "active"
EXPECTED_THEME_LANG = "ko"
EXPECTED_THEME_SOURCE = "design/studio-default/design.md"

ALLOWED_THEME_STATUSES = {"active", "inactive"}
ALLOWED_THEME_LANGS = {"ko", "en"}
ALLOWED_FRONT_MATTER_FIELDS = {"id", "name", "description", "version", "status", "lang"}

EXPECTED_TOKEN_VALUES = {
    "colors": OrderedDict(
        (
            ("background", "#F3F1ED"),
            ("surface", "#FFFFFF"),
            ("surface-muted", "#EAE7E1"),
            ("text-primary", "#202124"),
            ("text-secondary", "#4F5358"),
            ("text-muted", "#73777C"),
            ("border", "#D7D3CC"),
            ("accent", "#355C7D"),
            ("accent-hover", "#294A67"),
            ("focus", "#2F6FED"),
            ("success", "#2E7D4F"),
            ("warning", "#A86400"),
            ("danger", "#B3261E"),
        )
    ),
    "typography": OrderedDict(
        (
            ("font-family-sans", 'Pretendard, "Noto Sans KR", "Apple SD Gothic Neo", sans-serif'),
            ("font-size-xs", "0.75rem"),
            ("font-size-sm", "0.875rem"),
            ("font-size-md", "1rem"),
            ("font-size-lg", "1.125rem"),
            ("font-size-xl", "1.5rem"),
            ("font-size-2xl", "2rem"),
            ("font-weight-regular", "400"),
            ("font-weight-medium", "500"),
            ("font-weight-semibold", "600"),
            ("line-height-tight", "1.3"),
            ("line-height-normal", "1.6"),
            ("line-height-relaxed", "1.8"),
        )
    ),
    "spacing": OrderedDict(
        (
            ("space-0", "0"),
            ("space-1", "0.25rem"),
            ("space-2", "0.5rem"),
            ("space-3", "0.75rem"),
            ("space-4", "1rem"),
            ("space-5", "1.25rem"),
            ("space-6", "1.5rem"),
            ("space-8", "2rem"),
            ("space-10", "2.5rem"),
            ("space-12", "3rem"),
            ("space-16", "4rem"),
        )
    ),
    "radius": OrderedDict(
        (
            ("radius-sm", "0.375rem"),
            ("radius-md", "0.625rem"),
            ("radius-lg", "1rem"),
            ("radius-pill", "999px"),
        )
    ),
    "shadow": OrderedDict(
        (
            ("shadow-sm", "0 1px 2px rgba(0, 0, 0, 0.08)"),
            ("shadow-md", "0 8px 24px rgba(0, 0, 0, 0.10)"),
        )
    ),
    "layout": OrderedDict(
        (
            ("content-max-width", "1200px"),
            ("navigation-width", "280px"),
            ("page-gutter", "24px"),
            ("header-height", "64px"),
        )
    ),
}

THEME_SOURCE_PATH = Path(EXPECTED_THEME_SOURCE)
COLOR_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
REM_RE = re.compile(r"^[0-9]+(?:\.[0-9]+)?rem$")
PX_RE = re.compile(r"^[0-9]+(?:\.[0-9]+)?px$")
UNITLESS_NUMBER_RE = re.compile(r"^[0-9]+(?:\.[0-9]+)?$")
FONT_WEIGHT_RE = re.compile(r"^[0-9]+$")
THEME_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TOKEN_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SECTION_HEADING_PREFIX = "## "
TOKEN_FENCE = "```theme-tokens"
FENCE_CLOSE = "```"


def parse_theme_design(design_path: Path) -> ThemeDesign:
    source_text = design_path.read_text(encoding="utf-8")
    metadata, body_text = _parse_front_matter(design_path, source_text)
    theme_id = metadata["id"]
    theme_dir = design_path.parent

    if theme_dir.name != theme_id:
        raise BuildError(
            "Validate theme design",
            f"theme directory name must match id {theme_id}",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            field="id",
        )

    _validate_metadata(design_path, metadata)
    tokens_by_category = _parse_token_sections(design_path, theme_id, body_text)
    return ThemeDesign(
        id=metadata["id"],
        name=metadata["name"],
        description=metadata["description"],
        version=metadata["version"],
        status=metadata["status"],
        lang=metadata["lang"],
        source_path=design_path,
        tokens_by_category=tokens_by_category,
    )


def _parse_front_matter(design_path: Path, source_text: str) -> tuple[dict[str, object], str]:
    lines = source_text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise BuildError(
            "Validate theme design",
            "front matter must start with ---",
            path=design_path,
            source_file=design_path,
        )

    closing_index = next((index for index, raw_line in enumerate(lines[1:], start=1) if raw_line.strip() == "---"), None)
    if closing_index is None:
        raise BuildError(
            "Validate theme design",
            "missing closing front matter delimiter",
            path=design_path,
            source_file=design_path,
        )

    metadata: dict[str, object] = {}
    for raw_line in lines[1:closing_index]:
        stripped = raw_line.strip()
        if not stripped:
            raise BuildError(
                "Validate theme design",
                "blank lines are not allowed inside front matter",
                path=design_path,
                source_file=design_path,
            )
        if ":" not in raw_line:
            raise BuildError(
                "Validate theme design",
                "front matter lines must use key: value format",
                path=design_path,
                source_file=design_path,
            )

        key, _, value = raw_line.partition(":")
        key = key.strip()
        value = value.strip()

        if key not in ALLOWED_FRONT_MATTER_FIELDS:
            raise BuildError(
                "Validate theme design",
                f"unknown front matter field: {key}",
                path=design_path,
                source_file=design_path,
                field=key,
            )
        if key in metadata:
            raise BuildError(
                "Validate theme design",
                f"duplicate front matter field: {key}",
                path=design_path,
                source_file=design_path,
                field=key,
            )
        metadata[key] = _coerce_front_matter_value(design_path, key, value)

    body = "\n".join(lines[closing_index + 1 :])
    _validate_front_matter_keys(design_path, metadata)
    return metadata, body


def _coerce_front_matter_value(design_path: Path, key: str, value: str) -> object:
    if key == "version":
        if not value.isdigit():
            raise BuildError(
                "Validate theme design",
                "version must be a positive integer",
                path=design_path,
                source_file=design_path,
                field="version",
            )
        return int(value)
    return value


def _validate_front_matter_keys(design_path: Path, metadata: dict[str, object]) -> None:
    missing = ALLOWED_FRONT_MATTER_FIELDS - set(metadata)
    if missing:
        raise BuildError(
            "Validate theme design",
            f"missing required front matter field: {sorted(missing)[0]}",
            path=design_path,
            source_file=design_path,
            field=sorted(missing)[0],
        )


def _validate_metadata(design_path: Path, metadata: dict[str, object]) -> None:
    theme_id = str(metadata["id"])
    if not THEME_ID_RE.fullmatch(theme_id):
        raise BuildError(
            "Validate theme design",
            "theme id must be lowercase kebab-case",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            field="id",
        )
    if theme_id != EXPECTED_THEME_ID:
        raise BuildError(
            "Validate theme design",
            f"theme id must be {EXPECTED_THEME_ID}",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            field="id",
        )

    if metadata["name"] != EXPECTED_THEME_NAME:
        raise BuildError(
            "Validate theme design",
            f"theme name must be {EXPECTED_THEME_NAME}",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            field="name",
        )
    if metadata["description"] != EXPECTED_THEME_DESCRIPTION:
        raise BuildError(
            "Validate theme design",
            f"theme description must be {EXPECTED_THEME_DESCRIPTION}",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            field="description",
        )
    if metadata["version"] != EXPECTED_THEME_VERSION:
        raise BuildError(
            "Validate theme design",
            f"theme version must be {EXPECTED_THEME_VERSION}",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            field="version",
        )
    if metadata["status"] != EXPECTED_THEME_STATUS:
        raise BuildError(
            "Validate theme design",
            f"theme status must be {EXPECTED_THEME_STATUS}",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            field="status",
        )
    if metadata["lang"] != EXPECTED_THEME_LANG:
        raise BuildError(
            "Validate theme design",
            f"theme lang must be {EXPECTED_THEME_LANG}",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            field="lang",
        )

    if metadata["status"] not in ALLOWED_THEME_STATUSES:
        raise BuildError(
            "Validate theme design",
            "theme status must be active or inactive",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            field="status",
        )
    if metadata["lang"] not in ALLOWED_THEME_LANGS:
        raise BuildError(
            "Validate theme design",
            "theme lang must be ko or en",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            field="lang",
        )


def _parse_token_sections(design_path: Path, theme_id: str, body_text: str) -> dict[str, tuple[ThemeToken, ...]]:
    lines = body_text.splitlines()
    heading_positions: list[tuple[int, str]] = []
    seen_headings: set[str] = set()

    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if not stripped.startswith(SECTION_HEADING_PREFIX):
            continue

        heading_name = stripped[len(SECTION_HEADING_PREFIX) :].strip()
        if heading_name not in THEME_SECTION_ORDER:
            raise BuildError(
                "Validate theme tokens",
                f"unsupported token section: {heading_name}",
                path=design_path,
                source_file=design_path,
                theme_id=theme_id,
                section=heading_name,
            )
        if heading_name in seen_headings:
            raise BuildError(
                "Validate theme tokens",
                f"duplicate token section: {heading_name}",
                path=design_path,
                source_file=design_path,
                theme_id=theme_id,
                section=heading_name,
            )
        seen_headings.add(heading_name)
        heading_positions.append((index, heading_name))

    if not heading_positions:
        raise BuildError(
            "Validate theme tokens",
            "missing required token section",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
        )

    ordered_headings = [heading for _, heading in heading_positions]
    if ordered_headings != list(THEME_SECTION_ORDER):
        missing = [name for name in THEME_SECTION_ORDER if name not in ordered_headings]
        if missing:
            raise BuildError(
                "Validate theme tokens",
                f"missing required token section: {missing[0]}",
                path=design_path,
                source_file=design_path,
                theme_id=theme_id,
                section=missing[0],
            )
        raise BuildError(
            "Validate theme tokens",
            "token sections must appear in the confirmed order",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
        )

    sections: dict[str, tuple[ThemeToken, ...]] = {}
    for position, (start_index, heading_name) in enumerate(heading_positions):
        end_index = heading_positions[position + 1][0] if position + 1 < len(heading_positions) else len(lines)
        section_lines = lines[start_index + 1 : end_index]
        section_name = heading_name
        category = _section_to_category(section_name)
        sections[category] = _parse_token_block(design_path, theme_id, section_name, category, section_lines)

    for category in THEME_CATEGORY_ORDER:
        if category not in sections:
            raise BuildError(
                "Validate theme tokens",
                f"missing required token section: {category}",
                path=design_path,
                source_file=design_path,
                theme_id=theme_id,
                section=category,
            )

    return sections


def _section_to_category(section_name: str) -> str:
    mapping = {
        "Colors": "colors",
        "Typography": "typography",
        "Spacing": "spacing",
        "Radius": "radius",
        "Shadow": "shadow",
        "Layout": "layout",
    }
    return mapping[section_name]


def _parse_token_block(
    design_path: Path,
    theme_id: str,
    section_name: str,
    category: str,
    lines: list[str],
) -> tuple[ThemeToken, ...]:
    block_started = False
    block_closed = False
    parsed_tokens: dict[str, str] = {}
    seen_token_names: set[str] = set()
    seen_css_variables: set[str] = set()
    expected_tokens = EXPECTED_TOKEN_VALUES[category]

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("```"):
            if stripped != TOKEN_FENCE and stripped != FENCE_CLOSE:
                raise BuildError(
                    "Validate theme tokens",
                    "unsupported token fence",
                    path=design_path,
                    source_file=design_path,
                    theme_id=theme_id,
                    section=section_name,
                )
            if stripped == TOKEN_FENCE:
                if block_started:
                    raise BuildError(
                        "Validate theme tokens",
                        f"multiple token fences inside the same section: {section_name}",
                        path=design_path,
                        source_file=design_path,
                        theme_id=theme_id,
                        section=section_name,
                    )
                block_started = True
                continue
            if not block_started or block_closed:
                raise BuildError(
                    "Validate theme tokens",
                    f"unexpected token fence close in section: {section_name}",
                    path=design_path,
                    source_file=design_path,
                    theme_id=theme_id,
                    section=section_name,
                )
            block_closed = True
            continue

        if not block_started:
            continue
        if block_closed:
            if stripped == TOKEN_FENCE:
                raise BuildError(
                    "Validate theme tokens",
                    f"multiple token fences inside the same section: {section_name}",
                    path=design_path,
                    source_file=design_path,
                    theme_id=theme_id,
                    section=section_name,
                )
            raise BuildError(
                "Validate theme tokens",
                f"unexpected content after token fence in section: {section_name}",
                path=design_path,
                source_file=design_path,
                theme_id=theme_id,
                section=section_name,
            )

        token_name, token_value = _parse_token_line(design_path, theme_id, section_name, raw_line)
        if token_name not in expected_tokens:
            raise BuildError(
                "Validate theme tokens",
                f"unknown token: {token_name}",
                path=design_path,
                source_file=design_path,
                theme_id=theme_id,
                section=section_name,
                token_name=token_name,
            )
        if token_name in seen_token_names:
            raise BuildError(
                "Validate theme tokens",
                f"duplicate token name: {token_name}",
                path=design_path,
                source_file=design_path,
                theme_id=theme_id,
                section=section_name,
                token_name=token_name,
            )

        normalized_value = _validate_token_value(
            design_path=design_path,
            theme_id=theme_id,
            section_name=section_name,
            category=category,
            token_name=token_name,
            raw_value=token_value,
        )
        css_variable = f"--als-{token_name}"
        if css_variable in seen_css_variables:
            raise BuildError(
                "Validate theme tokens",
                f"duplicate CSS variable: {css_variable}",
                path=design_path,
                source_file=design_path,
                theme_id=theme_id,
                section=section_name,
                token_name=token_name,
            )
        seen_token_names.add(token_name)
        seen_css_variables.add(css_variable)
        parsed_tokens[token_name] = normalized_value

    if not block_started:
        raise BuildError(
            "Validate theme tokens",
            f"missing required token section: {section_name}",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            section=section_name,
        )
    if not block_closed:
        raise BuildError(
            "Validate theme tokens",
            f"missing closing token fence in section: {section_name}",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            section=section_name,
        )

    expected_names = list(expected_tokens.keys())
    missing_tokens = [name for name in expected_names if name not in seen_token_names]
    if missing_tokens:
        raise BuildError(
            "Validate theme tokens",
            f"missing required token: {missing_tokens[0]}",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            section=section_name,
            token_name=missing_tokens[0],
        )

    if len(parsed_tokens) != len(expected_tokens):
        raise BuildError(
            "Validate theme tokens",
            f"token count for {section_name} is incorrect",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            section=section_name,
        )

    ordered_tokens = [
        ThemeToken(
            category=category,
            name=token_name,
            value=parsed_tokens[token_name],
            css_variable=f"--als-{token_name}",
        )
        for token_name in expected_tokens.keys()
    ]
    return tuple(ordered_tokens)


def _parse_token_line(
    design_path: Path,
    theme_id: str,
    section_name: str,
    raw_line: str,
) -> tuple[str, str]:
    if "=" not in raw_line:
        raise BuildError(
            "Validate theme tokens",
            "malformed token line",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            section=section_name,
        )

    token_name, _, token_value = raw_line.partition("=")
    token_name = token_name.strip()
    token_value = token_value.strip()

    if not token_name or not token_value:
        raise BuildError(
            "Validate theme tokens",
            "malformed token line",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            section=section_name,
        )
    if not TOKEN_NAME_RE.fullmatch(token_name):
        raise BuildError(
            "Validate theme tokens",
            f"malformed token name: {token_name}",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            section=section_name,
            token_name=token_name,
        )

    return token_name, token_value


def _validate_token_value(
    *,
    design_path: Path,
    theme_id: str,
    section_name: str,
    category: str,
    token_name: str,
    raw_value: str,
) -> str:
    if ";" in raw_value:
        raise BuildError(
            "Validate theme tokens",
            "unsafe CSS value contains a semicolon",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            section=section_name,
            token_name=token_name,
            field="value",
        )
    if "!important" in raw_value:
        raise BuildError(
            "Validate theme tokens",
            "unsafe CSS value contains !important",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            section=section_name,
            token_name=token_name,
            field="value",
        )
    if "url(" in raw_value.lower():
        raise BuildError(
            "Validate theme tokens",
            "unsafe CSS value contains a URL reference",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            section=section_name,
            token_name=token_name,
            field="value",
        )
    if "var(" in raw_value.lower():
        raise BuildError(
            "Validate theme tokens",
            "unsafe CSS value contains a CSS variable reference",
            path=design_path,
            source_file=design_path,
            theme_id=theme_id,
            section=section_name,
            token_name=token_name,
            field="value",
        )

    if category == "colors":
        if not COLOR_HEX_RE.fullmatch(raw_value):
            raise BuildError(
                "Validate theme tokens",
                "invalid color token value",
                path=design_path,
                source_file=design_path,
                theme_id=theme_id,
                section=section_name,
                token_name=token_name,
                field="value",
            )
        return raw_value.upper()

    if category == "typography":
        if token_name == "font-family-sans":
            if not raw_value:
                raise BuildError(
                    "Validate theme tokens",
                    "font family must not be empty",
                    path=design_path,
                    source_file=design_path,
                    theme_id=theme_id,
                    section=section_name,
                    token_name=token_name,
                    field="value",
                )
            if not raw_value.endswith("sans-serif"):
                raise BuildError(
                    "Validate theme tokens",
                    "font family must end with a generic sans-serif family",
                    path=design_path,
                    source_file=design_path,
                    theme_id=theme_id,
                    section=section_name,
                    token_name=token_name,
                    field="value",
                )
            if "@" in raw_value:
                raise BuildError(
                    "Validate theme tokens",
                    "unsafe font family value contains @import syntax",
                    path=design_path,
                    source_file=design_path,
                    theme_id=theme_id,
                    section=section_name,
                    token_name=token_name,
                    field="value",
                )
            return raw_value
        if token_name.startswith("font-size-"):
            if not _is_positive_rem_value(raw_value):
                raise BuildError(
                    "Validate theme tokens",
                    "invalid font size unit",
                    path=design_path,
                    source_file=design_path,
                    theme_id=theme_id,
                    section=section_name,
                    token_name=token_name,
                    field="value",
                )
            return raw_value
        if token_name.startswith("font-weight-"):
            if not FONT_WEIGHT_RE.fullmatch(raw_value):
                raise BuildError(
                    "Validate theme tokens",
                    "invalid font weight",
                    path=design_path,
                    source_file=design_path,
                    theme_id=theme_id,
                    section=section_name,
                    token_name=token_name,
                    field="value",
                )
            weight = int(raw_value)
            if weight < 100 or weight > 900 or weight % 100 != 0:
                raise BuildError(
                    "Validate theme tokens",
                    "invalid font weight",
                    path=design_path,
                    source_file=design_path,
                    theme_id=theme_id,
                    section=section_name,
                    token_name=token_name,
                    field="value",
                )
            return raw_value
        if token_name.startswith("line-height-"):
            if not UNITLESS_NUMBER_RE.fullmatch(raw_value):
                raise BuildError(
                    "Validate theme tokens",
                    "invalid line height",
                    path=design_path,
                    source_file=design_path,
                    theme_id=theme_id,
                    section=section_name,
                    token_name=token_name,
                    field="value",
                )
            line_height = float(raw_value)
            if line_height <= 0 or line_height > 3:
                raise BuildError(
                    "Validate theme tokens",
                    "invalid line height",
                    path=design_path,
                    source_file=design_path,
                    theme_id=theme_id,
                    section=section_name,
                    token_name=token_name,
                    field="value",
                )
            return raw_value

    if category == "spacing":
        if token_name == "space-0":
            if raw_value != "0":
                raise BuildError(
                    "Validate theme tokens",
                    "space-0 must equal 0",
                    path=design_path,
                    source_file=design_path,
                    theme_id=theme_id,
                    section=section_name,
                    token_name=token_name,
                    field="value",
                )
            return raw_value
        if not _is_positive_rem_value(raw_value):
            if raw_value.endswith("px"):
                raise BuildError(
                    "Validate theme tokens",
                    "invalid spacing value",
                    path=design_path,
                    source_file=design_path,
                    theme_id=theme_id,
                    section=section_name,
                    token_name=token_name,
                    field="value",
                )
            raise BuildError(
                "Validate theme tokens",
                "invalid spacing value",
                path=design_path,
                source_file=design_path,
                theme_id=theme_id,
                section=section_name,
                token_name=token_name,
                field="value",
            )
        return raw_value

    if category == "radius":
        if token_name == "radius-pill":
            if not _is_positive_px_value(raw_value):
                raise BuildError(
                    "Validate theme tokens",
                    "radius-pill must use positive px",
                    path=design_path,
                    source_file=design_path,
                    theme_id=theme_id,
                    section=section_name,
                    token_name=token_name,
                    field="value",
                )
            return raw_value
        if "%" in raw_value:
            raise BuildError(
                "Validate theme tokens",
                "radius values must not use percentages",
                path=design_path,
                source_file=design_path,
                theme_id=theme_id,
                section=section_name,
                token_name=token_name,
                field="value",
            )
        if not _is_positive_rem_value(raw_value):
            raise BuildError(
                "Validate theme tokens",
                "invalid radius value",
                path=design_path,
                source_file=design_path,
                theme_id=theme_id,
                section=section_name,
                token_name=token_name,
                field="value",
            )
        return raw_value

    if category == "shadow":
        if raw_value not in EXPECTED_TOKEN_VALUES["shadow"].values():
            raise BuildError(
                "Validate theme tokens",
                "invalid shadow token value",
                path=design_path,
                source_file=design_path,
                theme_id=theme_id,
                section=section_name,
                token_name=token_name,
                field="value",
            )
        return raw_value

    if category == "layout":
        if not _is_positive_px_value(raw_value):
            raise BuildError(
                "Validate theme tokens",
                "invalid layout value",
                path=design_path,
                source_file=design_path,
                theme_id=theme_id,
                section=section_name,
                token_name=token_name,
                field="value",
            )
        numeric_value = float(raw_value[:-2])
        bounds = {
            "content-max-width": (600, 2000),
            "navigation-width": (180, 480),
            "page-gutter": (8, 96),
            "header-height": (40, 160),
        }
        lower_bound, upper_bound = bounds[token_name]
        if numeric_value < lower_bound or numeric_value > upper_bound:
            raise BuildError(
                "Validate theme tokens",
                "layout value is out of range",
                path=design_path,
                source_file=design_path,
                theme_id=theme_id,
                section=section_name,
                token_name=token_name,
                field="value",
            )
        return raw_value

    raise BuildError(
        "Validate theme tokens",
        f"unsupported token category: {category}",
        path=design_path,
        source_file=design_path,
        theme_id=theme_id,
        section=section_name,
        token_name=token_name,
    )


def _is_positive_rem_value(value: str) -> bool:
    return bool(REM_RE.fullmatch(value)) and not value.startswith("0rem") and float(value[:-3]) > 0


def _is_positive_px_value(value: str) -> bool:
    return bool(PX_RE.fullmatch(value)) and float(value[:-2]) > 0
