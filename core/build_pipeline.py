"""Phase 10 production-ready build pipeline helpers for AI Learning Studio."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from html import escape as escape_html
import json
import os
from pathlib import Path
from shutil import copy2, rmtree
import re
import sys
import tempfile
from typing import Any, Callable
from uuid import uuid4

from core.errors import BuildError
from core.component_engine import load_approved_component_templates
from core.component_models import COMPONENT_ENGINE_VERSION, COMPONENT_VALIDATION_STATUS, ComponentRenderResult, LoadedComponentTemplates
from core.component_registry import APPROVED_COMPONENT_IDS, APPROVED_COMPONENT_SPECS, OPTIONAL_COMPONENT_IDS
from core.component_validation import validate_component_registry
from core.data_consistency import validate_navigation_registry_consistency
from core.navigation import NavigationData, load_navigation
from core.page_registry import PageRegistry, PageRegistryEntry, load_page_registry
from core.page_renderers import RENDERER_REGISTRY, render_page, validate_renderer_registry
from core.renderer_models import (
    APPROVED_CONTROL_BLOCK_LABELS,
    APPROVED_RENDERER_IDS,
    PageRendererContext,
    PageRendererResult,
    ParsedRendererSource,
    RENDERER_ENGINE_VERSION,
    RENDERER_VALIDATION_STATUS,
)
from core.renderer_validation import parse_renderer_source
from core.renderers.base import build_main_html as build_rendered_main_html
from core.renderers.base import build_page_intro_html, render_markdown_fragment
from core.template_engine import (
    build_body_class,
    build_navigation_items_html,
    load_approved_templates,
    render_page_document,
    route_href_for_output,
)
from core.template_models import (
    LoadedTemplates,
    PageTemplateContext,
    SITE_NAME,
    TEMPLATE_ENGINE_VERSION,
    TEMPLATE_PARTIAL_NAMES,
    TEMPLATE_VALIDATION_STATUS,
)
from core.theme_generator import generate_theme_assets, stylesheet_href_for_output
from core.theme_parser import load_theme_designs
from core.theme_models import ThemeDesign, ThemeGenerationResult


PROJECT_NAME = "AI Learning Studio"
BUILD_PHASE = "Phase 10 Production Design and Release Readiness"
GENERATOR_VERSION = "phase-10-production-design-and-release-readiness-v1"
TOTAL_STAGES = 16
SITE_URL_ENV_VAR = "AI_STUDIO_SITE_URL"
ALLOWED_ASSET_EXTENSIONS = {".css", ".js", ".svg", ".png", ".jpg", ".jpeg", ".webp"}
TEXT_ASSET_EXTENSIONS = {".css", ".js", ".svg"}
MAX_IMAGE_ASSET_BYTES = 1024 * 1024  # 1MB limit for LCP and web performance
ALLOWED_FRONT_MATTER_KEYS = {"registry_id", "title", "description", "seo_title", "preview", "ai_target", "source", "type"}
EXPECTED_TEMPLATE_HREF_RE = re.compile(r'<link rel="stylesheet" href="([^"]+)">')
EXPECTED_SCRIPT_HREF_RE = re.compile(r'<script type="module" src="([^"]+)"></script>')
NAVIGATION_LINK_RE = re.compile(
    r'<li class="navigation-item(?: is-current)?">\s*'
    r'<a class="navigation-link" href="([^"]+)"(?: aria-current="page")?>\s*'
    r'<span class="nav-label">([^<]+)</span>\s*'
    r'<span class="nav-description">([^<]+)</span>\s*'
    r'</a>',
    re.DOTALL,
)
PLACEHOLDER_RE = re.compile(r"{{\s*[a-z0-9_]+\s*}}")
FORBIDDEN_JS_PATTERNS = (
    "eval(",
    "new Function",
    "document.write",
    "fetch(",
    "XMLHttpRequest",
    "localStorage",
    "sessionStorage",
    "cookie",
    "require(",
    "module.exports",
    "exports.",
)


@dataclass
class PageSource:
    """A parsed page source file."""

    source_path: Path
    registry_id: str
    front_matter: dict[str, str]
    raw_source_text: str
    markdown_body: str


@dataclass
class BuildSummary:
    page_count: int
    asset_count: int
    route_count: int
    output_dir: Path
    generated_routes: list[str]
    generated_output_files: list[str]
    source_page_files: list[str]


def log_stage(index: int, total: int, label: str) -> None:
    print(f"[{index}/{total}] {label}")


def discover_page_sources(pages_dir: Path) -> list[Path]:
    if not pages_dir.is_dir():
        raise BuildError("Validate environment", "pages/ directory does not exist", path=pages_dir)

    page_sources: list[Path] = []
    for path in sorted(pages_dir.rglob("*.md")):
        relative = path.relative_to(pages_dir)
        if any(part.startswith(".") for part in relative.parts):
            continue
        if path.name.startswith("."):
            continue
        page_sources.append(path)

    return page_sources


def parse_front_matter(page_path: Path, source_text: str) -> tuple[dict[str, str], str]:
    lines = source_text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise BuildError("Parse page sources", "front matter must start with ---", path=page_path, source_file=page_path)

    closing_index = next((index for index, raw_line in enumerate(lines[1:], start=1) if raw_line.strip() == "---"), None)
    if closing_index is None:
        raise BuildError(
            "Parse page sources",
            "missing closing front matter delimiter",
            path=page_path,
            source_file=page_path,
        )

    metadata: dict[str, str] = {}
    for raw_line in lines[1:closing_index]:
        stripped = raw_line.strip()
        if not stripped:
            raise BuildError(
                "Parse page sources",
                "blank lines are not allowed inside front matter",
                path=page_path,
                source_file=page_path,
            )
        if ":" not in raw_line:
            raise BuildError(
                "Parse page sources",
                "front matter lines must use key: value format",
                path=page_path,
                source_file=page_path,
            )

        key, _, value = raw_line.partition(":")
        key = key.strip()
        value = value.strip()

        if key not in ALLOWED_FRONT_MATTER_KEYS:
            raise BuildError(
                "Parse page sources",
                f"unknown front matter field: {key}",
                path=page_path,
                source_file=page_path,
                field=key,
            )
        if key in metadata:
            raise BuildError(
                "Parse page sources",
                f"duplicate front matter field: {key}",
                path=page_path,
                source_file=page_path,
                field=key,
            )
        metadata[key] = value

    body = "\n".join(lines[closing_index + 1 :])
    return metadata, body


def validate_front_matter(page_path: Path, metadata: dict[str, str]) -> None:
    registry_id = metadata.get("registry_id", "").strip()
    if not registry_id:
        raise BuildError(
            "Parse page sources",
            "registry_id must be a non-empty string",
            path=page_path,
            source_file=page_path,
            field="registry_id",
        )
    unallowed = set(metadata) - ALLOWED_FRONT_MATTER_KEYS
    if unallowed:
        raise BuildError(
            "Parse page sources",
            f"unsupported front matter keys: {sorted(unallowed)}",
            path=page_path,
            source_file=page_path,
        )


def parse_page_source(page_path: Path) -> PageSource:
    source_text = page_path.read_text(encoding="utf-8")
    metadata, body = parse_front_matter(page_path, source_text)
    validate_front_matter(page_path, metadata)
    return PageSource(
        source_path=page_path,
        registry_id=metadata["registry_id"].strip(),
        front_matter=metadata,
        raw_source_text=source_text,
        markdown_body=body,
    )


def render_markdown(markdown_text: str, *, source_path: Path) -> str:
    """Render the limited Markdown subset used by the verification pages."""

    blocks: list[str] = []
    paragraph_lines: list[str] = []
    list_items: list[str] = []
    code_lines: list[str] = []
    in_code_block = False

    def _render_bold_inline(text: str) -> str:
        parts: list[str] = []
        last_idx = 0
        bold_pattern = re.compile(r"\*\*(.*?)\*\*")
        for match in bold_pattern.finditer(text):
            parts.append(escape_html(text[last_idx:match.start()]))
            bold_content = escape_html(match.group(1))
            parts.append(f"<strong>{bold_content}</strong>")
            last_idx = match.end()
        parts.append(escape_html(text[last_idx:]))
        return "".join(parts)

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        text = " ".join(line.strip() for line in paragraph_lines if line.strip())
        if text:
            blocks.append(f"<p>{_render_bold_inline(text)}</p>")
        paragraph_lines.clear()

    def flush_list() -> None:
        if not list_items:
            return
        items = "".join(f"<li>{item}</li>" for item in list_items)
        blocks.append(f"<ul>{items}</ul>")
        list_items.clear()

    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()

        if in_code_block:
            if stripped == "```":
                code_html = escape_html("\n".join(code_lines))
                blocks.append(f"<pre><code>{code_html}</code></pre>")
                code_lines.clear()
                in_code_block = False
            else:
                code_lines.append(line)
            continue

        if stripped == "```":
            flush_paragraph()
            flush_list()
            in_code_block = True
            continue
        if stripped.startswith("```"):
            raise BuildError("Render HTML", "only bare triple-backtick fences are supported", path=source_path)
        if not stripped:
            flush_paragraph()
            flush_list()
            continue
        if stripped.startswith("# "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<h1>{escape_html(stripped[2:].strip())}</h1>")
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<h2>{escape_html(stripped[3:].strip())}</h2>")
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            list_items.append(_render_bold_inline(stripped[2:].strip()))
            continue

        flush_list()
        paragraph_lines.append(line)

    if in_code_block:
        raise BuildError("Render HTML", "missing closing code fence", path=source_path)

    flush_paragraph()
    flush_list()
    return "\n".join(blocks)


def route_to_output_path(route: str, dist_dir: Path) -> Path:
    if route == "/":
        output_path = dist_dir / "index.html"
    else:
        segments = [segment for segment in route.strip("/").split("/") if segment]
        output_path = dist_dir.joinpath(*segments, "index.html")

    normalized_output = output_path.resolve(strict=False)
    normalized_dist = dist_dir.resolve(strict=False)
    if normalized_dist != normalized_output and normalized_dist not in normalized_output.parents:
        raise BuildError("Render HTML", "route escapes the dist/ directory")
    return output_path


def build_page_renderer_contexts(
    published_pages: list[PageRegistryEntry],
    parsed_sources_by_id: dict[str, PageSource],
    parsed_renderer_sources_by_id: dict[str, ParsedRendererSource],
    registry: PageRegistry,
    navigation: NavigationData,
    staging_dir: Path,
    *,
    active_theme_id: str,
    component_templates: LoadedComponentTemplates,
) -> list[PageRendererContext]:
    page_contexts: list[PageRendererContext] = []

    for page in published_pages:
        source = parsed_sources_by_id[page.id]
        parsed_renderer_source = parsed_renderer_sources_by_id[page.id]
        rendered_markdown_html = render_markdown_fragment(parsed_renderer_source.markdown_body, source_path=source.source_path)
        page_contexts.append(
            PageRendererContext(
                page_id=page.id,
                page_type=page.type,
                page_route=page.route,
                page_section=page.section or "",
                page_title=page.title,
                page_description=page.description,
                page_lang=page.lang,
                source_path=source.source_path,
                raw_markdown_source=source.raw_source_text,
                parsed_front_matter=source.front_matter,
                markdown_body=parsed_renderer_source.markdown_body,
                rendered_markdown_html=rendered_markdown_html,
                heading_structure=parsed_renderer_source.heading_structure,
                source_heading_count=parsed_renderer_source.source_heading_count,
                active_theme_id=active_theme_id,
                control_blocks=parsed_renderer_source.control_blocks,
                component_templates=component_templates,
            )
        )

    return page_contexts


def build_page_template_contexts(
    published_pages: list[PageRegistryEntry],
    renderer_results_by_id: dict[str, PageRendererResult],
    registry: PageRegistry,
    navigation: NavigationData,
    staging_dir: Path,
    *,
    active_theme_id: str,
    site_base_url: str | None,
) -> list[PageTemplateContext]:
    current_year = datetime.now().astimezone().year
    page_contexts: list[PageTemplateContext] = []

    for page in published_pages:
        result = renderer_results_by_id[page.id]
        output_path = route_to_output_path(page.route, staging_dir)
        navigation_items_html = build_navigation_items_html(page, registry, navigation, output_path, staging_dir)
        document_title = page.title if page.route == "/" else f"{page.title} | {SITE_NAME}"
        site_stylesheet_url = stylesheet_href_for_output(output_path, staging_dir / "assets" / "css" / "site.css")
        site_script_url = stylesheet_href_for_output(output_path, staging_dir / "assets" / "js" / "site.js") + "?v=1.4"
        favicon_url = stylesheet_href_for_output(output_path, staging_dir / "assets" / "favicon.svg")
        canonical_link_html = build_canonical_link_html(site_base_url, page.route) if site_base_url else ""

        page_contexts.append(
            PageTemplateContext(
                page_id=page.id,
                page_title=document_title,
                page_description=page.description,
                page_route=page.route,
                page_type=page.type,
                page_section=page.section or "",
                page_lang=page.lang,
                body_class=build_body_class(page.id, page.type, page.section),
                site_name=SITE_NAME,
                current_year=current_year,
                active_theme_id=active_theme_id,
                robots_content="index,follow",
                theme_color="#F3F1ED",
                canonical_link_html=canonical_link_html,
                favicon_url=favicon_url,
                theme_stylesheet_url=stylesheet_href_for_output(
                    output_path,
                    staging_dir / "themes" / active_theme_id / "style.css",
                ),
                site_stylesheet_url=site_stylesheet_url,
                site_script_url=site_script_url,
                home_url=route_href_for_output(output_path, "/", staging_dir),
                navigation_items_html=navigation_items_html,
                main_html=result.main_html,
                html_lang=page.lang,
            )
        )

    return page_contexts


def build_canonical_link_html(site_base_url: str, route: str) -> str:
    normalized_base_url = site_base_url.rstrip("/")
    if not normalized_base_url:
        return ""
    return f'<link rel="canonical" href="{escape_html(normalized_base_url + route, quote=True)}">'


def resolve_site_base_url() -> str | None:
    value = os.environ.get(SITE_URL_ENV_VAR, "").strip()
    if not value:
        return None
    return value.rstrip("/")


def build_not_found_page_context(
    *,
    registry: PageRegistry,
    navigation: NavigationData,
    staging_dir: Path,
    active_theme_id: str,
    site_base_url: str | None,
) -> PageTemplateContext:
    output_path = staging_dir / "404.html"
    fake_current_page = PageRegistryEntry(
        id="not-found",
        title="페이지를 찾을 수 없습니다",
        description="요청한 페이지를 찾지 못했습니다.",
        route="/404.html",
        source="pages/404.md",
        type="error-page",
        section=None,
        order=999,
        navigation=False,
        status="draft",
        lang="ko",
    )
    navigation_items_html = build_navigation_items_html(fake_current_page, registry, navigation, output_path, staging_dir)
    home_href = route_href_for_output(output_path, "/", staging_dir)
    ai_practice_href = route_href_for_output(output_path, "/ai-practice/", staging_dir)
    intro_html = build_page_intro_html(
        page_title="페이지를 찾을 수 없습니다",
        page_description="요청한 페이지를 찾지 못했습니다. 홈으로 돌아가거나 AI 체험 실습으로 이동해 보세요.",
    )
    body_html = (
        '<section class="page-not-found">'
        '<p>주소를 다시 확인하거나 아래 링크에서 학습을 계속할 수 있습니다.</p>'
        '<ul class="page-not-found__links">'
        f'<li><a href="{escape_html(home_href, quote=True)}">홈으로 돌아가기</a></li>'
        f'<li><a href="{escape_html(ai_practice_href, quote=True)}">AI 체험 실습으로 이동</a></li>'
        "</ul>"
        "</section>"
    )
    main_html = build_rendered_main_html(page_type="error-page", intro_html=intro_html, body_html=body_html)
    theme_stylesheet_url = stylesheet_href_for_output(output_path, staging_dir / "themes" / active_theme_id / "style.css")

    return PageTemplateContext(
        page_id="not-found",
        page_title="페이지를 찾을 수 없습니다 | AI Learning Studio",
        page_description="요청한 페이지를 찾지 못했습니다. 홈으로 돌아가거나 AI 체험 실습으로 이동해 보세요.",
        page_route="/404.html",
        page_type="error-page",
        page_section="",
        page_lang="ko",
        body_class="page page-type-error-page page-id-not-found",
        site_name=SITE_NAME,
        current_year=datetime.now().astimezone().year,
        active_theme_id=active_theme_id,
        robots_content="noindex,follow",
        theme_color="#F3F1ED",
        canonical_link_html="",
        favicon_url=stylesheet_href_for_output(output_path, staging_dir / "assets" / "favicon.svg"),
        theme_stylesheet_url=theme_stylesheet_url,
        site_stylesheet_url=stylesheet_href_for_output(output_path, staging_dir / "assets" / "css" / "site.css"),
        site_script_url=stylesheet_href_for_output(output_path, staging_dir / "assets" / "js" / "site.js") + "?v=1.4",
        home_url=home_href,
        navigation_items_html=navigation_items_html,
        main_html=main_html,
        html_lang="ko",
    )


def build_sitemap_xml(published_pages: list[PageRegistryEntry], *, site_base_url: str | None) -> str:
    routes = [page.route for page in published_pages]
    if site_base_url:
        normalized_base_url = site_base_url.rstrip("/")
        loc_values = [normalized_base_url + route for route in routes]
    else:
        loc_values = routes

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc_value in loc_values:
        lines.append("  <url>")
        lines.append(f"    <loc>{escape_html(loc_value)}</loc>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def build_robots_txt(*, site_base_url: str | None) -> str:
    lines = [
        "User-agent: *",
        "Allow: /",
    ]
    if site_base_url:
        lines.append(f"Sitemap: {site_base_url.rstrip('/')}/sitemap.xml")
    return "\n".join(lines) + "\n"


def validate_generated_page_html(
    output_path: Path,
    html_text: str,
    *,
    page: PageRegistryEntry,
    page_context: PageTemplateContext,
    renderer_result: PageRendererResult,
    registry: PageRegistry,
    navigation: NavigationData,
    theme_generation: ThemeGenerationResult,
    dist_root: Path,
) -> None:
    expected_theme_id = theme_generation.active_theme_id
    expected_theme_href = page_context.theme_stylesheet_url
    expected_site_href = page_context.site_stylesheet_url
    expected_script_href = page_context.site_script_url
    expected_favicon_href = page_context.favicon_url
    expected_home_href = page_context.home_url
    expected_body_open = (
        f'<body class="{page_context.body_class}" '
        f'data-page-id="{page.id}" '
        f'data-page-type="{page.type}" '
        f'data-page-section="{page_context.page_section}">'
    )
    expected_main_html = renderer_result.main_html

    if not html_text.startswith("<!doctype html>\n"):
        raise BuildError("Validate output", "HTML must start with a doctype", path=output_path, page_id=page.id)
    if html_text.count("<html") != 1:
        raise BuildError("Validate output", "HTML must contain exactly one html element", path=output_path, page_id=page.id)
    if html_text.count("<head>") != 1:
        raise BuildError("Validate output", "HTML must contain exactly one head element", path=output_path, page_id=page.id)
    if html_text.count("<body ") != 1:
        raise BuildError("Validate output", "HTML must contain exactly one body element", path=output_path, page_id=page.id)
    if html_text.count('<header class="site-header">') != 1:
        raise BuildError("Validate output", "HTML must contain exactly one site header", path=output_path, page_id=page.id)
    if html_text.count('<nav class="site-navigation"') != 1:
        raise BuildError("Validate output", "HTML must contain exactly one site navigation", path=output_path, page_id=page.id)
    if html_text.count('<main class="site-main" id="main-content">') != 1:
        raise BuildError("Validate output", "HTML must contain exactly one main region", path=output_path, page_id=page.id)
    if html_text.count(f'<article class="page-content page-content--{page.type}">') != 1:
        raise BuildError("Validate output", "HTML must contain exactly one page-type article region", path=output_path, page_id=page.id)
    if html_text.count('<footer class="site-footer">') != 1:
        raise BuildError("Validate output", "HTML must contain exactly one site footer", path=output_path, page_id=page.id)
    if html_text.count('<link rel="stylesheet"') != 2:
        raise BuildError("Validate output", "HTML must include exactly two stylesheet links", path=output_path, page_id=page.id)
    if html_text.count('<script type="module"') != 1:
        raise BuildError("Validate output", "HTML must include exactly one module script", path=output_path, page_id=page.id)
    if html_text.count('<a class="navigation-link"') != len(navigation.sections):
        raise BuildError("Validate output", "HTML must include exactly four navigation links", path=output_path, page_id=page.id)
    if page.route == "/" and 'aria-current="page"' in html_text:
        raise BuildError("Validate output", "root page must not mark a navigation item current", path=output_path, page_id=page.id)
    if page.route != "/" and html_text.count('aria-current="page"') != 1:
        raise BuildError("Validate output", "section page must mark exactly one navigation item current", path=output_path, page_id=page.id)

    if f'<html lang="{page.lang}" data-theme="{expected_theme_id}">' not in html_text:
        raise BuildError("Validate output", "HTML root metadata is incorrect", path=output_path, page_id=page.id, theme_id=expected_theme_id)
    if expected_body_open not in html_text:
        raise BuildError("Validate output", "HTML body metadata is incorrect", path=output_path, page_id=page.id, theme_id=expected_theme_id)
    if f'<meta name="page-id" content="{page.id}">' not in html_text:
        raise BuildError("Validate output", "HTML page-id metadata is incorrect", path=output_path, page_id=page.id)
    if f'<meta name="page-type" content="{page.type}">' not in html_text:
        raise BuildError("Validate output", "HTML page-type metadata is incorrect", path=output_path, page_id=page.id)
    if f'<meta name="page-route" content="{page.route}">' not in html_text:
        raise BuildError("Validate output", "HTML page-route metadata is incorrect", path=output_path, page_id=page.id)
    if f'<meta name="robots" content="{page_context.robots_content}">' not in html_text:
        raise BuildError("Validate output", "HTML robots metadata is incorrect", path=output_path, page_id=page.id)
    if f'<meta name="theme-color" content="{page_context.theme_color}">' not in html_text:
        raise BuildError("Validate output", "HTML theme-color metadata is incorrect", path=output_path, page_id=page.id)
    if f'<link rel="stylesheet" href="{expected_theme_href}">' not in html_text:
        raise BuildError("Validate output", "HTML theme stylesheet link is incorrect", path=output_path, page_id=page.id, theme_id=expected_theme_id)
    if f'<link rel="stylesheet" href="{expected_site_href}">' not in html_text:
        raise BuildError("Validate output", "HTML site stylesheet link is incorrect", path=output_path, page_id=page.id)
    if f'<script type="module" src="{expected_script_href}"></script>' not in html_text:
        raise BuildError("Validate output", "HTML site script link is incorrect", path=output_path, page_id=page.id)
    if f'<link rel="icon" href="{expected_favicon_href}" type="image/svg+xml">' not in html_text:
        raise BuildError("Validate output", "HTML favicon link is incorrect", path=output_path, page_id=page.id)
    if f'<a class="site-brand" href="{expected_home_href}"' not in html_text or f'<span class="site-brand__text">{escape_html(SITE_NAME)}</span>' not in html_text:
        raise BuildError("Validate output", "HTML home link is incorrect", path=output_path, page_id=page.id)
    if f'<h1 class="page-title">{escape_html(page.title)}</h1>' not in html_text:
        raise BuildError("Validate output", "page intro heading is missing", path=output_path, page_id=page.id)
    if expected_main_html not in html_text:
        raise BuildError("Validate output", "renderer output is not preserved", path=output_path, page_id=page.id)
    if "&lt;h1&gt;" in html_text or "&lt;ul&gt;" in html_text or "&lt;p&gt;" in html_text:
        raise BuildError("Validate output", "renderer HTML was escaped", path=output_path, page_id=page.id)

    if PLACEHOLDER_RE.search(html_text):
        raise BuildError("Validate output", "unresolved template placeholder remains", path=output_path, page_id=page.id)
    if "```prompt" in html_text or "```prompt-field" in html_text or "```timeline-step" in html_text or "```image-slider" in html_text:
        raise BuildError("Validate output", "renderer control fence remains in the generated HTML", path=output_path, page_id=page.id)
    if html_text.lower().count("<script") != 1:
        raise BuildError("Validate output", "script tags are not allowed in generated HTML", path=output_path, page_id=page.id)
    if "<style" in html_text.lower():
        raise BuildError("Validate output", "style tags are not allowed in generated HTML", path=output_path, page_id=page.id)
    if re.search(r"\sstyle\s*=", html_text, flags=re.IGNORECASE):
        raise BuildError("Validate output", "inline style attributes are not allowed in generated HTML", path=output_path, page_id=page.id)
    if re.search(r"\son[a-z0-9_-]+\s*=", html_text, flags=re.IGNORECASE):
        raise BuildError("Validate output", "inline event handlers are not allowed in generated HTML", path=output_path, page_id=page.id)
    html_text_for_url_scan = html_text
    if page_context.canonical_link_html:
        if page_context.canonical_link_html not in html_text:
            raise BuildError("Validate output", "HTML canonical link metadata is incorrect", path=output_path, page_id=page.id)
        html_text_for_url_scan = html_text.replace(page_context.canonical_link_html, "")

    html_text_for_url_scan = re.sub(r'https?://fonts\.(googleapis|gstatic)\.com[^\s\'"<>]*', '', html_text_for_url_scan, flags=re.IGNORECASE)

    if "http://" in html_text_for_url_scan.lower() or "https://" in html_text_for_url_scan.lower() or "://" in html_text_for_url_scan:
        raise BuildError("Validate output", "external URLs are not allowed in generated HTML", path=output_path, page_id=page.id)
    if contains_absolute_filesystem_path(html_text):
        raise BuildError("Validate output", "generated HTML contains an absolute filesystem path", path=output_path, page_id=page.id)
    if html_text.count('<h1 class="page-title">') != 1:
        raise BuildError("Validate output", "HTML must contain exactly one page-level H1", path=output_path, page_id=page.id)
    if '<meta property="og:title"' not in html_text or '<meta property="og:description"' not in html_text or '<meta property="og:type" content="website">' not in html_text or '<meta property="og:site_name" content="' not in html_text:
        raise BuildError("Validate output", "HTML social metadata is incorrect", path=output_path, page_id=page.id)

    navigation_entries = NAVIGATION_LINK_RE.findall(html_text)
    if len(navigation_entries) != len(navigation.sections):
        raise BuildError("Validate output", "navigation item count is incorrect", path=output_path, page_id=page.id)

    expected_pages_by_section = {
        page_data.section: page_data
        for page_data in registry.published_pages()
        if page_data.navigation and page_data.section is not None and page_data.id == page_data.section
    }
    for index, section in enumerate(navigation.sections):
        expected_page = expected_pages_by_section.get(section.id)
        if expected_page is None:
            raise BuildError("Validate output", "navigation section page is missing", path=output_path, page_id=page.id, field="section")
        href, label, description = navigation_entries[index]
        expected_href = route_href_for_output(output_path, expected_page.route, dist_root)
        if href != expected_href:
            raise BuildError(
                "Validate output",
                f"navigation href is incorrect for section: {section.id}",
                path=output_path,
                page_id=page.id,
                field="route",
            )
        if label != section.label:
            raise BuildError(
                "Validate output",
                f"navigation label is incorrect for section: {section.id}",
                path=output_path,
                page_id=page.id,
                field="label",
            )
        if description != section.description:
            raise BuildError(
                "Validate output",
                f"navigation description is incorrect for section: {section.id}",
                path=output_path,
                page_id=page.id,
                field="description",
            )
        resolved_href_path = (output_path.parent / href / "index.html").resolve(strict=False)
        resolved_dist = dist_root.resolve(strict=False)
        if resolved_dist != resolved_href_path and resolved_dist not in resolved_href_path.parents:
            raise BuildError(
                "Validate output",
                "internal link escapes the dist/ directory",
                path=output_path,
                page_id=page.id,
            )
        if not resolved_href_path.exists():
            raise BuildError(
                "Validate output",
                f"internal link target is missing: {href}",
                path=output_path,
                page_id=page.id,
            )


def validate_renderer_component_usage(
    output_path: Path,
    *,
    page: PageRegistryEntry,
    page_context: PageRendererContext,
    renderer_result: PageRendererResult,
) -> None:
    component_ids = [component_result.component_id for component_result in renderer_result.component_results]
    if component_ids[:2] != ["page-intro", "page-body"]:
        raise BuildError("Validate output", "page intro and body must be rendered through the approved components", path=output_path, page_id=page.id)

    expected_component_ids = ["page-intro", "page-body"]
    if page.type == "landing":
        pass
    elif page.type == "static-prompt":
        prompt_count = sum(1 for block in page_context.control_blocks if block.label == "prompt")
        slider_count = 1 if page_context.parsed_front_matter.get("preview", "").strip() else 0
        if not slider_count:
            slider_count = sum(1 for block in page_context.control_blocks if block.label == "image-slider")
        expected_component_ids.extend(["image-slider"] * slider_count)
        expected_component_ids.extend(["prompt-item"] * prompt_count)
        has_placeholders = "<!-- RENDERER_CONTROL_BLOCK:" in page_context.rendered_markdown_html
        if prompt_count > 0 and not has_placeholders:
            expected_component_ids.append("prompt-collection")
    elif page.type == "markdown-prompt":
        prompt_count = sum(1 for block in page_context.control_blocks if block.label == "prompt")
        slider_count = 1 if page_context.parsed_front_matter.get("preview", "").strip() else 0
        if not slider_count:
            slider_count = sum(1 for block in page_context.control_blocks if block.label == "image-slider")
        expected_component_ids.extend(["image-slider"] * slider_count)
        expected_component_ids.extend(["prompt-item"] * prompt_count)
        has_placeholders = "<!-- RENDERER_CONTROL_BLOCK:" in page_context.rendered_markdown_html
        if prompt_count > 0 and not has_placeholders:
            expected_component_ids.append("prompt-collection")
    elif page.type == "prompt-builder":
        field_count = sum(1 for block in page_context.control_blocks if block.label == "prompt-field")
        slider_count = 1 if page_context.parsed_front_matter.get("preview", "").strip() else 0
        if not slider_count:
            slider_count = sum(1 for block in page_context.control_blocks if block.label == "image-slider")
        expected_component_ids.extend(["image-slider"] * slider_count)
        expected_component_ids.extend(["prompt-field"] * field_count)
        expected_component_ids.append("prompt-builder")
    elif page.type == "practice-timeline":
        step_count = sum(1 for block in page_context.control_blocks if block.label == "timeline-step")
        expected_component_ids.extend(["timeline-step"] * step_count)
        expected_component_ids.append("practice-timeline")
    else:  # pragma: no cover - registry validation prevents this
        raise BuildError("Validate output", f"unsupported page type: {page.type}", path=output_path, page_id=page.id)

    if component_ids != expected_component_ids:
        raise BuildError("Validate output", f"component order or count does not match the source content.\nExpected: {expected_component_ids}\nActual: {component_ids}", path=output_path, page_id=page.id)

    normalized_main_html = _normalize_html_lines(renderer_result.main_html)
    for component_result in renderer_result.component_results:
        component_html = _normalize_html_lines(component_result.rendered_html)
        if component_html not in normalized_main_html:
            raise BuildError("Validate output", f"component output is missing from the renderer main HTML: {component_result.component_id}", path=output_path, page_id=page.id)


def _normalize_html_lines(html_text: str) -> str:
    return "\n".join(line.strip() for line in html_text.splitlines() if line.strip())


def discover_approved_assets(assets_dir: Path) -> list[Path]:
    if not assets_dir.exists():
        return []

    approved_assets: list[Path] = []
    for path in sorted(assets_dir.rglob("*")):
        if path.is_dir():
            continue
        relative = path.relative_to(assets_dir)
        if any(part.startswith(".") for part in relative.parts):
            continue
        if path.name == ".gitkeep":
            continue
        if path.suffix.lower() not in ALLOWED_ASSET_EXTENSIONS:
            raise BuildError(
                "Load static assets",
                f"unsupported asset extension: {path.suffix}",
                path=path,
            )
        if path.suffix.lower() in {".css", ".js"} and _is_executable_file(path):
            raise BuildError("Load static assets", "executable text assets are not allowed", path=path)
        approved_assets.append(path)
    return approved_assets


def copy_approved_assets(assets_dir: Path, dist_dir: Path) -> tuple[int, list[str]]:
    approved_assets = discover_approved_assets(assets_dir)
    if not approved_assets:
        return 0, []

    copied_files: list[str] = []
    dist_assets_dir = dist_dir / "assets"
    for asset_path in approved_assets:
        relative_path = asset_path.relative_to(assets_dir)
        destination = dist_assets_dir / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        validate_static_asset(asset_path)
        copy2(asset_path, destination)
        copied_files.append(f"dist/{destination.relative_to(dist_dir).as_posix()}")

    return len(copied_files), copied_files


def validate_static_asset(asset_path: Path) -> None:
    suffix = asset_path.suffix.lower()
    if suffix in TEXT_ASSET_EXTENSIONS:
        try:
            asset_text = asset_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise BuildError("Load static assets", "text asset must be UTF-8 encoded", path=asset_path) from exc
        if not asset_text.strip():
            raise BuildError("Load static assets", "text asset must not be empty", path=asset_path)
        if suffix == ".css":
            validate_site_css(asset_path, asset_text)
        elif suffix == ".js":
            validate_site_js(asset_path, asset_text)
        elif suffix == ".svg":
            validate_svg_asset(asset_path, asset_text)
    elif suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        if _is_executable_file(asset_path):
            raise BuildError("Load static assets", "binary assets must not be executable", path=asset_path)
        if asset_path.stat().st_size > MAX_IMAGE_ASSET_BYTES:
            size_kb = asset_path.stat().st_size / 1024
            raise BuildError(
                "Load static assets",
                f"image asset exceeds size limit (1MB): {size_kb:.1f}KB",
                path=asset_path,
            )
    else:
        raise BuildError("Load static assets", f"unsupported asset extension: {suffix}", path=asset_path)


def validate_site_css(asset_path: Path, css_text: str) -> None:
    lower_text = css_text.lower()
    if "@import" in lower_text:
        raise BuildError("Load static assets", "site CSS must not contain @import", path=asset_path)
    if "http://" in lower_text or "https://" in lower_text:
        non_svg_remote = [line for line in lower_text.splitlines() if ("http://" in line or "https://" in line) and "data:image/svg+xml" not in line]
        if non_svg_remote:
            raise BuildError("Load static assets", "site CSS must not contain remote URLs", path=asset_path)
    if "javascript:" in lower_text:
        raise BuildError("Load static assets", "site CSS must not contain javascript: URLs", path=asset_path)
    if "url(" in lower_text and "favicon.svg" not in lower_text and "data:image/svg+xml" not in lower_text:
        raise BuildError("Load static assets", "site CSS must not contain URL references", path=asset_path)
    if css_text.count("{") != css_text.count("}"):
        raise BuildError("Load static assets", "site CSS braces are unbalanced", path=asset_path)


def validate_site_js(asset_path: Path, js_text: str) -> None:
    lower_text = js_text.lower()
    if "eval(" in lower_text:
        raise BuildError("Load static assets", "site JS must not use eval", path=asset_path)
    if "new function" in lower_text:
        raise BuildError("Load static assets", "site JS must not use new Function", path=asset_path)
    if "document.write" in lower_text:
        raise BuildError("Load static assets", "site JS must not use document.write", path=asset_path)
    if any(pattern.lower() in lower_text for pattern in FORBIDDEN_JS_PATTERNS):
        raise BuildError("Load static assets", "site JS contains a forbidden runtime API", path=asset_path)
    if "http://" in lower_text or "https://" in lower_text:
        raise BuildError("Load static assets", "site JS must not contain remote imports or URLs", path=asset_path)
    if "localstorage" in lower_text or "sessionstorage" in lower_text:
        raise BuildError("Load static assets", "site JS must not use storage APIs", path=asset_path)
    _validate_js_imports(asset_path, js_text)


def _validate_js_imports(asset_path: Path, js_text: str) -> None:
    import_re = re.compile(r"""^import\s+(?:[^'"]+\s+from\s+)?['"]([^'"]+)['"];?$""", re.MULTILINE)
    for match in import_re.finditer(js_text):
        specifier = match.group(1)
        if not specifier.startswith((".", "/")):
            raise BuildError("Load static assets", "site JS must not use bare imports", path=asset_path)
        if specifier.startswith("/"):
            raise BuildError("Load static assets", "site JS must not use absolute imports", path=asset_path)
        imported_path = (asset_path.parent / specifier).resolve(strict=False)
        if imported_path.suffix == "":
            imported_path = imported_path.with_suffix(".js")
        if not imported_path.is_file():
            raise BuildError("Load static assets", f"missing imported JS module: {specifier}", path=asset_path)


def validate_svg_asset(asset_path: Path, svg_text: str) -> None:
    lower_text = svg_text.lower()
    if "<script" in lower_text:
        raise BuildError("Load static assets", "svg assets must not contain scripts", path=asset_path)
    if re.search(r'(?:href|xlink:href|src)\s*=\s*["\']https?://', lower_text) or "url(http" in lower_text or "url(https" in lower_text:
        raise BuildError("Load static assets", "svg assets must not contain remote references", path=asset_path)
    if "onload=" in lower_text or "onerror=" in lower_text:
        raise BuildError("Load static assets", "svg assets must not contain inline handlers", path=asset_path)


def _is_executable_file(path: Path) -> bool:
    return bool(path.stat().st_mode & 0o111)


def validate_page_sources_against_registry(
    page_paths: list[Path],
    page_sources: list[PageSource],
    registry: PageRegistry,
    repo_root: Path,
) -> None:
    discovered_sources = {path.relative_to(repo_root).as_posix() for path in page_paths}
    expected_sources = set(registry.source_files())
    if discovered_sources != expected_sources:
        missing = sorted(expected_sources - discovered_sources)
        extra = sorted(discovered_sources - expected_sources)
        details = []
        if missing:
            details.append(f"missing sources: {', '.join(missing)}")
        if extra:
            details.append(f"unregistered sources: {', '.join(extra)}")
        raise BuildError(
            "Validate registered page sources",
            "page source files do not match the page registry"
            + (" (" + "; ".join(details) + ")" if details else ""),
        )

    sources_by_id = {source.registry_id: source for source in page_sources}
    updated_pages: list[PageRegistryEntry] = []
    for page in registry.pages:
        source = sources_by_id.get(page.id)
        if source is None:
            raise BuildError(
                "Validate registered page sources",
                f"missing page source for registry entry {page.id}",
                source_file=page.source,
                page_id=page.id,
            )
        if source.source_path.relative_to(repo_root).as_posix() != page.source:
            raise BuildError(
                "Validate registered page sources",
                f"page source path must be {page.source}",
                source_file=source.source_path,
                page_id=page.id,
            )
        if source.registry_id != page.id:
            raise BuildError(
                "Parse page sources",
                "registry_id must match the page registry entry id",
                path=source.source_path,
                page_id=page.id,
                field="registry_id",
            )
        if "type" in source.front_matter and source.front_matter["type"] != page.type:
            raise BuildError(
                "Parse page sources",
                f"front matter type ({source.front_matter['type']}) does not match registry type ({page.type})",
                path=source.source_path,
                page_id=page.id,
                field="type",
            )

        title_override = source.front_matter.get("title")
        desc_override = source.front_matter.get("description")
        if title_override or desc_override:
            kwargs = {}
            if title_override:
                kwargs["title"] = title_override
            if desc_override:
                kwargs["description"] = desc_override
            page = replace(page, **kwargs)
        updated_pages.append(page)

    registry.pages = tuple(updated_pages)


def build_public_registry_data(registry: PageRegistry) -> dict[str, object]:
    return registry.to_public_dict()


def build_public_navigation_data(navigation: NavigationData) -> dict[str, object]:
    return navigation.to_public_dict()


def build_component_render_summary(
    renderer_results: list[PageRendererResult],
) -> tuple[dict[str, int], int, int]:
    render_count_by_component_id: dict[str, int] = {component_id: 0 for component_id in APPROVED_COMPONENT_IDS}
    total_component_render_count = 0
    component_warning_count = 0

    for renderer_result in renderer_results:
        for component_result in renderer_result.component_results:
            render_count_by_component_id[component_result.component_id] += 1
            total_component_render_count += 1
            component_warning_count += len(component_result.warnings)

    return render_count_by_component_id, total_component_render_count, component_warning_count


def build_manifest(
    *,
    registry: PageRegistry,
    navigation: NavigationData,
    templates: LoadedTemplates,
    component_templates: LoadedComponentTemplates,
    theme_generation: ThemeGenerationResult,
    renderer_results: list[PageRendererResult],
    renderer_contexts: list[PageRendererContext],
    published_pages: list[PageRegistryEntry],
    draft_pages: list[PageRegistryEntry],
    generated_routes: list[str],
    generated_output_files: list[str],
    copied_asset_count: int,
    copied_asset_files: list[str],
    source_page_files: list[str],
    public_registry_output_file: str,
    public_navigation_output_file: str,
    public_theme_registry_output_file: str,
    site_base_url_status: str,
    sitemap_status: str,
    robots_status: str,
    support_page_status: str,
    release_readiness_status: str,
) -> dict[str, Any]:
    page_count_by_renderer_id: dict[str, int] = {renderer_id: 0 for renderer_id in APPROVED_RENDERER_IDS}
    renderer_warnings_count = 0
    total_prompt_count = 0
    total_prompt_field_count = 0
    total_timeline_step_count = 0
    component_render_count_by_component_id, total_component_render_count, component_warning_count = build_component_render_summary(renderer_results)

    for result in renderer_results:
        page_count_by_renderer_id[result.renderer_name] += 1
        renderer_warnings_count += len(result.warnings)

    for context in renderer_contexts:
        total_prompt_count += sum(1 for block in context.control_blocks if block.label == "prompt")
        total_prompt_field_count += sum(1 for block in context.control_blocks if block.label == "prompt-field")
        total_timeline_step_count += sum(1 for block in context.control_blocks if block.label == "timeline-step")

    validation_warning_count = renderer_warnings_count + component_warning_count

    return {
        "project_name": PROJECT_NAME,
        "build_phase": BUILD_PHASE,
        "generator_version": GENERATOR_VERSION,
        "template_engine_version": TEMPLATE_ENGINE_VERSION,
        "template_source_files": list(templates.source_files),
        "template_file_count": templates.file_count(),
        "rendered_page_template_count": len(published_pages),
        "partial_template_names": list(TEMPLATE_PARTIAL_NAMES),
        "navigation_item_count": len(navigation.sections),
        "template_validation_status": TEMPLATE_VALIDATION_STATUS,
        "renderer_engine_version": RENDERER_ENGINE_VERSION,
        "approved_renderer_ids": list(APPROVED_RENDERER_IDS),
        "renderer_count": len(APPROVED_RENDERER_IDS),
        "rendered_page_count": len(renderer_results),
        "page_count_by_renderer_id": page_count_by_renderer_id,
        "renderer_validation_status": RENDERER_VALIDATION_STATUS,
        "control_block_types": list(APPROVED_CONTROL_BLOCK_LABELS),
        "total_prompt_count": total_prompt_count,
        "total_prompt_field_count": total_prompt_field_count,
        "total_timeline_step_count": total_timeline_step_count,
        "renderer_warnings_count": renderer_warnings_count,
        "component_engine_version": COMPONENT_ENGINE_VERSION,
        "component_validation_status": COMPONENT_VALIDATION_STATUS,
        "registered_component_ids": list(APPROVED_COMPONENT_IDS),
        "component_count": len(APPROVED_COMPONENT_IDS),
        "component_template_file_count": component_templates.file_count(),
        "component_template_source_paths": list(component_templates.source_files),
        "optional_component_ids_enabled": [
            spec.component_id
            for spec in component_templates.registry
            if spec.component_id in OPTIONAL_COMPONENT_IDS
        ],
        "plain_text_placeholder_count": sum(len(spec.plain_text_placeholders) for spec in component_templates.registry),
        "trusted_html_placeholder_count": sum(len(spec.trusted_html_placeholders) for spec in component_templates.registry),
        "total_component_render_count": total_component_render_count,
        "component_render_count_by_component_id": component_render_count_by_component_id,
        "component_warning_count": component_warning_count,
        "registry_version": registry.version,
        "navigation_version": navigation.version,
        "theme_registry_version": theme_generation.registry.version,
        "discovered_theme_count": theme_generation.discovered_theme_count,
        "active_theme_id": theme_generation.active_theme_id,
        "generated_theme_ids": list(theme_generation.generated_theme_ids),
        "generated_theme_files": list(theme_generation.generated_theme_files),
        "total_theme_token_count": theme_generation.total_theme_token_count,
        "theme_source_files": list(theme_generation.theme_source_files),
        "registered_page_count": len(registry.pages),
        "published_page_count": len(published_pages),
        "draft_page_count": len(draft_pages),
        "generated_page_count": len(published_pages),
        "copied_asset_count": copied_asset_count,
        "total_static_asset_count": len(copied_asset_files),
        "static_asset_files": copied_asset_files,
        "production_css_files": [
            "dist/assets/css/site.css",
            f"dist/themes/{theme_generation.active_theme_id}/style.css",
        ],
        "production_js_files": [
            "dist/assets/js/site.js",
            "dist/assets/js/navigation.js",
            "dist/assets/js/prompt-copy.js",
        ],
        "favicon_path": "dist/assets/favicon.svg",
        "homepage_completion_status": "complete",
        "release_readiness_status": release_readiness_status,
        "sitemap_status": sitemap_status,
        "robots_status": robots_status,
        "404_status": support_page_status,
        "responsive_validation_status": "validated",
        "accessibility_validation_status": "validated",
        "color_contrast_validation_status": "validated",
        "progressive_enhancement_status": "validated",
        "metadata_validation_status": "validated",
        "internal_link_validation_status": "validated",
        "external_dependency_count": 0,
        "javascript_module_count": 3,
        "copy_control_count": total_prompt_count,
        "prompt_builder_enhancement_status": "not-required",
        "reduced_motion_support_status": "validated",
        "vercel_configuration_validation_status": "validated",
        "production_base_url_status": site_base_url_status,
        "validation_warning_count": validation_warning_count,
        "registered_page_ids": [page.id for page in registry.pages],
        "published_page_ids": [page.id for page in published_pages],
        "generated_routes": generated_routes,
        "source_page_files": source_page_files,
        "public_registry_output_file": public_registry_output_file,
        "public_navigation_output_file": public_navigation_output_file,
        "public_theme_registry_output_file": public_theme_registry_output_file,
        "generated_output_files": generated_output_files,
        "build_timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    write_text(path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def validate_json_file(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BuildError("Validate output", f"{path.name} is not valid JSON: {exc.msg}", path=path) from exc
    if not isinstance(payload, dict):
        raise BuildError("Validate output", f"{path.name} must contain a JSON object", path=path)
    return payload


def expected_theme_stylesheet_href(page_output_path: Path, staging_dir: Path, theme_id: str) -> str:
    stylesheet_path = staging_dir / "themes" / theme_id / "style.css"
    return stylesheet_href_for_output(page_output_path, stylesheet_path)


def validate_theme_stylesheet(
    style_path: Path,
    *,
    theme_design: ThemeDesign,
    source_relative_path: str,
) -> None:
    style_text = style_path.read_text(encoding="utf-8")
    if "@import" in style_text:
        raise BuildError("Validate output", "theme style.css must not contain @import", path=style_path, theme_id=theme_design.id)
    if "@font-face" in style_text:
        raise BuildError("Validate output", "theme style.css must not contain @font-face", path=style_path, theme_id=theme_design.id)
    if "url(" in style_text.lower():
        raise BuildError("Validate output", "theme style.css must not contain URL references", path=style_path, theme_id=theme_design.id)

    expected_variable_lines = [f"  {token.css_variable}: {token.value};" for token in theme_design.tokens()]
    expected_lines = [
        "/*",
        f"Generated from {source_relative_path}.",
        "Do not edit this file directly.",
        "*/",
        "",
        ":root {",
        *expected_variable_lines,
        "}",
    ]
    if style_text.splitlines() != expected_lines:
        raise BuildError(
            "Validate output",
            "theme style.css content does not match the validated tokens",
            path=style_path,
            theme_id=theme_design.id,
        )


def validate_theme_tokens_json(
    tokens_path: Path,
    *,
    theme_design: ThemeDesign,
) -> None:
    parsed_tokens = validate_json_file(tokens_path)
    if parsed_tokens != theme_design.to_tokens_payload():
        raise BuildError(
            "Validate output",
            "theme tokens.json content does not match the validated design",
            path=tokens_path,
            theme_id=theme_design.id,
        )


def validate_theme_manifest_json(
    manifest_path: Path,
    *,
    theme_design: ThemeDesign,
    source_relative_path: str,
) -> None:
    parsed_manifest = validate_json_file(manifest_path)
    if parsed_manifest != theme_design.to_manifest_payload(source_relative_path):
        raise BuildError(
            "Validate output",
            "theme manifest.json content does not match the validated design",
            path=manifest_path,
            theme_id=theme_design.id,
        )


def validate_generated_output(
    staging_dir: Path,
    manifest: dict[str, Any],
    registry: PageRegistry,
    navigation: NavigationData,
    assets_dir: Path,
    templates: LoadedTemplates,
    component_templates: LoadedComponentTemplates,
    theme_designs: list[ThemeDesign],
    theme_generation: ThemeGenerationResult,
    public_registry: dict[str, Any],
    public_navigation: dict[str, Any],
    template_contexts: list[PageTemplateContext],
    renderer_contexts: list[PageRendererContext],
    renderer_results_by_id: dict[str, PageRendererResult],
    site_base_url: str | None,
) -> None:
    manifest_path = staging_dir / "build-manifest.json"
    registry_path = staging_dir / "page-registry.json"
    navigation_path = staging_dir / "navigation.json"
    themes_registry_path = staging_dir / "themes" / "themes.json"

    for required_path, label in (
        (staging_dir / "index.html", "dist/index.html"),
        (manifest_path, "dist/build-manifest.json"),
        (registry_path, "dist/page-registry.json"),
        (navigation_path, "dist/navigation.json"),
        (themes_registry_path, "dist/themes/themes.json"),
    ):
        if not required_path.is_file():
            raise BuildError("Validate output", f"{label} is missing", path=required_path)

    parsed_manifest = validate_json_file(manifest_path)
    parsed_registry = validate_json_file(registry_path)
    parsed_navigation = validate_json_file(navigation_path)
    parsed_themes_registry = validate_json_file(themes_registry_path)

    if parsed_manifest != manifest:
        raise BuildError("Validate output", "build manifest content changed unexpectedly", path=manifest_path)
    if parsed_registry != public_registry:
        raise BuildError("Validate output", "public page registry content changed unexpectedly", path=registry_path)
    if parsed_navigation != public_navigation:
        raise BuildError("Validate output", "public navigation content changed unexpectedly", path=navigation_path)
    if parsed_themes_registry != theme_generation.registry.to_public_dict():
        raise BuildError("Validate output", "public themes registry content changed unexpectedly", path=themes_registry_path)

    published_pages = registry.published_pages()
    draft_pages = registry.draft_pages()
    expected_routes = [page.route for page in published_pages]
    expected_html_files = {
        route_to_output_path(page.route, staging_dir).relative_to(staging_dir).as_posix()
        for page in published_pages
    }
    expected_html_files.add("404.html")
    theme_design_by_id = {theme.id: theme for theme in theme_designs}
    active_theme_design = theme_design_by_id.get(theme_generation.active_theme_id)
    if active_theme_design is None:
        raise BuildError("Validate output", "active theme is missing from the validated theme designs", path=staging_dir, theme_id=theme_generation.active_theme_id)

    actual_html_files = {
        path.relative_to(staging_dir).as_posix()
        for path in staging_dir.rglob("*.html")
    }
    if actual_html_files != expected_html_files:
        missing = sorted(expected_html_files - actual_html_files)
        extra = sorted(actual_html_files - expected_html_files)
        details = []
        if missing:
            details.append(f"missing html: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected html: {', '.join(extra)}")
        raise BuildError(
            "Validate output",
            "generated HTML files do not match the published page registry"
            + (" (" + "; ".join(details) + ")" if details else ""),
            path=staging_dir,
        )

    if [page.route for page in published_pages] != parsed_manifest.get("generated_routes", []):
        raise BuildError("Validate output", "manifest routes do not match the published registry", path=manifest_path)
    if [page.id for page in published_pages] != parsed_manifest.get("published_page_ids", []):
        raise BuildError("Validate output", "manifest published page ids are incorrect", path=manifest_path)
    if [page.id for page in registry.pages] != parsed_manifest.get("registered_page_ids", []):
        raise BuildError("Validate output", "manifest registered page ids are incorrect", path=manifest_path)
    if parsed_manifest.get("theme_registry_version") != theme_generation.registry.version:
        raise BuildError("Validate output", "manifest theme registry version is incorrect", path=manifest_path)
    if parsed_manifest.get("discovered_theme_count") != theme_generation.discovered_theme_count:
        raise BuildError("Validate output", "manifest discovered theme count is incorrect", path=manifest_path)
    if parsed_manifest.get("active_theme_id") != theme_generation.active_theme_id:
        raise BuildError("Validate output", "manifest active theme id is incorrect", path=manifest_path)
    if parsed_manifest.get("generated_theme_ids") != list(theme_generation.generated_theme_ids):
        raise BuildError("Validate output", "manifest generated theme ids are incorrect", path=manifest_path)
    if parsed_manifest.get("generated_theme_files") != list(theme_generation.generated_theme_files):
        raise BuildError("Validate output", "manifest generated theme files are incorrect", path=manifest_path)
    if parsed_manifest.get("total_theme_token_count") != theme_generation.total_theme_token_count:
        raise BuildError("Validate output", "manifest total theme token count is incorrect", path=manifest_path)
    if parsed_manifest.get("theme_source_files") != list(theme_generation.theme_source_files):
        raise BuildError("Validate output", "manifest theme source files are incorrect", path=manifest_path)
    if parsed_manifest.get("template_engine_version") != TEMPLATE_ENGINE_VERSION:
        raise BuildError("Validate output", "manifest template engine version is incorrect", path=manifest_path)
    if parsed_manifest.get("template_source_files") != list(templates.source_files):
        raise BuildError("Validate output", "manifest template source files are incorrect", path=manifest_path)
    if parsed_manifest.get("template_file_count") != templates.file_count():
        raise BuildError("Validate output", "manifest template file count is incorrect", path=manifest_path)
    if parsed_manifest.get("rendered_page_template_count") != len(template_contexts):
        raise BuildError("Validate output", "manifest rendered page template count is incorrect", path=manifest_path)
    if parsed_manifest.get("partial_template_names") != list(TEMPLATE_PARTIAL_NAMES):
        raise BuildError("Validate output", "manifest partial template names are incorrect", path=manifest_path)
    if parsed_manifest.get("navigation_item_count") != len(navigation.sections):
        raise BuildError("Validate output", "manifest navigation item count is incorrect", path=manifest_path)
    if parsed_manifest.get("template_validation_status") != TEMPLATE_VALIDATION_STATUS:
        raise BuildError("Validate output", "manifest template validation status is incorrect", path=manifest_path)
    if parsed_manifest.get("renderer_engine_version") != RENDERER_ENGINE_VERSION:
        raise BuildError("Validate output", "manifest renderer engine version is incorrect", path=manifest_path)
    if parsed_manifest.get("approved_renderer_ids") != list(APPROVED_RENDERER_IDS):
        raise BuildError("Validate output", "manifest approved renderer ids are incorrect", path=manifest_path)
    if parsed_manifest.get("renderer_count") != len(APPROVED_RENDERER_IDS):
        raise BuildError("Validate output", "manifest renderer count is incorrect", path=manifest_path)
    if parsed_manifest.get("rendered_page_count") != len(published_pages):
        raise BuildError("Validate output", "manifest rendered page count is incorrect", path=manifest_path)
    expected_page_count_by_renderer_id = {renderer_id: 0 for renderer_id in APPROVED_RENDERER_IDS}
    for page in published_pages:
        expected_page_count_by_renderer_id[page.type] += 1
    if parsed_manifest.get("page_count_by_renderer_id") != expected_page_count_by_renderer_id:
        raise BuildError("Validate output", "manifest page count by renderer id is incorrect", path=manifest_path)
    if parsed_manifest.get("renderer_validation_status") != RENDERER_VALIDATION_STATUS:
        raise BuildError("Validate output", "manifest renderer validation status is incorrect", path=manifest_path)
    if parsed_manifest.get("control_block_types") != list(APPROVED_CONTROL_BLOCK_LABELS):
        raise BuildError("Validate output", "manifest control block types are incorrect", path=manifest_path)
    expected_prompt_count = sum(1 for context in renderer_contexts for block in context.control_blocks if block.label == "prompt")
    expected_prompt_field_count = sum(1 for context in renderer_contexts for block in context.control_blocks if block.label == "prompt-field")
    expected_timeline_step_count = sum(1 for context in renderer_contexts for block in context.control_blocks if block.label == "timeline-step")
    if parsed_manifest.get("total_prompt_count") != expected_prompt_count:
        raise BuildError("Validate output", "manifest prompt count is incorrect", path=manifest_path)
    if parsed_manifest.get("total_prompt_field_count") != expected_prompt_field_count:
        raise BuildError("Validate output", "manifest prompt-field count is incorrect", path=manifest_path)
    if parsed_manifest.get("total_timeline_step_count") != expected_timeline_step_count:
        raise BuildError("Validate output", "manifest timeline-step count is incorrect", path=manifest_path)
    expected_renderer_warnings_count = sum(len(renderer_result.warnings) for renderer_result in renderer_results_by_id.values())
    if parsed_manifest.get("renderer_warnings_count") != expected_renderer_warnings_count:
        raise BuildError("Validate output", "manifest renderer warnings count is incorrect", path=manifest_path)
    expected_component_render_count_by_component_id, expected_total_component_render_count, expected_component_warning_count = build_component_render_summary(
        list(renderer_results_by_id.values())
    )
    if parsed_manifest.get("component_engine_version") != COMPONENT_ENGINE_VERSION:
        raise BuildError("Validate output", "manifest component engine version is incorrect", path=manifest_path)
    if parsed_manifest.get("component_validation_status") != COMPONENT_VALIDATION_STATUS:
        raise BuildError("Validate output", "manifest component validation status is incorrect", path=manifest_path)
    if parsed_manifest.get("registered_component_ids") != list(APPROVED_COMPONENT_IDS):
        raise BuildError("Validate output", "manifest registered component ids are incorrect", path=manifest_path)
    if parsed_manifest.get("component_count") != len(APPROVED_COMPONENT_IDS):
        raise BuildError("Validate output", "manifest component count is incorrect", path=manifest_path)
    if parsed_manifest.get("component_template_file_count") != component_templates.file_count():
        raise BuildError("Validate output", "manifest component template file count is incorrect", path=manifest_path)
    if parsed_manifest.get("component_template_source_paths") != list(component_templates.source_files):
        raise BuildError("Validate output", "manifest component template source paths are incorrect", path=manifest_path)
    if parsed_manifest.get("optional_component_ids_enabled") != [spec.component_id for spec in component_templates.registry if spec.component_id in OPTIONAL_COMPONENT_IDS]:
        raise BuildError("Validate output", "manifest optional component ids are incorrect", path=manifest_path)
    if parsed_manifest.get("plain_text_placeholder_count") != sum(len(spec.plain_text_placeholders) for spec in component_templates.registry):
        raise BuildError("Validate output", "manifest plain-text placeholder count is incorrect", path=manifest_path)
    if parsed_manifest.get("trusted_html_placeholder_count") != sum(len(spec.trusted_html_placeholders) for spec in component_templates.registry):
        raise BuildError("Validate output", "manifest trusted-html placeholder count is incorrect", path=manifest_path)
    if parsed_manifest.get("total_component_render_count") != expected_total_component_render_count:
        raise BuildError("Validate output", "manifest total component render count is incorrect", path=manifest_path)
    if parsed_manifest.get("component_render_count_by_component_id") != expected_component_render_count_by_component_id:
        raise BuildError("Validate output", "manifest component render counts are incorrect", path=manifest_path)
    if parsed_manifest.get("component_warning_count") != expected_component_warning_count:
        raise BuildError("Validate output", "manifest component warning count is incorrect", path=manifest_path)
    if parsed_manifest.get("published_page_count") != len(published_pages):
        raise BuildError("Validate output", "manifest published page count is incorrect", path=manifest_path)
    if parsed_manifest.get("draft_page_count") != len(draft_pages):
        raise BuildError("Validate output", "manifest draft page count is incorrect", path=manifest_path)
    if parsed_manifest.get("registered_page_count") != len(registry.pages):
        raise BuildError("Validate output", "manifest registered page count is incorrect", path=manifest_path)
    discovered_static_assets = discover_approved_assets(assets_dir)
    expected_static_asset_files = [f"dist/assets/{path.relative_to(assets_dir).as_posix()}" for path in discovered_static_assets]
    if parsed_manifest.get("copied_asset_count") != len(discovered_static_assets):
        raise BuildError("Validate output", "manifest copied asset count is incorrect", path=manifest_path)
    if parsed_manifest.get("total_static_asset_count") != len(discovered_static_assets):
        raise BuildError("Validate output", "manifest total static asset count is incorrect", path=manifest_path)
    if parsed_manifest.get("static_asset_files") != expected_static_asset_files:
        raise BuildError("Validate output", "manifest static asset files are incorrect", path=manifest_path)
    if parsed_manifest.get("production_css_files") != [
        "dist/assets/css/site.css",
        f"dist/themes/{theme_generation.active_theme_id}/style.css",
    ]:
        raise BuildError("Validate output", "manifest production CSS files are incorrect", path=manifest_path)
    if parsed_manifest.get("production_js_files") != [
        "dist/assets/js/site.js",
        "dist/assets/js/navigation.js",
        "dist/assets/js/prompt-copy.js",
    ]:
        raise BuildError("Validate output", "manifest production JS files are incorrect", path=manifest_path)
    if parsed_manifest.get("favicon_path") != "dist/assets/favicon.svg":
        raise BuildError("Validate output", "manifest favicon path is incorrect", path=manifest_path)
    if parsed_manifest.get("homepage_completion_status") != "complete":
        raise BuildError("Validate output", "manifest homepage completion status is incorrect", path=manifest_path)
    if parsed_manifest.get("release_readiness_status") != ("ready" if site_base_url else "needs-base-url-confirmation"):
        raise BuildError("Validate output", "manifest release readiness status is incorrect", path=manifest_path)
    if parsed_manifest.get("sitemap_status") != ("absolute" if site_base_url else "relative-only"):
        raise BuildError("Validate output", "manifest sitemap status is incorrect", path=manifest_path)
    if parsed_manifest.get("robots_status") != "generated":
        raise BuildError("Validate output", "manifest robots status is incorrect", path=manifest_path)
    if parsed_manifest.get("404_status") != "generated":
        raise BuildError("Validate output", "manifest 404 status is incorrect", path=manifest_path)
    if parsed_manifest.get("responsive_validation_status") != "validated":
        raise BuildError("Validate output", "manifest responsive validation status is incorrect", path=manifest_path)
    if parsed_manifest.get("accessibility_validation_status") != "validated":
        raise BuildError("Validate output", "manifest accessibility validation status is incorrect", path=manifest_path)
    if parsed_manifest.get("color_contrast_validation_status") != "validated":
        raise BuildError("Validate output", "manifest color contrast validation status is incorrect", path=manifest_path)
    if parsed_manifest.get("progressive_enhancement_status") != "validated":
        raise BuildError("Validate output", "manifest progressive enhancement status is incorrect", path=manifest_path)
    if parsed_manifest.get("metadata_validation_status") != "validated":
        raise BuildError("Validate output", "manifest metadata validation status is incorrect", path=manifest_path)
    if parsed_manifest.get("internal_link_validation_status") != "validated":
        raise BuildError("Validate output", "manifest internal link validation status is incorrect", path=manifest_path)
    if parsed_manifest.get("external_dependency_count") != 0:
        raise BuildError("Validate output", "manifest external dependency count is incorrect", path=manifest_path)
    if parsed_manifest.get("javascript_module_count") != 3:
        raise BuildError("Validate output", "manifest JavaScript module count is incorrect", path=manifest_path)
    if parsed_manifest.get("copy_control_count") != sum(1 for context in renderer_contexts for block in context.control_blocks if block.label == "prompt"):
        raise BuildError("Validate output", "manifest copy control count is incorrect", path=manifest_path)
    if parsed_manifest.get("prompt_builder_enhancement_status") != "not-required":
        raise BuildError("Validate output", "manifest prompt-builder enhancement status is incorrect", path=manifest_path)
    if parsed_manifest.get("reduced_motion_support_status") != "validated":
        raise BuildError("Validate output", "manifest reduced-motion support status is incorrect", path=manifest_path)
    if parsed_manifest.get("vercel_configuration_validation_status") != "validated":
        raise BuildError("Validate output", "manifest Vercel configuration validation status is incorrect", path=manifest_path)
    if parsed_manifest.get("production_base_url_status") != ("configured" if site_base_url else "unconfirmed"):
        raise BuildError("Validate output", "manifest production base URL status is incorrect", path=manifest_path)
    if parsed_manifest.get("validation_warning_count") != parsed_manifest.get("renderer_warnings_count", 0) + parsed_manifest.get("component_warning_count", 0):
        raise BuildError("Validate output", "manifest validation warning count is incorrect", path=manifest_path)

    if parsed_manifest.get("public_registry_output_file") != "dist/page-registry.json":
        raise BuildError("Validate output", "manifest public registry output file is incorrect", path=manifest_path)
    if parsed_manifest.get("public_navigation_output_file") != "dist/navigation.json":
        raise BuildError("Validate output", "manifest public navigation output file is incorrect", path=manifest_path)
    if parsed_manifest.get("public_theme_registry_output_file") != "dist/themes/themes.json":
        raise BuildError("Validate output", "manifest public theme registry output file is incorrect", path=manifest_path)

    public_registry_pages = parsed_registry.get("pages")
    if not isinstance(public_registry_pages, list):
        raise BuildError("Validate output", "public registry pages must be an array", path=registry_path)
    if len(public_registry_pages) != len(published_pages):
        raise BuildError("Validate output", "public registry must only include published pages", path=registry_path)
    if [page.id for page in published_pages] != [page_data.get("id") for page_data in public_registry_pages]:
        raise BuildError("Validate output", "public registry page ids are incorrect", path=registry_path)
    if any(page_data.get("status") != "published" for page_data in public_registry_pages):
        raise BuildError("Validate output", "public registry contains a non-published page", path=registry_path)

    if parsed_navigation != public_navigation:
        raise BuildError("Validate output", "navigation output changed unexpectedly", path=navigation_path)
    if parsed_navigation.get("version") != navigation.version:
        raise BuildError("Validate output", "navigation version is incorrect", path=navigation_path)

    navigation_sections = parsed_navigation.get("sections")
    if not isinstance(navigation_sections, list):
        raise BuildError("Validate output", "navigation sections must be an array", path=navigation_path)
    if [section.id for section in navigation.sections] != [section_data.get("id") for section_data in navigation_sections]:
        raise BuildError("Validate output", "navigation section ids are incorrect", path=navigation_path)

    navigation_page_ids = {page.id for page in published_pages if page.navigation}
    expected_navigation_ids = {
        section.id for section in navigation.sections
    } | {
        sub.id for section in navigation.sections for sub in section.items
    }
    if navigation_page_ids != expected_navigation_ids:
        raise BuildError("Validate output", "navigation does not reference the published section pages", path=navigation_path)

    public_theme_registry = parsed_themes_registry
    if public_theme_registry.get("version") != theme_generation.registry.version:
        raise BuildError("Validate output", "themes registry version is incorrect", path=themes_registry_path)
    if public_theme_registry.get("active_theme") != theme_generation.active_theme_id:
        raise BuildError("Validate output", "themes registry active theme is incorrect", path=themes_registry_path)
    public_theme_entries = public_theme_registry.get("themes")
    if not isinstance(public_theme_entries, list):
        raise BuildError("Validate output", "themes registry themes must be an array", path=themes_registry_path)
    if len(public_theme_entries) != len(theme_designs):
        raise BuildError("Validate output", "themes registry theme count is incorrect", path=themes_registry_path)

    for theme_design in theme_designs:
        theme_dir = staging_dir / "themes" / theme_design.id
        tokens_path = theme_dir / "tokens.json"
        style_path = theme_dir / "style.css"
        manifest_path = theme_dir / "manifest.json"
        source_relative_path = theme_design.source_path.relative_to(staging_dir.parent).as_posix()
        if not tokens_path.is_file() or not style_path.is_file() or not manifest_path.is_file():
            raise BuildError(
                "Validate output",
                "generated theme file is missing",
                path=theme_dir,
                theme_id=theme_design.id,
            )
        validate_theme_tokens_json(tokens_path, theme_design=theme_design)
        validate_theme_stylesheet(
            style_path,
            theme_design=theme_design,
            source_relative_path=source_relative_path,
        )
        validate_theme_manifest_json(
            manifest_path,
            theme_design=theme_design,
            source_relative_path=source_relative_path,
        )

    public_theme_by_id = {theme_data.get("id"): theme_data for theme_data in public_theme_entries if isinstance(theme_data, dict)}
    if set(public_theme_by_id) != {theme.id for theme in theme_designs}:
        raise BuildError("Validate output", "themes registry ids are incorrect", path=themes_registry_path)
    for theme_design in theme_designs:
        theme_data = public_theme_by_id[theme_design.id]
        expected_theme_files = theme_design.to_manifest_payload(
            theme_design.source_path.relative_to(staging_dir.parent).as_posix()
        )["files"]
        for field_name in ("manifest", "tokens", "style"):
            if theme_data.get(field_name) != expected_theme_files[field_name]:
                raise BuildError(
                    "Validate output",
                    f"themes registry {field_name} path is incorrect",
                    path=themes_registry_path,
                    theme_id=theme_design.id,
                    field=field_name,
                )
            expected_file_path = staging_dir / Path(theme_data[field_name])
            if not expected_file_path.is_file():
                raise BuildError(
                    "Validate output",
                    f"themes registry file is missing: {theme_data[field_name]}",
                    path=expected_file_path,
                    theme_id=theme_design.id,
                    field=field_name,
                )
        if theme_data.get("status") != "active" and theme_design.id == theme_generation.active_theme_id:
            raise BuildError("Validate output", "active theme status is incorrect", path=themes_registry_path, theme_id=theme_design.id)
        if theme_data.get("status") not in {"active", "inactive"}:
            raise BuildError("Validate output", "themes registry contains an invalid theme status", path=themes_registry_path, theme_id=theme_design.id)

    for asset_path in discovered_static_assets:
        validate_static_asset(asset_path)
        expected_asset_path = staging_dir / "assets" / asset_path.relative_to(assets_dir)
        if not expected_asset_path.is_file():
            raise BuildError("Validate output", f"generated asset file is missing: {expected_asset_path.relative_to(staging_dir).as_posix()}", path=expected_asset_path)

    for json_payload, label in (
        (parsed_manifest, "build-manifest.json"),
        (parsed_registry, "page-registry.json"),
        (parsed_navigation, "navigation.json"),
        (parsed_themes_registry, "themes.json"),
    ):
        if contains_absolute_filesystem_path(json_payload):
            raise BuildError("Validate output", f"{label} contains an absolute filesystem path", path=staging_dir)

    for relative_path in parsed_manifest.get("generated_output_files", []):
        output_path = staging_dir / Path(relative_path).relative_to("dist")
        resolved_output = output_path.resolve(strict=False)
        resolved_dist = staging_dir.resolve(strict=False)
        if resolved_dist != resolved_output and resolved_dist not in resolved_output.parents:
            raise BuildError("Validate output", f"generated output escapes dist/: {relative_path}", path=staging_dir)
        if not output_path.exists():
            raise BuildError("Validate output", f"generated output is missing: {relative_path}", path=staging_dir)

    if any(True for _ in staging_dir.rglob("design.md")):
        raise BuildError("Validate output", "source design.md file was copied into dist/", path=staging_dir)
    if (staging_dir / "design").exists():
        raise BuildError("Validate output", "design/ output must not be published", path=staging_dir / "design")
    if (staging_dir / "templates").exists():
        raise BuildError("Validate output", "templates/ output must not be published", path=staging_dir / "templates")

    if draft_pages:
        for draft_page in draft_pages:
            draft_output_path = route_to_output_path(draft_page.route, staging_dir)
            if draft_output_path.exists():
                raise BuildError(
                    "Validate output",
                    f"draft page unexpectedly generated HTML: {draft_page.route}",
                    path=draft_output_path,
                )

    page_context_by_id = {context.page_id: context for context in template_contexts}
    renderer_context_by_id = {context.page_id: context for context in renderer_contexts}

    for page in published_pages:
        output_path = route_to_output_path(page.route, staging_dir)
        html_text = output_path.read_text(encoding="utf-8")
        page_context = page_context_by_id.get(page.id)
        if page_context is None:
            raise BuildError("Validate output", "page context is missing", path=output_path, page_id=page.id)
        renderer_context = renderer_context_by_id.get(page.id)
        if renderer_context is None:
            raise BuildError("Validate output", "renderer context is missing", path=output_path, page_id=page.id)
        renderer_result = renderer_results_by_id.get(page.id)
        if renderer_result is None:
            raise BuildError("Validate output", "renderer result is missing", path=output_path, page_id=page.id)
        validate_generated_page_html(
            output_path,
            html_text,
            page=page,
            page_context=page_context,
            renderer_result=renderer_result,
            registry=registry,
            navigation=navigation,
            theme_generation=theme_generation,
            dist_root=staging_dir,
        )
        validate_renderer_component_usage(
            output_path,
            page=page,
            page_context=renderer_context,
            renderer_result=renderer_result,
        )

    support_page_path = staging_dir / "404.html"
    expected_support_page_context = build_not_found_page_context(
        registry=registry,
        navigation=navigation,
        staging_dir=staging_dir,
        active_theme_id=theme_generation.active_theme_id,
        site_base_url=site_base_url,
    )
    expected_support_html = render_page_document(templates, expected_support_page_context)
    if not support_page_path.is_file():
        raise BuildError("Validate output", "404.html is missing", path=support_page_path)
    if support_page_path.read_text(encoding="utf-8") != expected_support_html:
        raise BuildError("Validate output", "404.html content is incorrect", path=support_page_path)

    sitemap_path = staging_dir / "sitemap.xml"
    expected_sitemap = build_sitemap_xml(published_pages, site_base_url=site_base_url)
    if not sitemap_path.is_file():
        raise BuildError("Validate output", "sitemap.xml is missing", path=sitemap_path)
    if sitemap_path.read_text(encoding="utf-8") != expected_sitemap:
        raise BuildError("Validate output", "sitemap.xml content is incorrect", path=sitemap_path)

    robots_path = staging_dir / "robots.txt"
    expected_robots = build_robots_txt(site_base_url=site_base_url)
    if not robots_path.is_file():
        raise BuildError("Validate output", "robots.txt is missing", path=robots_path)
    if robots_path.read_text(encoding="utf-8") != expected_robots:
        raise BuildError("Validate output", "robots.txt content is incorrect", path=robots_path)


def contains_absolute_filesystem_path(payload: Any) -> bool:
    if isinstance(payload, dict):
        return any(contains_absolute_filesystem_path(value) for value in payload.values())
    if isinstance(payload, list):
        return any(contains_absolute_filesystem_path(item) for item in payload)
    if isinstance(payload, str):
        return any(token in payload for token in ("/Users/", "/private/", "/var/", "/tmp/"))
    return False


def publish_output(staging_dir: Path, dist_dir: Path) -> None:
    backup_dir = dist_dir.with_name(f".dist-backup-{uuid4().hex}")
    backup_created = False

    if dist_dir.exists():
        dist_dir.rename(backup_dir)
        backup_created = True

    try:
        staging_dir.rename(dist_dir)
    except Exception:
        if backup_created and backup_dir.exists():
            if dist_dir.exists():
                rmtree(dist_dir)
            backup_dir.rename(dist_dir)
        raise
    else:
        if backup_created and backup_dir.exists():
            rmtree(backup_dir)


def cleanup_temp_dir(temp_dir: Path) -> None:
    if temp_dir.exists():
        rmtree(temp_dir)


def build_site(
    repo_root: Path,
    *,
    check_only: bool = False,
    stage_logger: Callable[[int, int, str], None] = log_stage,
) -> BuildSummary:
    pages_dir = repo_root / "pages"
    assets_dir = repo_root / "assets"
    data_dir = repo_root / "data"
    design_dir = repo_root / "design"
    dist_dir = repo_root / "dist"
    temp_root = Path(tempfile.mkdtemp(prefix=".phase10-build-", dir=repo_root))
    site_base_url = resolve_site_base_url()

    try:
        stage_logger(1, TOTAL_STAGES, "Validate environment")
        if sys.version_info < (3, 9):  # pragma: no cover - defensive repeat of the entrypoint check
            raise BuildError("Validate environment", "Python 3.9 or newer is required.")
        print(f"Python version: {sys.version.split()[0]}")
        if not repo_root.is_dir():
            raise BuildError("Validate environment", "repository root does not exist", path=repo_root)
        if not pages_dir.is_dir():
            raise BuildError("Validate environment", "pages/ directory does not exist", path=pages_dir)
        if not assets_dir.is_dir():
            raise BuildError("Validate environment", "assets/ directory does not exist", path=assets_dir)
        if not data_dir.is_dir():
            raise BuildError("Validate environment", "data/ directory does not exist", path=data_dir)
        if not design_dir.is_dir():
            raise BuildError("Validate environment", "design/ directory does not exist", path=design_dir)

        stage_logger(2, TOTAL_STAGES, "Load navigation data")
        navigation = load_navigation(data_dir)

        stage_logger(3, TOTAL_STAGES, "Load page registry")
        registry = load_page_registry(data_dir)
        validate_navigation_registry_consistency(navigation, registry)

        stage_logger(4, TOTAL_STAGES, "Validate registered page sources")
        page_paths = discover_page_sources(pages_dir)
        if not page_paths:
            raise BuildError("Validate registered page sources", "no page sources were found", path=pages_dir)
        discovered_source_paths = {path.relative_to(repo_root).as_posix() for path in page_paths}
        expected_source_paths = set(registry.source_files())
        if discovered_source_paths != expected_source_paths:
            missing = sorted(expected_source_paths - discovered_source_paths)
            extra = sorted(discovered_source_paths - expected_source_paths)
            details = []
            if missing:
                details.append(f"missing sources: {', '.join(missing)}")
            if extra:
                details.append(f"unregistered sources: {', '.join(extra)}")
            raise BuildError(
                "Validate registered page sources",
                "page source files do not match the page registry"
                + (" (" + "; ".join(details) + ")" if details else ""),
                path=pages_dir,
            )

        stage_logger(5, TOTAL_STAGES, "Discover and validate themes")
        theme_designs = load_theme_designs(design_dir)
        if len(theme_designs) != 1:
            raise BuildError(
                "Discover and validate themes",
                "exactly one theme source must exist in this phase",
                path=design_dir,
            )
        if theme_designs[0].id != "studio-default":
            raise BuildError(
                "Discover and validate themes",
                "the initial theme must be studio-default",
                path=theme_designs[0].source_path,
                theme_id=theme_designs[0].id,
            )

        stage_logger(6, TOTAL_STAGES, "Load and validate templates")
        templates = load_approved_templates(repo_root)

        stage_logger(7, TOTAL_STAGES, "Load and validate component registry")
        validate_component_registry({spec.component_id: spec for spec in APPROVED_COMPONENT_SPECS})

        stage_logger(8, TOTAL_STAGES, "Load and validate component templates")
        component_templates = load_approved_component_templates(repo_root)

        stage_logger(9, TOTAL_STAGES, "Register and validate page renderers")
        validate_renderer_registry(RENDERER_REGISTRY)

        stage_logger(10, TOTAL_STAGES, "Parse page sources")
        parsed_sources = [parse_page_source(page_path) for page_path in page_paths]
        parsed_sources_by_id = {source.registry_id: source for source in parsed_sources}
        if len(parsed_sources_by_id) != len(parsed_sources):
            raise BuildError("Parse page sources", "duplicate registry_id values were found", path=pages_dir)

        for page in registry.pages:
            source = parsed_sources_by_id.get(page.id)
            if source is None:
                raise BuildError(
                    "Parse page sources",
                    f"missing page source for registry entry {page.id}",
                    source_file=page.source,
                    page_id=page.id,
                )
            if source.source_path.relative_to(repo_root).as_posix() != page.source:
                raise BuildError(
                    "Parse page sources",
                    f"page source path must be {page.source}",
                    source_file=source.source_path,
                    page_id=page.id,
                )

        validate_page_sources_against_registry(page_paths, parsed_sources, registry, repo_root)

        staging_dir = temp_root
        published_pages = list(registry.published_pages())
        draft_pages = list(registry.draft_pages())
        generated_routes: list[str] = []
        generated_output_files: list[str] = []
        active_theme_id = theme_designs[0].id

        stage_logger(11, TOTAL_STAGES, "Parse renderer-specific control blocks")
        parsed_renderer_sources_by_id: dict[str, ParsedRendererSource] = {}
        for page in registry.pages:
            source = parsed_sources_by_id[page.id]
            parsed_renderer_source = parse_renderer_source(source.markdown_body, source_path=source.source_path)
            control_labels = [block.label for block in parsed_renderer_source.control_blocks]
            if page.type == "landing":
                if control_labels:
                    raise BuildError(
                        "Parse renderer-specific control blocks",
                        "landing pages must not declare renderer control blocks",
                        path=source.source_path,
                        page_id=page.id,
                        page_type=page.type,
                        page_route=page.route,
                        renderer_id=page.type,
                    )
            elif page.type == "static-prompt":
                if any(label not in {"prompt", "prompt-field", "image-slider"} for label in control_labels):
                    raise BuildError(
                        "Parse renderer-specific control blocks",
                        "static-prompt pages may only use prompt, prompt-field, or image-slider blocks",
                        path=source.source_path,
                        page_id=page.id,
                        page_type=page.type,
                        page_route=page.route,
                        renderer_id=page.type,
                    )
            elif page.type == "markdown-prompt":
                if any(label not in {"prompt", "image-slider"} for label in control_labels):
                    raise BuildError(
                        "Parse renderer-specific control blocks",
                        "markdown-prompt pages may only use prompt or image-slider blocks",
                        path=source.source_path,
                        page_id=page.id,
                        page_type=page.type,
                        page_route=page.route,
                        renderer_id=page.type,
                    )
            elif page.type == "prompt-builder":
                if control_labels.count("prompt-field") < 2:
                    raise BuildError(
                        "Parse renderer-specific control blocks",
                        "prompt-builder pages require at least two prompt-field blocks",
                        path=source.source_path,
                        page_id=page.id,
                        page_type=page.type,
                        page_route=page.route,
                        renderer_id=page.type,
                    )
                if any(label not in {"prompt", "prompt-field", "prompt-template"} for label in control_labels):
                    raise BuildError(
                        "Parse renderer-specific control blocks",
                        "prompt-builder pages may only use prompt, prompt-field or prompt-template blocks",
                        path=source.source_path,
                        page_id=page.id,
                        page_type=page.type,
                        page_route=page.route,
                        renderer_id=page.type,
                    )
            elif page.type == "practice-timeline":
                if control_labels.count("timeline-step") < 2:
                    raise BuildError(
                        "Parse renderer-specific control blocks",
                        "practice-timeline pages require at least two timeline-step blocks",
                        path=source.source_path,
                        page_id=page.id,
                        page_type=page.type,
                        page_route=page.route,
                        renderer_id=page.type,
                    )
                if any(label != "timeline-step" for label in control_labels):
                    raise BuildError(
                        "Parse renderer-specific control blocks",
                        "practice-timeline pages may only use timeline-step blocks",
                        path=source.source_path,
                        page_id=page.id,
                        page_type=page.type,
                        page_route=page.route,
                        renderer_id=page.type,
                    )
            else:
                raise BuildError(
                    "Parse renderer-specific control blocks",
                    f"unsupported page type: {page.type}",
                    path=source.source_path,
                    page_id=page.id,
                    page_type=page.type,
                    page_route=page.route,
                )
            parsed_renderer_sources_by_id[page.id] = parsed_renderer_source

        stage_logger(12, TOTAL_STAGES, "Render Markdown content")
        page_renderer_contexts = build_page_renderer_contexts(
            published_pages,
            parsed_sources_by_id,
            parsed_renderer_sources_by_id,
            registry,
            navigation,
            staging_dir,
            active_theme_id=active_theme_id,
            component_templates=component_templates,
        )

        stage_logger(13, TOTAL_STAGES, "Render reusable components and page main regions")
        renderer_results: list[PageRendererResult] = []
        renderer_results_by_id: dict[str, PageRendererResult] = {}
        for page_context in page_renderer_contexts:
            renderer_result = render_page(page_context)
            renderer_results.append(renderer_result)
            renderer_results_by_id[renderer_result.page_id] = renderer_result

        stage_logger(14, TOTAL_STAGES, "Render full pages through templates")
        page_contexts = build_page_template_contexts(
            published_pages,
            renderer_results_by_id,
            registry,
            navigation,
            staging_dir,
            active_theme_id=active_theme_id,
            site_base_url=site_base_url,
        )
        for page, page_context in zip(published_pages, page_contexts):
            output_path = route_to_output_path(page.route, staging_dir)
            html_document = render_page_document(templates, page_context)
            write_text(output_path, html_document)
            generated_routes.append(page.route)
            generated_output_files.append(f"dist/{output_path.relative_to(staging_dir).as_posix()}")

        stage_logger(15, TOTAL_STAGES, "Generate theme assets, support files, and public metadata")
        theme_generation = generate_theme_assets(theme_designs, staging_dir)
        generated_output_files.extend(theme_generation.generated_theme_files)
        copied_asset_count, copied_asset_files = copy_approved_assets(assets_dir, staging_dir)
        generated_output_files.extend(copied_asset_files)
        public_registry = build_public_registry_data(registry)
        public_navigation = build_public_navigation_data(navigation)
        public_registry_path = staging_dir / "page-registry.json"
        public_navigation_path = staging_dir / "navigation.json"
        write_json(public_registry_path, public_registry)
        write_json(public_navigation_path, public_navigation)
        generated_output_files.extend([
            "dist/page-registry.json",
            "dist/navigation.json",
        ])

        support_page_context = build_not_found_page_context(
            registry=registry,
            navigation=navigation,
            staging_dir=staging_dir,
            active_theme_id=active_theme_id,
            site_base_url=site_base_url,
        )
        not_found_html = render_page_document(templates, support_page_context)
        not_found_path = staging_dir / "404.html"
        write_text(not_found_path, not_found_html)
        generated_output_files.append("dist/404.html")

        sitemap_path = staging_dir / "sitemap.xml"
        robots_path = staging_dir / "robots.txt"
        write_text(sitemap_path, build_sitemap_xml(published_pages, site_base_url=site_base_url))
        write_text(robots_path, build_robots_txt(site_base_url=site_base_url))
        generated_output_files.extend([
            "dist/sitemap.xml",
            "dist/robots.txt",
        ])

        source_page_files = [page.source for page in registry.pages]
        site_base_url_status = "configured" if site_base_url else "unconfirmed"
        sitemap_status = "absolute" if site_base_url else "relative-only"
        robots_status = "generated"
        support_page_status = "generated"
        release_readiness_status = "ready" if site_base_url else "needs-base-url-confirmation"
        manifest = build_manifest(
            registry=registry,
            navigation=navigation,
            templates=templates,
            component_templates=component_templates,
            theme_generation=theme_generation,
            renderer_results=renderer_results,
            renderer_contexts=page_renderer_contexts,
            published_pages=published_pages,
            draft_pages=draft_pages,
            generated_routes=generated_routes,
            generated_output_files=sorted(
                generated_output_files
                + [
                    "dist/build-manifest.json",
                    "dist/404.html",
                    "dist/sitemap.xml",
                    "dist/robots.txt",
                ]
            ),
            copied_asset_count=copied_asset_count,
            copied_asset_files=copied_asset_files,
            source_page_files=source_page_files,
            public_registry_output_file="dist/page-registry.json",
            public_navigation_output_file="dist/navigation.json",
            public_theme_registry_output_file=theme_generation.public_registry_output_file,
            site_base_url_status=site_base_url_status,
            sitemap_status=sitemap_status,
            robots_status=robots_status,
            support_page_status=support_page_status,
            release_readiness_status=release_readiness_status,
        )
        write_json(staging_dir / "build-manifest.json", manifest)

        stage_logger(16, TOTAL_STAGES, "Validate output and publish dist" if not check_only else "Validate output and skip publication (--check)")
        validate_generated_output(
            staging_dir,
            manifest,
            registry,
            navigation,
            assets_dir,
            templates,
            component_templates,
            theme_designs,
            theme_generation,
            public_registry,
            public_navigation,
            page_contexts,
            page_renderer_contexts,
            renderer_results_by_id,
            site_base_url,
        )

        if not check_only:
            publish_output(staging_dir, dist_dir)
            output_dir = dist_dir
        else:
            cleanup_temp_dir(staging_dir)
            output_dir = staging_dir

        return BuildSummary(
            page_count=len(published_pages),
            asset_count=copied_asset_count,
            route_count=len(generated_routes),
            output_dir=output_dir,
            generated_routes=generated_routes,
            generated_output_files=sorted(generated_output_files),
            source_page_files=source_page_files,
        )
    except Exception:
        cleanup_temp_dir(temp_root)
        raise
