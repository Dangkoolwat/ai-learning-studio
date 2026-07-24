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


EXCLUDED_HEADER_TITLES = {"이메일 정보", "작성 지침", "참고 사항", "주의 사항", "기본 정보", "요청 사항"}


def render_inline_prompt_body_html(prompt_body: str) -> str:
    """Transform bracketed choices into inline <select> or <input> elements, while preserving section headers."""

    combobox_counter = 0

    def replace_bracket(match: re.Match[str]) -> str:
        nonlocal combobox_counter
        content = match.group(1).strip()

        # Preserve section header brackets like [이메일 정보], [작성 지침]
        if content in EXCLUDED_HEADER_TITLES:
            return match.group(0)

        # 1. Dropdown + free typing combo: [팀장님 / 클라이언트 담당자 / 협력사 담당자] or [+ 사업자등록증 / 견적서 / 통장사본]
        if "/" in content:
            is_multi = content.startswith("+")
            raw_content = content[1:].strip() if is_multi else content
            options = [opt.strip() for opt in raw_content.split("/") if opt.strip()]
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

        # 2. Free text: [첫 번째 핵심 내용]
        escaped_val = escape_html(content)
        return (
            f'<span class="itc" data-type="text" '
            f'data-value="{escaped_val}" data-placeholder="{escaped_val}" '
            f'tabindex="0" role="textbox">'
            f'{escaped_val} <i class="itc-arrow">✎</i></span>'
        )

    lines = prompt_body.splitlines()
    escaped_lines = [escape_html(line) for line in lines]
    escaped_body = "\n".join(escaped_lines)

    # Match any bracketed content [ ...]
    pattern = re.compile(r"\[([^\]]+)\]")
    return pattern.sub(replace_bracket, escaped_body)


def render_static_prompt_page(context: PageRendererContext) -> PageRendererResult:
    """Render a static prompt page."""

    prompt_blocks = [parse_prompt_block(block) for block in context.control_blocks if block.label == "prompt"]
    slider_blocks = _parse_preview_blocks(context) or [
        parse_image_slider_block(block) for block in context.control_blocks if block.label == "image-slider"
    ]
    if not prompt_blocks:
        raise BuildError(
            "Render page",
            "static-prompt pages require at least one prompt block",
            path=context.source_path,
            page_id=context.page_id,
            page_type=context.page_type,
            page_route=context.page_route,
            renderer_id=context.page_type,
        )
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
    ai_target_str = context.parsed_front_matter.get("ai_target", "").strip()
    ai_targets = [t.strip() for t in ai_target_str.split(",") if t.strip()]
    badges_html = []
    ext_links_html = []
    for target in ai_targets:
        target_lower = target.lower()
        if "chatgpt" in target_lower:
            badges_html.append('<span class="badge-ai badge-ai--chatgpt">ChatGPT 전용</span>')
            ext_links_html.append('<span role="button" tabindex="0" class="prompt-item__external-link" data-open-ai="chatgpt">ChatGPT에서 사용 ↗</span>')
        elif "gemini" in target_lower:
            badges_html.append('<span class="badge-ai badge-ai--gemini">Gemini 전용</span>')
            ext_links_html.append('<span role="button" tabindex="0" class="prompt-item__external-link" data-open-ai="gemini">Gemini에서 사용 ↗</span>')
        else:
            badges_html.append(f'<span class="badge-ai badge-ai--universal">{escape_html(target)}</span>')

    ai_badges_block = f'<div class="prompt-item__ai-badges">{" ".join(badges_html)}</div>\n' if badges_html else ""
    ext_actions_block = " ".join(ext_links_html)

    prompt_item_results = []
    for prompt_block in prompt_blocks:
        body_html = render_inline_prompt_body_html(prompt_block.body)
        has_inline_controls = 'class="itc"' in body_html

        if has_inline_controls:
            actions_html = ""
            preview_html = (
                '<article class="prompt-item prompt-item--preview">\n'
                '  <div class="prompt-item__preview-header">\n'
                '    <h3 class="prompt-item__preview-title">완성된 프롬프트 (실시간 미리보기)</h3>\n'
                f'    {ai_badges_block}'
                '  </div>\n'
                '  <div class="prompt-item__preview-box"><code class="prompt-item__preview-code"></code></div>\n'
                '  <footer class="prompt-item__actions">\n'
                '    <button type="button" class="prompt-item__copy-button" data-prompt-copy>프롬프트 복사</button>\n'
                f'    {ext_actions_block}\n'
                '    <span class="prompt-item__copy-status sr-only" aria-live="polite"></span>\n'
                '  </footer>\n'
                '</article>'
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

        prompt_item_results.append(
            render_prompt_item_component(
                PromptItemComponent(
                    prompt_title=prompt_block.title,
                    prompt_description_html=render_prompt_item_description_fragment(prompt_block.description),
                    prompt_body_html=body_html,
                    prompt_actions_html=actions_html,
                    prompt_preview_html=preview_html,
                    prompt_badges_html=ai_badges_block,
                ),
                context.component_templates,
            )
        )
    prompt_items_html = "\n".join(result.rendered_html for result in prompt_item_results)
    section_result = render_prompt_collection_component(
        PromptCollectionComponent(prompt_items_html=prompt_items_html),
        context.component_templates,
    )
    section_html = section_result.rendered_html
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
        component_results=(intro_result, body_result, *slider_results, *prompt_item_results, section_result),
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
