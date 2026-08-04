"""Page registry contract helpers for AI Learning Studio."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from core.errors import BuildError
from core.navigation import EXPECTED_SECTIONS


EXPECTED_VERSION = 1
LANDING_PAGE_TYPE = "landing"
PUBLIC_PAGE_TYPES = {"static-prompt", "prompt-builder", "practice-timeline", "markdown-prompt"}
ALLOWED_PAGE_TYPES = PUBLIC_PAGE_TYPES | {LANDING_PAGE_TYPE}
ALLOWED_STATUS = {"published", "draft"}
EXPECTED_PAGES = (
    {
        "id": "home",
        "title": "AI Learning Studio",
        "description": "AI 입문자와 기초 활용자가 프롬프트 복사, 요청 정리, 이미지 AI 실습을 차근차근 배우는 한국어 학습 사이트",
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
        "title": "프롬프트 단계별 체험하기",
        "description": "같은 주제에 여러 프롬프트 방식을 적용하고 결과 차이 비교하기",
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
        "id": "ai-practice-summer-vacation-basic",
        "title": "여름휴가 계획 세우기 (프롬프트 기초편)",
        "description": "여름휴가 계획이라는 같은 주제를 여러 프롬프트 방식으로 바꾸며 최종 프롬프트를 완성합니다.",
        "route": "/ai-practice/summer-vacation-basic/",
        "source": "pages/sections/ai-practice/summer-vacation-basic.md",
        "type": "static-prompt",
        "section": "ai-practice",
        "order": 2,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ai-practice-uijeongbu-oneday-tour",
        "title": "의정부 숨은 명소 찾기",
        "description": "의정부 숨은 명소 1일 코스라는 같은 주제를 여러 프롬프트 방식으로 바꾸며 최종 프롬프트를 완성합니다.",
        "route": "/ai-practice/uijeongbu-oneday-tour/",
        "source": "pages/sections/ai-practice/uijeongbu-oneday-tour.md",
        "type": "static-prompt",
        "section": "ai-practice",
        "order": 3,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ready-to-use",
        "title": "바로 써보기",
        "description": "필요한 조건만 선택해 프롬프트를 만들고 바로 사용하기",
        "route": "/ready-to-use/",
        "source": "pages/sections/ready-to-use.md",
        "type": "static-prompt",
        "section": "ready-to-use",
        "order": 4,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },

    {
        "id": "ready-to-use-korean-editor",
        "title": "맞춤형 한국어 교정",
        "description": "원하는 용도와 말투를 선택해 빠르고 자연스럽게 글을 다듬어 보세요.",
        "route": "/ready-to-use/korean-editor/",
        "source": "pages/sections/ready-to-use/korean-editor.md",
        "type": "static-prompt",
        "section": "ready-to-use",
        "order": 5,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ready-to-use-self-development",
        "title": "자기 개발 학습 계획",
        "description": "목표와 현재 수준, 사용 가능한 시간에 맞춰 현실적인 학습 계획을 짜주는 프롬프트 예제",
        "route": "/ready-to-use/self-development/",
        "source": "pages/sections/ready-to-use/self-development.md",
        "type": "static-prompt",
        "section": "ready-to-use",
        "order": 6,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ready-to-use-universal-handoff",
        "title": "AI 작업 이어가기",
        "description": "긴 대화를 작업 인계서로 변환하여 어느 AI에서든 끊김 없이 이어서 작업할 수 있게 만드는 범용 프롬프트",
        "route": "/ready-to-use/universal-handoff/",
        "source": "pages/sections/ready-to-use/universal-handoff.md",
        "type": "static-prompt",
        "section": "ready-to-use",
        "order": 7,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ready-to-use-recipe-generator",
        "title": "뚝딱 완성! 맞춤 레시피 가이드",
        "description": "공식 영양 기준을 참고하여 조건에 맞는 레시피와 칼로리 정보를 생성하는 프롬프트",
        "route": "/ready-to-use/recipe-generator/",
        "source": "pages/sections/ready-to-use/recipe-generator.md",
        "type": "static-prompt",
        "section": "ready-to-use",
        "order": 8,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ai-assistant",
        "title": "나만의 AI 만들기",
        "description": "Project·Gem 등에 사용할 맞춤형 역할과 지침 만들기",
        "route": "/ai-assistant/",
        "source": "pages/sections/ai-assistant.md",
        "type": "static-prompt",
        "section": "ai-assistant",
        "order": 9,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ai-assistant-hallucination-minimizer",
        "title": "할루시네이션 최소화",
        "description": "사실을 지어내지 않게 하고, 불확실하면 확인이 필요하다고 말하게 하는 짧은 지침 프롬프트입니다.",
        "route": "/ai-assistant/hallucination-minimizer/",
        "source": "pages/sections/ai-assistant/hallucination-minimizer.md",
        "type": "static-prompt",
        "section": "ai-assistant",
        "order": 10,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ai-assistant-gemini-verifier",
        "title": "Gemini 지식 검증",
        "description": "Gemini GEMs 및 Projects 전용 지식 검증 전문가(Knowledge Verification Expert) 지침 프롬프트입니다.",
        "route": "/ai-assistant/gemini-verifier/",
        "source": "pages/sections/ai-assistant/gemini-verifier.md",
        "type": "static-prompt",
        "section": "ai-assistant",
        "order": 11,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ai-assistant-vacation-planner",
        "title": "맞춤형 여행 플래너",
        "description": "실습에 바로 활용하는 국내외 맞춤형 여행 플래너 GEM·Project 전용 지침 프롬프트입니다.",
        "route": "/ai-assistant/vacation-planner-guide/",
        "source": "pages/sections/ai-assistant/vacation-planner-guide.md",
        "type": "static-prompt",
        "section": "ai-assistant",
        "order": 12,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ai-assistant-gemini-canvas-map",
        "title": "Gemini 캔버스 대화형 여행 지도",
        "description": "Gemini Canvas를 활용해 웹 브라우저에서 바로 작동하는 단일 HTML Leaflet 대화형 여행 지도를 만드는 프롬프트입니다.",
        "route": "/ai-assistant/gemini-canvas-map/",
        "source": "pages/sections/ai-assistant/gemini-canvas-map.md",
        "type": "static-prompt",
        "section": "ai-assistant",
        "order": 13,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ai-assistant-korean-editor",
        "title": "자연스러운 한국어 다듬기 지침서",
        "description": "실습에 바로 활용하는 자연스러운 한국어 전문 편집자 GEM·Project 전용 지침 프롬프트입니다.",
        "route": "/ai-assistant/korean-editor-guide/",
        "source": "pages/sections/ai-assistant/korean-editor-guide.md",
        "type": "static-prompt",
        "section": "ai-assistant",
        "order": 14,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ai-assistant-language-tutor",
        "title": "외국어 회화 코치",
        "description": "번역을 최소화하고 흐름을 이어가며 맞춤형으로 회화를 훈련시키는 1:1 외국어 파트너 지침 프롬프트입니다.",
        "route": "/ai-assistant/language-tutor-guide/",
        "source": "pages/sections/ai-assistant/language-tutor-guide.md",
        "type": "prompt-builder",
        "section": "ai-assistant",
        "order": 15,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ai-assistant-self-development-coach",
        "title": "현실적인 자기계발 코치",
        "description": "목표를 실천 가능한 작은 단위로 나누고, 무리하지 않게 지속할 수 있도록 돕는 1:1 맞춤형 코치 시스템 프롬프트입니다.",
        "route": "/ai-assistant/self-development-coach/",
        "source": "pages/sections/ai-assistant/self-development-coach.md",
        "type": "static-prompt",
        "section": "ai-assistant",
        "order": 16,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ai-assistant-life-story-interviewer",
        "title": "편안하게 대화하며 쓰는 나의 이야기",
        "description": "글이나 음성으로 AI와 천천히 인터뷰하며, 삶의 한 장면을 나다운 글로 남기는 지침서입니다.",
        "route": "/ai-assistant/life-story-interviewer/",
        "source": "pages/sections/ai-assistant/life-story-interviewer.md",
        "type": "markdown-prompt",
        "section": "ai-assistant",
        "order": 17,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "image-ai",
        "title": "이미지 만들기",
        "description": "이미지 생성·편집에 사용할 프롬프트 만들기와 실습",
        "route": "/image-ai/",
        "source": "pages/sections/image-ai.md",
        "type": "static-prompt",
        "section": "image-ai",
        "order": 18,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },

    {
        "id": "image-ai-typography",
        "title": "손글씨 타이포그래피 만들기",
        "description": "원하는 문구를 입력해 마커로 그린 듯한 삐뚤빼뚤하고 귀여운 레터링 이미지를 만들어 보세요.",
        "route": "/image-ai/typography/",
        "source": "pages/sections/image-ai/typography.md",
        "type": "static-prompt",
        "section": "image-ai",
        "order": 19,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "image-ai-recipe-infographic",
        "title": "모던 레시피 인포그래픽 생성",
        "description": "원하는 음식 이름을 입력해 감각적이고 모던한 세로형 레시피 인포그래픽 이미지를 만들어 보세요.",
        "route": "/image-ai/recipe-infographic/",
        "source": "pages/sections/image-ai/recipe-infographic.md",
        "type": "prompt-builder",
        "section": "image-ai",
        "order": 20,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "image-ai-3d-career-character",
        "title": "나만의 3D 직업 캐릭터 만들기",
        "description": "내 사진과 직업을 바탕으로 다양한 모습의 3D 캐릭터 포스터 프롬프트를 만들어 보세요.",
        "route": "/image-ai/3d-career-character/",
        "source": "pages/sections/image-ai/3d-career-character.md",
        "type": "static-prompt",
        "section": "image-ai",
        "order": 21,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "image-ai-resume-profile",
        "title": "AI 이력서·프로필 사진 생성",
        "description": "내 사진을 기반으로 다양한 의상과 구도의 전문적인 프로필 사진을 제작해 보세요.",
        "route": "/image-ai/resume-profile/",
        "source": "pages/sections/image-ai/resume-profile.md",
        "type": "static-prompt",
        "section": "image-ai",
        "order": 22,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },

    {
        "id": "ready-to-use-uijeongbu-route-finder",
        "title": "의정부 편한 길 찾기",
        "description": "출발지와 목적지, 몸 상태와 짐의 정도를 입력하면 계단과 가파른 길을 피한 편한 이동 경로를 찾아줍니다.",
        "route": "/ready-to-use/uijeongbu-route-finder/",
        "source": "pages/sections/ready-to-use/uijeongbu-route-finder.md",
        "type": "static-prompt",
        "section": "ready-to-use",
        "order": 23,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ready-to-use-healing-chat",
        "title": "마음을 가볍게 정리하는 힐링 대화",
        "description": "복잡한 마음을 털어놓고 싶을 때, 원하는 방식(위로, 정리, 해결책)에 맞춰 AI와 편안하게 대화할 수 있는 프롬프트입니다.",
        "route": "/ready-to-use/healing-chat/",
        "source": "pages/sections/ready-to-use/healing-chat.md",
        "type": "static-prompt",
        "section": "ready-to-use",
        "order": 24,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ready-to-use-event-budget-calculator",
        "title": "상황에 맞는 경조사비 결정",
        "description": "경조사 종류와 관계, 참석 여부, 경제적 상황을 입력하면 최신 국내 조사와 공식 자료를 확인해 적절한 금액과 전달 방법을 추천합니다.",
        "route": "/ready-to-use/event-budget-calculator/",
        "source": "pages/sections/ready-to-use/event-budget-calculator.md",
        "type": "static-prompt",
        "section": "ready-to-use",
        "order": 25,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    },
    {
        "id": "ready-to-use-funeral-etiquette",
        "title": "사회초년생을 위한 장례식장 예절",
        "description": "장례식장에 처음 방문하는 사회초년생을 위해 복장부터 조문 순서, 예절, 피해야 할 행동까지 쉽고 정확하게 안내하는 프롬프트입니다.",
        "route": "/ready-to-use/funeral-etiquette/",
        "source": "pages/sections/ready-to-use/funeral-etiquette.md",
        "type": "markdown-prompt",
        "section": "ready-to-use",
        "order": 26,
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
