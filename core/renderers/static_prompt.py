"""Static-prompt renderer for AI Learning Studio."""

from __future__ import annotations

import re
from types import SimpleNamespace

from core.component_engine import (
    render_image_slider_component,
    render_page_body_component,
    render_page_intro_component,
    render_prompt_collection_component,
    render_prompt_item_component,
    render_prompt_item_description_fragment,
)
from core.component_models import ImageSliderComponent, PageBodyComponent, PageIntroComponent, PromptCollectionComponent, PromptItemComponent
from core.errors import BuildError
from html import escape as escape_html
from core.renderer_models import PageRendererContext, PageRendererResult
from core.renderer_validation import parse_image_slider_block, parse_prompt_block, validate_renderer_result
from core.renderers.base import build_main_html


RENDERER_NAME = "static-prompt"
RENDERER_VERSION = 1


EXCLUDED_HEADER_KEYWORDS = {
    "이메일 정보", "작성 지침", "참고 사항", "주의 사항", "기본 정보", "요청 사항",
    "사용자 메모", "역할 정의", "운영 원칙", "답변 형식", "답변 마무리 원칙",
    "최종 점검 항목", "최종 점검", "표기 규칙", "역할", "목적", "규칙", "주의사항",
    "작성 원칙", "필수 조건", "참고 조건", "출력 형식", "입력 조건", "기본 규칙"
}


def _is_section_header(line_stripped: str, full_match_str: str, content: str) -> bool:
    """Determine if a bracketed match is a section header instead of an input field."""
    if full_match_str in ("[/]", "[|]"):
        return False
    if line_stripped == full_match_str:
        return True
    if content in EXCLUDED_HEADER_KEYWORDS:
        return True
    if line_stripped.startswith(full_match_str) and not ("/" in content or "|" in content):
        after = line_stripped[len(full_match_str):].strip()
        if not after or after.startswith(":") or after.startswith("："):
            return True
    return False


def render_inline_prompt_body_html(prompt_body: str) -> str:
    """Transform bracketed choices into inline <select> or <input> elements, while preserving section headers."""

    lines = prompt_body.splitlines()
    processed_lines = []

    pattern = re.compile(r"\[([^\]]+)\]")

    for line in lines:
        escaped_line = escape_html(line)
        line_stripped = line.strip()

        def replace_bracket(match: re.Match[str]) -> str:
            full_match = match.group(0)
            content = match.group(1).strip()

            # Preserve section headers e.g. [역할 정의], [운영 원칙]
            if _is_section_header(line_stripped, full_match, content):
                return escape_html(full_match)

            # 1. Dropdown combo supporting both '/' and '|': [팀장님 / 클라이언트] or [팀장님 | 클라이언트]
            if "/" in content or "|" in content:
                is_multi = content.startswith("+")
                raw_content = content[1:].strip() if is_multi else content
                delimiters = r"[/|]"
                options = [opt.strip() for opt in re.split(delimiters, raw_content) if opt.strip()]
                if options:
                    default_val = escape_html(options[0])
                    options_attr = escape_html("|".join(options))
                    data_type = "multi-combo" if is_multi else "combo"
                    return (
                        f'<span class="itc" data-type="{data_type}" '
                        f'data-options="{options_attr}" '
                        f'data-value="{default_val}" '
                        f'tabindex="0" role="combobox" aria-expanded="false">'
                        f'{default_val} <i class="itc-arrow">▾</i></span>'
                    )

            # 2. Free text field: [첫 번째 핵심 내용]
            escaped_val = escape_html(content)
            return (
                f'<span class="itc" data-type="text" '
                f'data-value="{escaped_val}" data-placeholder="{escaped_val}" '
                f'tabindex="0" role="textbox">'
                f'{escaped_val} <i class="itc-arrow">✎</i></span>'
            )

        processed_line = pattern.sub(replace_bracket, escaped_line)
        processed_lines.append(processed_line)

    return "\n".join(processed_lines)


