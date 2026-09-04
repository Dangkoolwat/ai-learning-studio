"""Shared renderer helpers for AI Learning Studio."""

from __future__ import annotations

from html import escape as escape_html
from pathlib import Path
import re

from core.errors import BuildError


INLINE_LINK_OR_IMAGE_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)]+)\)")
INLINE_BOLD_RE = re.compile(r"\*\*(.*?)\*\*")


class _ListItem:
    """Represents a list item that can hold child paragraphs, code blocks, and sub-lists."""

    def __init__(self, main_text: str) -> None:
        self.main_text: str = main_text
        self.child_blocks: list[str] = []
        self.sub_list_type: str | None = None
        self.sub_list_items: list[str] = []

    def flush_sub_list(self) -> None:
        if self.sub_list_items:
            tag = self.sub_list_type or "ul"
            items_html = "".join(f"<li>{it}</li>" for it in self.sub_list_items)
            self.child_blocks.append(f"<{tag}>{items_html}</{tag}>")
            self.sub_list_items.clear()
            self.sub_list_type = None

    def render(self) -> str:
        self.flush_sub_list()
        children_html = "".join(self.child_blocks)
        return f"<li>{self.main_text}{children_html}</li>"


def render_markdown_fragment(markdown_text: str, *, source_path: Path) -> str:
    """Render the limited Markdown subset used by the project."""

    step_cards: list[list[str]] = []
    current_card_blocks: list[str] = []
    paragraph_lines: list[str] = []
    list_items: list[_ListItem] = []
    current_list_type: str | None = None
    code_lines: list[str] = []
    in_code_block = False
    in_list_code = False
    code_indent = 0

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        text = " ".join(line.strip() for line in paragraph_lines if line.strip())
        if text:
            current_card_blocks.append(f"<p>{_render_inline_markup(text, source_path=source_path)}</p>")
        paragraph_lines.clear()

    def flush_list() -> None:
        nonlocal current_list_type
        if not list_items:
            return
        tag = current_list_type or "ul"
        items_html = "".join(item.render() for item in list_items)
        current_card_blocks.append(f"<{tag}>{items_html}</{tag}>")
        list_items.clear()
        current_list_type = None

    def flush_step_card() -> None:
        flush_paragraph()
        flush_list()
        step_cards.append(list(current_card_blocks))
        current_card_blocks.clear()

    for raw_line in markdown_text.splitlines():
        stripped = raw_line.strip()
        indent_len = len(raw_line) - len(raw_line.lstrip())

        if in_code_block:
            if stripped.startswith("```"):
                code_html = escape_html("\n".join(code_lines))
                if in_list_code and list_items:
                    list_items[-1].flush_sub_list()
                    list_items[-1].child_blocks.append(f"<pre><code>{code_html}</code></pre>")
                else:
                    current_card_blocks.append(f"<pre><code>{code_html}</code></pre>")
                code_lines.clear()
                in_code_block = False
                in_list_code = False
                code_indent = 0
            else:
                if code_indent > 0 and raw_line.startswith(" " * code_indent):
                    code_lines.append(raw_line[code_indent:])
                else:
                    code_lines.append(raw_line)
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            if indent_len >= 2 and list_items:
                list_items[-1].flush_sub_list()
                in_code_block = True
                in_list_code = True
                code_indent = indent_len
            else:
                flush_list()
                in_code_block = True
                in_list_code = False
                code_indent = 0
            continue

        if not stripped:
            flush_paragraph()
            if list_items:
                list_items[-1].flush_sub_list()
            continue

        if stripped.startswith("<!-- RENDERER_CONTROL_BLOCK:"):
            flush_paragraph()
            flush_list()
            current_card_blocks.append(stripped)
            continue

        if stripped in {"---", "***", "___"}:
            flush_step_card()
            continue

        heading_level, heading_text = _parse_heading(stripped)
        if heading_level is not None:
            flush_paragraph()
            flush_list()
            rendered_level = min(heading_level + 1, 6)
            current_card_blocks.append(f"<h{rendered_level}>{escape_html(heading_text)}</h{rendered_level}>")
            continue

        # Check for indented line belonging to active list item
        if indent_len >= 2 and list_items:
            flush_paragraph()
            if stripped.startswith("- "):
                if list_items[-1].sub_list_type and list_items[-1].sub_list_type != "ul":
                    list_items[-1].flush_sub_list()
                list_items[-1].sub_list_type = "ul"
                list_items[-1].sub_list_items.append(_render_inline_markup(stripped[2:].strip(), source_path=source_path))
                continue

            sub_ol_match = re.match(r"^\d+\.\s+(.*)$", stripped)
            if sub_ol_match:
                if list_items[-1].sub_list_type and list_items[-1].sub_list_type != "ol":
                    list_items[-1].flush_sub_list()
                list_items[-1].sub_list_type = "ol"
                list_items[-1].sub_list_items.append(_render_inline_markup(sub_ol_match.group(1).strip(), source_path=source_path))
                continue

            # Indented paragraph within active list item
            list_items[-1].flush_sub_list()
            list_items[-1].child_blocks.append(f"<p>{_render_inline_markup(stripped, source_path=source_path)}</p>")
            continue

        # Root level list items (indent_len < 2)
        if stripped.startswith("- "):
            flush_paragraph()
            if current_list_type and current_list_type != "ul":
                flush_list()
            current_list_type = "ul"
            list_items.append(_ListItem(_render_inline_markup(stripped[2:].strip(), source_path=source_path)))
            continue

        ol_match = re.match(r"^\d+\.\s+(.*)$", stripped)
        if ol_match:
            flush_paragraph()
            if current_list_type and current_list_type != "ol":
                flush_list()
            current_list_type = "ol"
            list_items.append(_ListItem(_render_inline_markup(ol_match.group(1).strip(), source_path=source_path)))
            continue

        flush_list()
        paragraph_lines.append(raw_line)

    if in_code_block:
        raise BuildError("Render Markdown", "missing closing code fence", path=source_path)

    flush_step_card()

    result_blocks: list[str] = []
    for card_blocks in step_cards:
        if not card_blocks:
            continue
        if result_blocks:
            result_blocks.append('<div class="step-flow-arrow" aria-hidden="true">↓</div>')

        is_tips_card = any("활용 꿀팁" in b or "Quick Tips" in b for b in card_blocks)
        card_cls = "practice-step-card practice-step-card--tips" if is_tips_card else "practice-step-card"
        result_blocks.append(f'<div class="{card_cls}">')
        result_blocks.extend(card_blocks)
        result_blocks.append('</div>')

    return "\n".join(result_blocks)


