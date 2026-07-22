"""Page registry contract helpers for AI Learning Studio."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from core.errors import BuildError
from core.navigation import EXPECTED_SECTIONS


EXPECTED_VERSION = 1
LANDING_PAGE_TYPE = "landing"
PUBLIC_PAGE_TYPES = {"static-prompt", "prompt-builder", "practice-timeline"}
ALLOWED_PAGE_TYPES = PUBLIC_PAGE_TYPES | {LANDING_PAGE_TYPE}
ALLOWED_STATUS = {"published", "draft"}
EXPECTED_PAGES = (
    {
        "id": "home",
        "title": "AI Learning Studio",
        "description": "AI Learning Studio 페이지 레지스트리 검증용 랜딩 페이지",
        "route": "/",
        "source": "pages/index.md",
        "type": LANDING_PAGE_TYPE,
        "section": None,
        "order": 0,
        "navigation": False,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ai-practice",
        "title": "AI 체험 실습",
        "description": "AI 체험 실습 섹션 검증 페이지",
        "route": "/ai-practice/",
        "source": "pages/sections/ai-practice.md",
        "type": "static-prompt",
        "section": "ai-practice",
        "order": 1,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ready-to-use",
        "title": "바로 사용하기",
        "description": "바로 사용하기 섹션 검증 페이지",
        "route": "/ready-to-use/",
        "source": "pages/sections/ready-to-use.md",
        "type": "static-prompt",
        "section": "ready-to-use",
        "order": 2,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ai-assistant",
        "title": "AI 도우미",
        "description": "AI 도우미 섹션 검증 페이지",
        "route": "/ai-assistant/",
        "source": "pages/sections/ai-assistant.md",
        "type": "static-prompt",
        "section": "ai-assistant",
        "order": 3,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "image-ai",
        "title": "이미지 AI",
        "description": "이미지 AI 섹션 검증 페이지",
        "route": "/image-ai/",
        "source": "pages/sections/image-ai.md",
        "type": "static-prompt",
        "section": "image-ai",
        "order": 4,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
)
EXPECTED_PAGE_IDS = tuple(page["id"] for page in EXPECTED_PAGES)
EXPECTED_SOURCE_FILES = tuple(page["source"] for page in EXPECTED_PAGES)
EXPECTED_ROUTE_MAP = {page["id"]: page["route"] for page in EXPECTED_PAGES}


@dataclass(slots=True, frozen=True)
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


@dataclass(slots=True)
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


def load_page_registry(data_dir: Path) -> PageRegistry:
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
    if len(pages) != len(EXPECTED_PAGES):
        raise BuildError(
            "Load page registry",
            f"page registry must define exactly {len(EXPECTED_PAGES)} pages",
            path=registry_path,
            data_file=registry_path,
            field="pages",
        )

    parsed_pages: list[PageRegistryEntry] = []
    seen_ids: set[str] = set()
    seen_sources: set[str] = set()
    seen_routes: set[str] = set()
    expected_by_id = {page["id"]: page for page in EXPECTED_PAGES}

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

        page_id = page_data["id"]
        if page_id not in expected_by_id:
            raise BuildError(
                "Load page registry",
                f"unexpected page id: {page_id}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
            )
        expected = expected_by_id[page_id]

        if page_id in seen_ids:
            raise BuildError(
                "Load page registry",
                f"duplicate page id: {page_id}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
            )
        seen_ids.add(page_id)

        if page_data["title"] != expected["title"]:
            raise BuildError(
                "Load page registry",
                f"page title must be {expected['title']}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="title",
            )
        if page_data["description"] != expected["description"]:
            raise BuildError(
                "Load page registry",
                f"page description must be {expected['description']}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="description",
            )
        if page_data["route"] != expected["route"]:
            raise BuildError(
                "Load page registry",
                f"page route must be {expected['route']}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="route",
            )
        if page_data["source"] != expected["source"]:
            raise BuildError(
                "Load page registry",
                f"page source must be {expected['source']}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="source",
            )
        if page_data["type"] != expected["type"]:
            raise BuildError(
                "Load page registry",
                f"page type must be {expected['type']}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="type",
            )
        if page_data["section"] != expected["section"]:
            raise BuildError(
                "Load page registry",
                f"page section must be {expected['section']}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="section",
            )
        if page_data["order"] != expected["order"]:
            raise BuildError(
                "Load page registry",
                f"page order must be {expected['order']}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="order",
            )
        if page_data["navigation"] != expected["navigation"]:
            raise BuildError(
                "Load page registry",
                f"page navigation must be {expected['navigation']}",
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
        if page_data["status"] != expected["status"]:
            raise BuildError(
                "Load page registry",
                f"page status must be {expected['status']}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="status",
            )
        if page_data["lang"] != expected["lang"]:
            raise BuildError(
                "Load page registry",
                f"page lang must be {expected['lang']}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="lang",
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

        source_path = Path(page_data["source"])
        if source_path.is_absolute() or any(part == ".." for part in source_path.parts):
            raise BuildError(
                "Load page registry",
                "page source must be a repository-relative path",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="source",
            )

        if page_data["route"] in seen_routes:
            raise BuildError(
                "Load page registry",
                f"duplicate route: {page_data['route']}",
                path=registry_path,
                data_file=registry_path,
                page_id=page_id,
                field="route",
            )
        seen_routes.add(page_data["route"])

        if page_id != "home":
            if page_data["section"] not in {section["id"] for section in EXPECTED_SECTIONS}:
                raise BuildError(
                    "Load page registry",
                    f"page section must be one of: {', '.join(section['id'] for section in EXPECTED_SECTIONS)}",
                    path=registry_path,
                    data_file=registry_path,
                    page_id=page_id,
                    field="section",
                )

        parsed_pages.append(
            PageRegistryEntry(
                id=page_data["id"],
                title=page_data["title"],
                description=page_data["description"],
                route=page_data["route"],
                source=page_data["source"],
                type=page_data["type"],
                section=page_data["section"],
                order=page_data["order"],
                navigation=page_data["navigation"],
                status=page_data["status"],
                lang=page_data["lang"],
            )
        )

    parsed_pages.sort(key=lambda page: page.order)
    if tuple(page.id for page in parsed_pages) != EXPECTED_PAGE_IDS:
        raise BuildError(
            "Load page registry",
            "page order does not match the required registry contract",
            path=registry_path,
            data_file=registry_path,
        )
    if tuple(page.source for page in parsed_pages) != EXPECTED_SOURCE_FILES:
        raise BuildError(
            "Load page registry",
            "page source order does not match the required registry contract",
            path=registry_path,
            data_file=registry_path,
        )

    return PageRegistry(version=EXPECTED_VERSION, pages=tuple(parsed_pages))
