"""Static-prompt renderer for AI Learning Studio."""

from __future__ import annotations

import re

from core.component_engine import (
    render_page_body_component,
    render_page_intro_component,
    render_prompt_collection_component,
    render_prompt_item_component,
    render_prompt_item_description_fragment,
)
from core.component_models import PageBodyComponent, PageIntroComponent, PromptCollectionComponent, PromptItemComponent
from core.errors import BuildError
from html import escape as escape_html
from core.renderer_models import PageRendererContext, PageRendererResult
from core.renderer_validation import parse_prompt_block, validate_renderer_result
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
    prompt_item_results = []
    for prompt_block in prompt_blocks:
        body_html = render_inline_prompt_body_html(prompt_block.body)
        has_inline_controls = 'class="itc"' in body_html

        if has_inline_controls:
            actions_html = ""
            preview_html = (
                '<article class="prompt-item prompt-item--preview">\n'
                '  <h3 class="prompt-item__preview-title">완성된 프롬프트 (실시간 미리보기)</h3>\n'
                '  <div class="prompt-item__preview-box"><code class="prompt-item__preview-code"></code></div>\n'
                '  <footer class="prompt-item__actions">\n'
                '    <button type="button" class="prompt-item__copy-button" data-prompt-copy>프롬프트 복사</button>\n'
                '    <span class="prompt-item__copy-status sr-only" aria-live="polite"></span>\n'
                '  </footer>\n'
                '</article>'
            )
        else:
            actions_html = (
                '<footer class="prompt-item__actions">\n'
                '  <button type="button" class="prompt-item__copy-button" data-prompt-copy>프롬프트 복사</button>\n'
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
                ),
                context.component_templates,
            )
        )
    prompt_items_html = "\n".join(result.rendered_html for result in prompt_item_results)
    section_result = render_prompt_collection_component(
        PromptCollectionComponent(prompt_items_html=prompt_items_html),
        context.component_templates,
    )
    result = PageRendererResult(
        page_id=context.page_id,
        page_type=context.page_type,
        page_route=context.page_route,
        renderer_name=RENDERER_NAME,
        renderer_version=RENDERER_VERSION,
        main_html=build_main_html(
            page_type=context.page_type,
            intro_html=intro_result.rendered_html,
            body_html=body_result.rendered_html,
            section_html=section_result.rendered_html,
        ),
        source_heading_count=context.source_heading_count,
        rendered_section_count=len(prompt_blocks),
        component_results=(intro_result, body_result, *prompt_item_results, section_result),
        warnings=_heading_warning(context),
    )
    validate_renderer_result(context, result)
    return result


def _heading_warning(context: PageRendererContext) -> tuple[str, ...]:
    if not context.heading_structure:
        return ()
    return ("Markdown headings were normalized below the page intro to keep one page-level H1.",)
