"""Template rendering helpers for AI Learning Studio."""

from __future__ import annotations

from html import escape as escape_html
import os
from pathlib import Path
import re
from textwrap import indent

from core.errors import BuildError
from core.navigation import NavigationData
from core.page_registry import PageRegistry, PageRegistryEntry
from core.template_models import (
    APPROVED_TEMPLATE_SPECS,
    LoadedTemplates,
    PageTemplateContext,
    SITE_NAME,
    TEMPLATE_BASE_PATH,
    TEMPLATE_ENGINE_VERSION,
    TEMPLATE_PARTIAL_NAMES,
    TEMPLATE_VALIDATION_STATUS,
)
from core.template_validation import extract_placeholders, validate_template_source


RENDER_PLACEHOLDER_RE = re.compile(r"{{\s*[a-z0-9_]+\s*}}")


def load_approved_templates(repo_root: Path) -> LoadedTemplates:
    """Load and validate the approved template files."""

    repo_root = repo_root.resolve(strict=False)
    loaded_templates: dict[str, str] = {}
    source_files: list[str] = []
    seen_logical_names: set[str] = set()

    for spec in APPROVED_TEMPLATE_SPECS:
        if spec.logical_name in seen_logical_names:
            raise BuildError(
                "Load templates",
                f"duplicate logical template name: {spec.logical_name}",
                path=repo_root / spec.relative_path,
            )
        seen_logical_names.add(spec.logical_name)

        template_path = (repo_root / spec.relative_path).resolve(strict=False)
        if repo_root != template_path and repo_root not in template_path.parents:
            raise BuildError(
                "Load templates",
                "template path escapes the repository root",
                path=template_path,
            )
        if template_path.suffix != ".html":
            raise BuildError("Load templates", "template files must end in .html", path=template_path)
        if not template_path.is_file():
            raise BuildError("Load templates", "required template file is missing", path=template_path)

        try:
            template_text = template_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise BuildError("Load templates", "template file must be UTF-8 encoded", path=template_path) from exc
        except OSError as exc:
            raise BuildError("Load templates", "template file could not be read", path=template_path) from exc

        validate_template_source(template_path, template_text, spec=spec)
        loaded_templates[spec.logical_name] = template_text
        source_files.append(spec.relative_path.as_posix())

    return LoadedTemplates(
        base_html=loaded_templates["base"],
        head_html=loaded_templates["head"],
        site_header_html=loaded_templates["site-header"],
        navigation_html=loaded_templates["navigation"],
        footer_html=loaded_templates["footer"],
        source_files=tuple(source_files),
    )


def build_body_class(page_id: str, page_type: str, page_section: str | None) -> str:
    classes = ["page", f"page-type-{page_type}", f"page-id-{page_id}"]
    if page_section:
        classes.append(f"page-section-{page_section}")
    return " ".join(classes)


def route_href_for_output(current_output_path: Path, target_route: str, dist_root: Path) -> str:
    """Return a route-relative href between two generated routes."""

    current_directory = current_output_path.parent
    target_output_path = _route_to_output_path(target_route, dist_root)
    relative_path = os.path.relpath(target_output_path.parent, start=current_directory)
    href = Path(relative_path).as_posix()
    if href == ".":
        return "./"
    if not href.endswith("/"):
        href = f"{href}/"
    return href


def build_navigation_items_html(
    current_page: PageRegistryEntry,
    registry: PageRegistry,
    navigation: NavigationData,
    current_output_path: Path,
    dist_root: Path,
) -> str:
    """Build the navigation list items for the current page."""

    published_pages_by_section: dict[str, PageRegistryEntry] = {}
    for page in registry.published_pages():
        if not page.navigation:
            continue
        if page.section is None:
            raise BuildError(
                "Render pages through templates",
                "published navigation page is missing a section",
                page_id=page.id,
                field="section",
            )
        if page.route == "/":
            raise BuildError(
                "Render pages through templates",
                "root page cannot appear in the navigation",
                page_id=page.id,
                field="route",
            )
        if page.section in published_pages_by_section:
            raise BuildError(
                "Render pages through templates",
                f"duplicate navigation item for section: {page.section}",
                page_id=page.id,
                field="section",
            )
        published_pages_by_section[page.section] = page

    items: list[str] = []
    current_route = _normalize_route(current_page.route)
    for section in navigation.sections:
        page = published_pages_by_section.get(section.id)
        if page is None:
            raise BuildError(
                "Render pages through templates",
                f"missing published page for navigation section: {section.id}",
                page_id=current_page.id,
                field="section",
            )

        href = route_href_for_output(current_output_path, page.route, dist_root)
        is_current = current_page.id == page.id or current_route == _normalize_route(page.route)
        list_item_class = "navigation-item is-current" if is_current else "navigation-item"
        aria_current = ' aria-current="page"' if is_current else ""
        items.append(
            "  <li class=\"{list_item_class}\">\n"
            "    <a class=\"navigation-link\" href=\"{href}\"{aria_current}>\n"
            "      <span class=\"nav-label\">{label}</span>\n"
            "      <span class=\"nav-description\">{description}</span>\n"
            "    </a>\n"
            "  </li>".format(
                list_item_class=list_item_class,
                href=escape_html(href),
                aria_current=aria_current,
                label=escape_html(section.label),
                description=escape_html(section.description),
            )
        )

    return "\n".join(items)