def _build_initial_clean_prompt_text(prompt_body: str) -> str:
    """Extract initial clean text for preview box by replacing bracketed controls with default values."""
    lines = prompt_body.splitlines()
    processed_lines = []
    pattern = re.compile(r"\[([^\]]+)\]")

    for line in lines:
        line_stripped = line.strip()

        def replace_bracket(match: re.Match[str]) -> str:
            full_match = match.group(0)
            content = match.group(1).strip()

            if _is_section_header(line_stripped, full_match, content):
                return full_match

            if "/" in content or "|" in content:
                is_multi = content.startswith("+")
                raw_content = content[1:].strip() if is_multi else content
                options = [opt.strip() for opt in re.split(r"[/|]", raw_content) if opt.strip()]
                if options:
                    return options[0]

            return content

        processed_line = pattern.sub(replace_bracket, line)
        processed_lines.append(processed_line)

    filtered_lines = [l for l in processed_lines if not re.match(r"^-\s*[^:]+:\s*$", l.strip())]
    return "\n".join(filtered_lines).strip()


def render_static_prompt_page(context: PageRendererContext) -> PageRendererResult:
    """Render a static prompt page."""

    prompt_blocks = [parse_prompt_block(block) for block in context.control_blocks if block.label == "prompt"]
    slider_blocks = _parse_preview_blocks(context) or [
        parse_image_slider_block(block) for block in context.control_blocks if block.label == "image-slider"
    ]
    intro_result = render_page_intro_component(
        PageIntroComponent(page_title=context.page_title, page_description=context.page_description),
        context.component_templates,
    )
    body_result = render_page_body_component(
        PageBodyComponent(body_html=context.rendered_markdown_html),
        context.component_templates,
    )
    slider_results = [
        render_image_slider_component(_build_image_slider_component(block), context.component_templates)
        for block in slider_blocks
    ]
def _build_ai_badges_and_actions(ai_targets: list[str]) -> tuple[str, str]:
    badges_html = []
    ext_links_html = []
    for target in ai_targets:
        target_lower = target.lower()
        if "chatgpt" in target_lower:
            badges_html.append('<span class="badge-ai badge-ai--chatgpt">ChatGPT</span>')
            ext_links_html.append('<span role="button" tabindex="0" class="prompt-item__external-link" data-open-ai="chatgpt">ChatGPT에서 사용 ↗</span>')
        elif "gemini" in target_lower:
            badges_html.append('<span class="badge-ai badge-ai--gemini">Gemini</span>')
            ext_links_html.append('<span role="button" tabindex="0" class="prompt-item__external-link" data-open-ai="gemini">Gemini에서 사용 ↗</span>')
        elif "claude" in target_lower:
            badges_html.append('<span class="badge-ai badge-ai--claude">Claude</span>')
            ext_links_html.append('<span role="button" tabindex="0" class="prompt-item__external-link" data-open-ai="claude">Claude에서 사용 ↗</span>')
        else:
            badges_html.append(f'<span class="badge-ai badge-ai--universal">{escape_html(target)}</span>')

    ai_badges_block = f'<div class="prompt-item__ai-badges">{" ".join(badges_html)}</div>\n' if badges_html else ""
    ext_actions_block = " ".join(ext_links_html)
    return ai_badges_block, ext_actions_block