def build_page_intro_html(*, page_title: str, page_description: str) -> str:
    """Build the shared page intro fragment."""

    description_html = f'    <p class="page-description">{escape_html(page_description)}</p>\n'
    return (
        "    <header class=\"page-intro\">\n"
        f"      <h1>{escape_html(page_title)}</h1>\n"
        f"{description_html}"
        "    </header>"
    )


def indent_preserving_pre(html_text: str, prefix: str = "    ") -> str:
    """Indent HTML text while preserving raw content inside <pre>...</pre> and preview <code>...</code> tags."""
    lines = html_text.splitlines()
    indented_lines: list[str] = []
    in_pre = False

    for line in lines:
        if in_pre:
            indented_lines.append(line)
            if "</pre>" in line or "</code>" in line or "</template>" in line:
                in_pre = False
            continue

        if "<pre" in line or '<code class="prompt-item__preview-code"' in line or "<template" in line:
            in_pre = True
            indented_lines.append(prefix + line if line.strip() else line)
            if "</pre>" in line or "</code>" in line or "</template>" in line:
                in_pre = False
            continue

        indented_lines.append(prefix + line if line.strip() else line)

    return "\n".join(indented_lines)


def build_main_html(
    *,
    page_type: str,
    intro_html: str,
    body_html: str,
    section_html: str | None = None,
) -> str:
    """Build the renderer-owned main region."""

    parts = [
        '<main class="site-main" id="main-content">',
        f'  <article class="page-content page-content--{page_type}">',
        indent_preserving_pre(intro_html, "    "),
        "",
        indent_preserving_pre(body_html, "    "),
    ]
    if section_html:
        parts.extend(["", indent_preserving_pre(section_html, "    ")])
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


def _render_bold_and_escape(text: str) -> str:
    """Render inline bold tags (**text** -> <strong>text</strong>) and escape raw HTML."""
    rendered_parts: list[str] = []
    last_index = 0

    for match in INLINE_BOLD_RE.finditer(text):
        rendered_parts.append(escape_html(text[last_index:match.start()]))
        bold_content = escape_html(match.group(1))
        rendered_parts.append(f"<strong>{bold_content}</strong>")
        last_index = match.end()

    rendered_parts.append(escape_html(text[last_index:]))
    return "".join(rendered_parts)


def _render_inline_markup(text: str, *, source_path: Path) -> str:
    """Render the small inline subset (links, bold, images) used by the project."""

    rendered_parts: list[str] = []
    last_index = 0

    for match in INLINE_LINK_OR_IMAGE_RE.finditer(text):
        rendered_parts.append(_render_bold_and_escape(text[last_index:match.start()]))
        is_image = bool(match.group(1))
        label = _render_bold_and_escape(match.group(2))
        href = match.group(3).strip()
        if not _is_safe_internal_href(href):
            raise BuildError("Render Markdown", "only internal links/images are allowed in markdown content", path=source_path)

        if is_image:
            if "#lightbox" in label:
                clean_label = label.replace("#lightbox", "").strip()
                filename = href.split('/')[-1].split('#')[0].split('?')[0]
                if not filename:
                    filename = 'download'
                svg_icon = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>'

                wrapper_html = (
                    f'<div class="image-wrapper lightbox-enabled">'
                    f'<img src="{escape_html(href, quote=True)}" alt="{clean_label}">'
                    f'<a class="image-hover-download" href="{escape_html(href, quote=True)}" download="{escape_html(filename, quote=True)}" title="다운로드" aria-label="다운로드">{svg_icon}</a>'
                    f'</div>'
                )
                rendered_parts.append(wrapper_html)
            else:
                rendered_parts.append(f'<img src="{escape_html(href, quote=True)}" alt="{label}">')
        else:
            rendered_parts.append(f'<a href="{escape_html(href, quote=True)}">{label}</a>')

        last_index = match.end()

    rendered_parts.append(_render_bold_and_escape(text[last_index:]))
    return "".join(rendered_parts)


def _is_safe_internal_href(href: str) -> bool:
    if href.startswith(("/", "./", "../", "#", "mailto:")):
        return not href.startswith("//")
    return False