def render_page_document(templates: LoadedTemplates, context: PageTemplateContext) -> str:
    """Render a complete page document through the approved templates."""

    head_html = render_template(
        templates.head_html,
        template_name="head",
        replacements={
            "site_name": escape_html(context.site_name),
            "page_title": escape_html(context.page_title),
            "page_description": escape_html(context.page_description),
            "robots_content": escape_html(context.robots_content),
            "theme_color": escape_html(context.theme_color),
            "canonical_path": escape_html(context.page_route),
            "canonical_link_html": context.canonical_link_html,
            "favicon_url": escape_html(context.favicon_url),
            "theme_stylesheet_url": escape_html(context.theme_stylesheet_url),
            "site_stylesheet_url": escape_html(context.site_stylesheet_url),
            "site_script_url": escape_html(context.site_script_url),
            "page_id": escape_html(context.page_id),
            "page_type": escape_html(context.page_type),
        },
    )
    site_header_html = render_template(
        templates.site_header_html,
        template_name="site-header",
        replacements={
            "home_url": escape_html(context.home_url),
            "site_name": escape_html(context.site_name),
        },
    )
    navigation_html = render_template(
        templates.navigation_html,
        template_name="navigation",
        replacements={"navigation_items_html": context.navigation_items_html},
    )
    footer_html = render_template(
        templates.footer_html,
        template_name="footer",
        replacements={
            "site_name": escape_html(context.site_name),
            "current_year": escape_html(str(context.current_year)),
        },
    )

    return render_template(
        templates.base_html,
        template_name="base",
        replacements={
            "head_html": head_html,
            "site_header_html": site_header_html,
            "navigation_html": navigation_html,
            "main_html": context.main_html,
            "footer_html": footer_html,
            "html_lang": escape_html(context.html_lang),
            "theme_id": escape_html(context.active_theme_id),
            "page_id": escape_html(context.page_id),
            "page_type": escape_html(context.page_type),
            "page_section": escape_html(context.page_section),
            "body_class": escape_html(context.body_class),
        },
    )


def build_main_html(rendered_markdown_html: str) -> str:
    article_html = indent(rendered_markdown_html, "    ")
    return (
        '<main class="site-main" id="main-content">\n'
        '  <article class="page-content">\n'
        f"{article_html}\n"
        "  </article>\n"
        "</main>"
    )


def render_template(
    template_text: str,
    *,
    template_name: str,
    replacements: dict[str, str],
) -> str:
    """Replace approved placeholders in a validated template."""

    expected_placeholders = tuple(spec.placeholders for spec in APPROVED_TEMPLATE_SPECS if spec.logical_name == template_name)
    if not expected_placeholders:
        raise BuildError("Render template", f"unknown template name: {template_name}")
    return render_placeholder_template(
        template_text,
        template_name=template_name,
        approved_placeholders=expected_placeholders[0],
        replacements=replacements,
    )


def render_placeholder_template(
    template_text: str,
    *,
    template_name: str,
    approved_placeholders: tuple[str, ...],
    replacements: dict[str, str],
) -> str:
    """Render a placeholder template with an approved placeholder set."""

    replacement_keys = set(replacements)
    approved_keys = set(approved_placeholders)
    if replacement_keys != approved_keys:
        missing = sorted(approved_keys - replacement_keys)
        extra = sorted(replacement_keys - approved_keys)
        details = []
        if missing:
            details.append(f"missing replacements: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected replacements: {', '.join(extra)}")
        raise BuildError(
            "Render template",
            f"{template_name} template replacements do not match the approved placeholder list"
            + (" (" + "; ".join(details) + ")" if details else ""),
        )

    rendered = template_text
    for placeholder_name in approved_placeholders:
        pattern = re.compile(r"{{\s*" + re.escape(placeholder_name) + r"\s*}}")
        rendered, count = pattern.subn(replacements[placeholder_name], rendered)
        if count == 0:
            raise BuildError(
                "Render template",
                f"placeholder was not rendered: {placeholder_name}",
                field=placeholder_name,
            )

    if RENDER_PLACEHOLDER_RE.search(rendered):
        raise BuildError("Render template", "unresolved template placeholder remains")

    return rendered


def _normalize_route(route: str) -> str:
    if route == "/":
        return "/"

    segments = [segment for segment in route.strip("/").split("/") if segment]
    if any(segment in {".", ".."} for segment in segments):
        raise BuildError("Render pages through templates", "route must not contain dot segments", field="route")
    return "/" + "/".join(segments) + "/"


def _route_to_output_path(route: str, dist_root: Path) -> Path:
    normalized_route = _normalize_route(route)
    if normalized_route == "/":
        output_path = dist_root / "index.html"
    else:
        segments = [segment for segment in normalized_route.strip("/").split("/") if segment]
        output_path = dist_root.joinpath(*segments, "index.html")

    resolved_dist = dist_root.resolve(strict=False)
    resolved_output = output_path.resolve(strict=False)
    if resolved_dist != resolved_output and resolved_dist not in resolved_output.parents:
        raise BuildError("Render pages through templates", "route escapes the dist directory")
    return output_path