def render_static_prompt_page(context: PageRendererContext) -> PageRendererResult:
    """Render a static prompt page."""

    prompt_blocks = [parse_prompt_block(block) for block in context.control_blocks if block.label == "prompt"]
    slider_blocks = _parse_preview_blocks(context) or [
        parse_image_slider_block(block) for block in context.control_blocks if block.label == "image-slider"
    ]
    intro_result = render_page_intro_component(
        PageIntroComponent(page_title=context.page_title, page_description=context.page_description),
        context.component_templates,
    )
    body_result = render_page_body_component(
        PageBodyComponent(body_html=context.rendered_markdown_html),
        context.component_templates,
    )
    slider_results = [
        render_image_slider_component(_build_image_slider_component(block), context.component_templates)
        for block in slider_blocks
    ]
    page_ai_target_str = context.parsed_front_matter.get("ai_target", "").strip()
    if not page_ai_target_str:
        default_ai_targets = ["ChatGPT", "Gemini"]
    else:
        default_ai_targets = [t.strip() for t in page_ai_target_str.split(",") if t.strip()]

    raw_source = context.parsed_front_matter.get("source", "").strip()
    cleaned_source = re.sub(r'^(?:출처|source)\s*[:：]\s*', '', raw_source, flags=re.IGNORECASE).strip()
    source_html = (
        f'<div class="prompt-item__source"><span class="prompt-item__source-label">Source :</span> {escape_html(cleaned_source)}</div>'
        if cleaned_source
        else ""
    )

    prompt_item_results = []
    prompt_block_html_map = {}
    for prompt_block in prompt_blocks:
        if prompt_block.ai_target:
            block_targets = [t.strip() for t in prompt_block.ai_target.split(",") if t.strip()]
        else:
            block_targets = default_ai_targets

        ai_badges_block, ext_actions_block = _build_ai_badges_and_actions(block_targets)
        body_html = render_inline_prompt_body_html(prompt_block.body)
        has_inline_controls = 'class="itc"' in body_html

        if has_inline_controls:
            initial_clean_text = _build_initial_clean_prompt_text(prompt_block.body)
            initial_clean_html = escape_html(initial_clean_text)
            actions_html = (
                '<footer class="prompt-item__actions">\n'
                '  <button type="button" class="prompt-item__copy-button" data-prompt-copy>프롬프트 복사</button>\n'
                f'  {ext_actions_block}\n'
                '  <span class="prompt-item__copy-status sr-only" aria-live="polite"></span>\n'
                '</footer>'
            )
            preview_html = (
                '<div class="prompt-item__preview-section">\n'
                '  <div class="prompt-item__preview-header">\n'
                '    <div class="prompt-item__title prompt-item__title--preview">완성된 프롬프트 (실시간 미리보기)</div>\n'
                '  </div>\n'
                f'  <div class="prompt-item__preview-box"><code class="prompt-item__preview-code">{initial_clean_html}</code></div>\n'
                '</div>'
            )
        else:
            actions_html = (
                '<footer class="prompt-item__actions">\n'
                '  <button type="button" class="prompt-item__copy-button" data-prompt-copy>프롬프트 복사</button>\n'
                f'  {ext_actions_block}\n'
                '  <span class="prompt-item__copy-status sr-only" aria-live="polite"></span>\n'
                '</footer>'
            )
            preview_html = ""

        item_result = render_prompt_item_component(
            PromptItemComponent(
                prompt_title=prompt_block.title,
                prompt_description_html=render_prompt_item_description_fragment(prompt_block.description),
                prompt_body_html=body_html,
                prompt_actions_html=actions_html,
                prompt_preview_html=preview_html,
                prompt_badges_html=ai_badges_block,
                prompt_source_html=source_html,
            ),
            context.component_templates,
        )
        prompt_item_results.append(item_result)

    # Map control blocks to their rendered HTML by block index
    prompt_blocks_by_index = {
        block.index: result.rendered_html
        for block, result in zip(
            [b for b in context.control_blocks if b.label == "prompt"],
            prompt_item_results
        )
    }

    body_html_content = context.rendered_markdown_html
    has_placeholders = "<!-- RENDERER_CONTROL_BLOCK:" in body_html_content

    if has_placeholders:
        def _replace_placeholder(match: re.Match) -> str:
            lbl = match.group(1)
            idx = int(match.group(2))
            if lbl == "prompt" and idx in prompt_blocks_by_index:
                return prompt_blocks_by_index[idx]
            return ""

        body_html_content = re.sub(
            r"<!-- RENDERER_CONTROL_BLOCK:([a-z0-9-]+):(\d+) -->",
            _replace_placeholder,
            body_html_content,
        )

    body_result = render_page_body_component(
        PageBodyComponent(body_html=body_html_content),
        context.component_templates,
    )

    if prompt_blocks and not has_placeholders:
        prompt_items_html = "\n".join(result.rendered_html for result in prompt_item_results)
        section_result = render_prompt_collection_component(
            PromptCollectionComponent(prompt_items_html=prompt_items_html),
            context.component_templates,
        )
        section_html = section_result.rendered_html
        component_results = (intro_result, body_result, *slider_results, *prompt_item_results, section_result)
    else:
        section_html = ""
        component_results = (intro_result, body_result, *slider_results, *prompt_item_results)

    top_preview_html = "\n".join(result.rendered_html for result in slider_results)
    result = PageRendererResult(
        page_id=context.page_id,
        page_type=context.page_type,
        page_route=context.page_route,
        renderer_name=RENDERER_NAME,
        renderer_version=RENDERER_VERSION,
        main_html=build_main_html(
            page_type=context.page_type,
            intro_html=intro_result.rendered_html,
            body_html="\n".join(part for part in (top_preview_html, body_result.rendered_html) if part),
            section_html=section_html,
        ),
        source_heading_count=context.source_heading_count,
        rendered_section_count=len(prompt_blocks) + len(slider_blocks),
        component_results=component_results,
        warnings=_heading_warning(context),
    )
    validate_renderer_result(context, result)
    return result


