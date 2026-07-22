"""Shared renderer helpers for AI Learning Studio."""

from __future__ import annotations

from html import escape as escape_html
from pathlib import Path
import re
from textwrap import indent

from core.errors import BuildError


INLINE_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def render_markdown_fragment(markdown_text: str, *, source_path: Path) -> str:
    """Render the limited Markdown subset used by the project."""

    blocks: list[str] = []
    paragraph_lines: list[str] = []
    list_items: list[str] = []
    code_lines: list[str] = []
    in_code_block = False

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        text = " ".join(line.strip() for line in paragraph_lines if line.strip())
        if text:
            blocks.append(f"<p>{_render_inline_markup(text, source_path=source_path)}</p>")
        paragraph_lines.clear()

    def flush_list() -> None:
        if not list_items:
            return
        items = "".join(f"<li>{item}</li>" for item in list_items)
        blocks.append(f"<ul>{items}</ul>")
        list_items.clear()

    for raw_line in markdown_text.splitlines():
        stripped = raw_line.strip()

        if in_code_block:
            if stripped.startswith("```"):
                code_html = escape_html("\n".join(code_lines))
                blocks.append(f"<pre><code>{code_html}</code></pre>")
                code_lines.clear()
                in_code_block = False
            else:
                code_lines.append(raw_line)
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            in_code_block = True
            continue
        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        heading_level, heading_text = _parse_heading(stripped)
        if heading_level is not None:
            flush_paragraph()
            flush_list()
            rendered_level = min(heading_level + 1, 6)
            blocks.append(f"<h{rendered_level}>{escape_html(heading_text)}</h{rendered_level}>")
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            list_items.append(_render_inline_markup(stripped[2:].strip(), source_path=source_path))
            continue

        flush_list()
        paragraph_lines.append(raw_line)

    if in_code_block:
        raise BuildError("Render Markdown", "missing closing code fence", path=source_path)

    flush_paragraph()
    flush_list()
    return "\n".join(blocks)


def build_page_intro_html(*, page_title: str, page_description: str) -> str:
    """Build the shared page intro fragment."""

    description_html = f'    <p class="page-description">{escape_html(page_description)}</p>\n'
    return (
        "    <header class=\"page-intro\">\n"
        f"      <h1>{escape_html(page_title)}</h1>\n"
        f"{description_html}"
        "    </header>"
    )


def build_main_html(*, page_type: str, intro_html: str, body_html: str, section_html: str | None = None) -> str:
    """Build the renderer-owned main region."""

    parts = [
        '<main class="site-main" id="main-content">',
        f'  <article class="page-content page-content--{page_type}">',
        indent(intro_html, "    "),
        "",
        indent(body_html, "    "),
    ]
    if section_html:
        parts.extend(["", indent(section_html, "    ")])
    parts.extend([
        "  </article>",
        "</main>",
    ])
    return "\n".join(parts)


def _parse_heading(text: str) -> tuple[int | None, str]:
    if not text.startswith("#"):
        return None, text
    if text.startswith("###### "):
        return 6, text[7:].strip()
    if text.startswith("##### "):
        return 5, text[6:].strip()
    if text.startswith("#### "):
        return 4, text[5:].strip()
    if text.startswith("### "):
        return 3, text[4:].strip()
    if text.startswith("## "):
        return 2, text[3:].strip()
    if text.startswith("# "):
        return 1, text[2:].strip()
    return None, text


def _render_inline_markup(text: str, *, source_path: Path) -> str:
    """Render the small inline subset used by the project."""

    rendered_parts: list[str] = []
    last_index = 0

    for match in INLINE_LINK_RE.finditer(text):
        rendered_parts.append(escape_html(text[last_index:match.start()]))
        label = escape_html(match.group(1))
        href = match.group(2).strip()
        if not _is_safe_internal_href(href):
            raise BuildError("Render Markdown", "only internal links are allowed in markdown content", path=source_path)
        rendered_parts.append(f'<a href="{escape_html(href, quote=True)}">{label}</a>')
        last_index = match.end()

    rendered_parts.append(escape_html(text[last_index:]))
    return "".join(rendered_parts)


def _is_safe_internal_href(href: str) -> bool:
    if href.startswith(("/", "./", "../", "#")):
        return not href.startswith("//")
    return False
