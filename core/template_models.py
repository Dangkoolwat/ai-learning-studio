"""Template data models and constants for AI Learning Studio."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


TEMPLATE_ENGINE_VERSION = 1
TEMPLATE_VALIDATION_STATUS = "validated"
SITE_NAME = "AI Learning Studio"


@dataclass(slots=True, frozen=True)
class TemplateSpec:
    """A single approved human-authored template file."""

    logical_name: str
    relative_path: Path
    placeholders: tuple[str, ...]


TEMPLATE_BASE_PATH = Path("templates/base.html")
TEMPLATE_HEAD_PATH = Path("templates/partials/head.html")
TEMPLATE_SITE_HEADER_PATH = Path("templates/partials/site-header.html")
TEMPLATE_NAVIGATION_PATH = Path("templates/partials/navigation.html")
TEMPLATE_FOOTER_PATH = Path("templates/partials/footer.html")

APPROVED_TEMPLATE_SPECS = (
    TemplateSpec(
        logical_name="base",
        relative_path=TEMPLATE_BASE_PATH,
        placeholders=(
            "head_html",
            "site_header_html",
            "navigation_html",
            "main_html",
            "footer_html",
            "html_lang",
            "theme_id",
            "page_id",
            "page_type",
            "page_section",
            "body_class",
        ),
    ),
    TemplateSpec(
        logical_name="head",
        relative_path=TEMPLATE_HEAD_PATH,
        placeholders=(
            "page_title",
            "page_description",
            "canonical_path",
            "theme_stylesheet_url",
            "page_id",
            "page_type",
        ),
    ),
    TemplateSpec(
        logical_name="site-header",
        relative_path=TEMPLATE_SITE_HEADER_PATH,
        placeholders=(
            "home_url",
            "site_name",
        ),
    ),
    TemplateSpec(
        logical_name="navigation",
        relative_path=TEMPLATE_NAVIGATION_PATH,
        placeholders=("navigation_items_html",),
    ),
    TemplateSpec(
        logical_name="footer",
        relative_path=TEMPLATE_FOOTER_PATH,
        placeholders=(
            "site_name",
            "current_year",
        ),
    ),
)

TEMPLATE_PARTIAL_NAMES = ("head", "site-header", "navigation", "footer")


@dataclass(slots=True, frozen=True)
class LoadedTemplates:
    """Validated template source text loaded from the repository."""

    base_html: str
    head_html: str
    site_header_html: str
    navigation_html: str
    footer_html: str
    source_files: tuple[str, ...]

    def file_count(self) -> int:
        return len(self.source_files)


@dataclass(slots=True, frozen=True)
class PageTemplateContext:
    """Build-time values used to render a full page shell."""

    page_id: str
    page_title: str
    page_description: str
    page_route: str
    page_type: str
    page_section: str
    page_lang: str
    body_class: str
    site_name: str
    current_year: int
    active_theme_id: str
    theme_stylesheet_url: str
    home_url: str
    navigation_items_html: str
    main_html: str
    html_lang: str