def _heading_warning(context: PageRendererContext) -> tuple[str, ...]:
    if not context.heading_structure:
        return ()
    return ("Markdown headings were normalized below the page intro to keep one page-level H1.",)


def _build_image_slider_component(block) -> ImageSliderComponent:
    slide_count = len(block.slides)
    slides_html: list[str] = []
    nav_html: list[str] = []
    for index, slide in enumerate(block.slides):
        is_first = index == 0
        slides_html.append(
            (
                '<article class="image-slider__slide{active_class}" id="{slide_id}" data-slider-slide>\n'
                '  <div class="image-slider__frame">\n'
                '    <img class="image-slider__image" src="{image_src}" alt="{image_alt}" />\n'
                '  </div>\n'
                '</article>'
            ).format(
                slide_id=slide.slide_id,
                image_src=escape_html(slide.image_src, quote=True),
                image_alt=escape_html(slide.image_alt),
                active_class=" is-active" if is_first else "",
            )
        )
        nav_html.append(
            f'<li class="image-slider__nav-item"><button type="button" class="image-slider__nav-link{" is-active" if is_first else ""}" aria-label="슬라이드 {index + 1}로 이동" data-slider-dot>•</button></li>'
        )
    slider_html = (
        '<div class="image-slider__wrapper">\n'
        '  <button type="button" class="image-slider__arrow image-slider__arrow--prev" aria-label="이전 이미지" data-slider-prev>&lt;</button>\n'
        '  <div class="image-slider__viewport">\n'
        '    <div class="image-slider__track" data-slider-track>\n'
        + "".join(slides_html)
        + '\n    </div>\n'
        '  </div>\n'
        '  <button type="button" class="image-slider__arrow image-slider__arrow--next" aria-label="다음 이미지" data-slider-next>&gt;</button>\n'
        '</div>\n'
        + '<ol class="image-slider__nav">'
        + "".join(nav_html)
        + "</ol>"
    )
    return ImageSliderComponent(
        slider_title=block.title,
        slider_description=block.description or "",
        slider_slides_html=slider_html,
    )


def _parse_preview_blocks(context: PageRendererContext):
    preview_value = context.parsed_front_matter.get("preview", "").strip()
    if not preview_value:
        return ()

    entries = [item.strip() for item in preview_value.split(",") if item.strip()]
    if len(entries) < 2:
        raise BuildError(
            "Render page",
            "preview front matter requires at least two image paths",
            path=context.source_path,
            page_id=context.page_id,
            page_type=context.page_type,
            page_route=context.page_route,
            renderer_id=context.page_type,
        )

    slides = []
    for index, image_src in enumerate(entries, start=1):
        slides.append(
            SimpleNamespace(
                slide_id=f"slide-{index}",
                image_src=image_src,
                image_alt=f"preview image {index}",
                title=f"미리보기 {index}",
                caption="예시 이미지",
            )
        )

    return (SimpleNamespace(title=context.page_title, description=context.page_description, slides=tuple(slides)),)
