"""Page registry contract helpers for AI Learning Studio."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from core.errors import BuildError


EXPECTED_VERSION = 1
LANDING_PAGE_TYPE = "landing"
PUBLIC_PAGE_TYPES = {"static-prompt", "prompt-builder", "practice-timeline", "markdown-prompt"}
ALLOWED_PAGE_TYPES = PUBLIC_PAGE_TYPES | {LANDING_PAGE_TYPE}
ALLOWED_STATUS = {"published", "draft"}


@dataclass(frozen=True)
class PageRegistryEntry:
    """A validated page registry entry."""

    id: str
    title: str
    description: str
    route: str
    source: str
    type: str
    section: str | None
    order: int
    navigation: bool
    status: str
    lang: str

    def to_public_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "route": self.route,
            "source": self.source,
            "type": self.type,
            "section": self.section,
            "order": self.order,
            "navigation": self.navigation,
            "status": self.status,
            "lang": self.lang,
        }


@dataclass
class PageRegistry:
    """The validated authoritative page registry."""

    version: int
    pages: tuple[PageRegistryEntry, ...]

    def page_by_id(self, page_id: str) -> PageRegistryEntry:
        for page in self.pages:
            if page.id == page_id:
                return page
        raise KeyError(page_id)

    def published_pages(self) -> tuple[PageRegistryEntry, ...]:
        return tuple(page for page in self.pages if page.status == "published")

    def draft_pages(self) -> tuple[PageRegistryEntry, ...]:
        return tuple(page for page in self.pages if page.status == "draft")

    def to_public_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "pages": [page.to_public_dict() for page in self.published_pages()],
        }

    def source_files(self) -> tuple[str, ...]:
        return tuple(page.source for page in self.pages)


def _require_page_text(
    value: object,
    *,
    message: str,
    registry_path: Path,
    page_id: str,
    field: str,
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BuildError(
            "Load page registry",
            message,
            path=registry_path,
            data_file=registry_path,
            page_id=page_id,
            field=field,
        )
    return value


def derive_route_from_source(source: str) -> str:
    """Derive the canonical route for a registered Markdown source path.

    pages/index.md maps to /, and pages/sections/<name>.md or
    pages/sections/<section>/<name>.md map to /<name>/ and
    /<section>/<name>/ respectively.
    """
    stem = source[len("pages/") : -len(".md")]
    if stem == "index":
        return "/"
    if stem.startswith("sections/"):
        stem = stem[len("sections/") :]
    return f"/{stem}/"


def load_page_registry(data_dir: Path) -> PageRegistry:
    """Load and structurally validate data/page-registry.json.

    The registry JSON file is the single source of truth for page metadata.
    Validation covers structure, field types, uniqueness, route-source
    consistency; cross-file consistency with navigation data is enforced
    separately by core.data_consistency.
    """
    registry_path = data_dir / "page-registry.json"
    if not registry_path.is_file():
        raise BuildError(
            "Load page registry",
            "data/page-registry.json is missing",
            path=registry_path,
            data_file=registry_path,
        )

    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BuildError(
            "Load page registry",
            f"data/page-registry.json is not valid JSON: {exc.msg}",
            path=registry_path,
            data_file=registry_path,
        ) from exc

    if not isinstance(payload, dict):
        raise BuildError(
            "Load page registry",
            "page registry must be a JSON object",
            path=registry_path,
            data_file=registry_path,
        )

    version = payload.get("version")
    if version != EXPECTED_VERSION:
        raise BuildError(
            "Load page registry",
            f"page registry version must be {EXPECTED_VERSION}",
            path=registry_path,
            data_file=registry_path,
            field="version",
        )

    pages = payload.get("pages")
    if not isinstance(pages, list):
        raise BuildError(
            "Load page registry",
            "page registry pages must be a JSON array",
            path=registry_path,
            data_file=registry_path,
            field="pages",
        )
    if not pages:
        raise BuildError(
            "Load page registry",
            "page registry must define at least one page",
            path=registry_path,
            data_file=registry_path,
            field="pages",
        )

    parsed_pages: list[PageRegistryEntry] = []
    seen_ids: set[str] = set()
    seen_sources: set[str] = set()

    for page_data in pages:
        if not isinstance(page_data, dict):
            raise BuildError(
                "Load page registry",
                "each page registry entry must be a JSON object",
                path=registry_path,
                data_file=registry_path,
            )

        allowed_keys = {
            "id",
            "title",
            "description",
            "route",
            "source",
            "type",
            "section",
            "order",
            "navigation",
            "status",
            "lang",
        }
        unexpected_keys = set(page_data) - allowed_keys
        missing_keys = allowed_keys - set(page_data)
        if unexpected_keys or missing_keys:
            details = []
            if missing_keys:
                details.append(f"missing keys: {', '.join(sorted(missing_keys))}")
            if unexpected_keys:
                details.append(f"unexpected keys: {', '.join(sorted(unexpected_keys))}")
            raise BuildError(
                "Load page registry",
                "page registry entry fields do not match the expected contract"
                + (" (" + "; ".join(details) + ")" if details else ""),
                path=registry_path,
                data_file=registry_path,
            )

        page_id = _require_page_text(
            page_data["id"],
            message="page id must be a non-empty string",
            registry_path=registry_path,
            page_id=str(page_data.get("id")),
            field="id",
        )
        if page_id in seen_ids:
            raise BuildError(
                "Load page registry",
                f"duplicate page id: {page_id}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
            )
        seen_ids.add(page_id)

        _require_page_text(
            page_data["title"],
            message=f"page title must be a non-empty string for page: {page_id}",
            registry_path=registry_path,
            page_id=page_id,
            field="title",
        )
        _require_page_text(
            page_data["description"],
            message=f"page description must be a non-empty string for page: {page_id}",
            registry_path=registry_path,
            page_id=page_id,
            field="description",
        )

        route = page_data["route"]
        if (
            not isinstance(route, str)
            or not route.startswith("/")
            or not route.endswith("/")
            or len(route) < 1
        ):
            raise BuildError(
                "Load page registry",
                f"page route must be a directory path like /example/ for page: {page_id}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="route",
            )

        source = page_data["source"]
        source_path = Path(source) if isinstance(source, str) else None
        if (
            source_path is None
            or source_path.is_absolute()
            or any(part == ".." for part in source_path.parts)
            or not source.endswith(".md")
            or not source.startswith("pages/")
        ):
            raise BuildError(
                "Load page registry",
                f"page source must be a repository-relative pages/*.md path for page: {page_id}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="source",
            )

        if page_data["type"] not in ALLOWED_PAGE_TYPES:
            raise BuildError(
                "Load page registry",
                f"page type must be one of: {', '.join(sorted(ALLOWED_PAGE_TYPES))}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="type",
            )

        section = page_data["section"]
        if section is not None and (not isinstance(section, str) or not section.strip()):
            raise BuildError(
                "Load page registry",
                f"page section must be null or a non-empty string for page: {page_id}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="section",
            )

        order = page_data["order"]
        if not isinstance(order, int) or isinstance(order, bool) or order < 0:
            raise BuildError(
                "Load page registry",
                f"page order must be a non-negative integer for page: {page_id}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="order",
            )

        if not isinstance(page_data["navigation"], bool):
            raise BuildError(
                "Load page registry",
                f"page navigation must be a boolean for page: {page_id}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="navigation",
            )

        if page_data["status"] not in ALLOWED_STATUS:
            raise BuildError(
                "Load page registry",
                f"page status must be one of: {', '.join(sorted(ALLOWED_STATUS))}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="status",
            )

        _require_page_text(
            page_data["lang"],
            message=f"page lang must be a non-empty string for page: {page_id}",
            registry_path=registry_path,
            page_id=page_id,
            field="lang",
        )

        derived_route = derive_route_from_source(source)
        if route != derived_route:
            raise BuildError(
                "Load page registry",
                f"page route ({route}) does not match the route derived from its source path ({derived_route})",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="route",
            )

        if source in seen_sources:
            raise BuildError(
                "Load page registry",
                f"duplicate page source: {source}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="source",
            )
        seen_sources.add(source)

        parsed_pages.append(
            PageRegistryEntry(
                id=page_id,
                title=page_data["title"],
                description=page_data["description"],
                route=route,
                source=source,
                type=page_data["type"],
                section=section,
                order=order,
                navigation=page_data["navigation"],
                status=page_data["status"],
                lang=page_data["lang"],
            )
        )

    parsed_pages.sort(key=lambda page: page.order)

    return PageRegistry(version=EXPECTED_VERSION, pages=tuple(parsed_pages))
