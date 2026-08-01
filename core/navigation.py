"""Navigation contract helpers for AI Learning Studio."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from core.errors import BuildError


EXPECTED_VERSION = 1
EXPECTED_SECTIONS = (
    {
        "id": "ai-practice",
        "label": "프롬프트 단계별 체험하기",
        "description": "같은 주제에 여러 프롬프트 방식을 적용하고 결과 차이 비교하기",
        "order": 1,
        "items": [
            {
                "id": "ai-practice-summer-vacation-basic",
                "label": "여름휴가 계획 세우기 (기초편)",
                "description": "여름휴가 계획이라는 같은 주제를 여러 프롬프트 방식으로 바꾸며 최종 프롬프트 완성하기",
                "route": "/ai-practice/summer-vacation-basic/",
            },
        ],
    },
    {
        "id": "ready-to-use",
        "label": "바로 써보기",
        "description": "필요한 조건만 선택해 프롬프트를 만들고 바로 사용하기",
        "order": 2,
        "items": [

            {
                "id": "ready-to-use-korean-editor",
                "label": "맞춤형 한국어 교정 프롬프트",
                "description": "원하는 용도와 말투를 선택해 빠르고 자연스럽게 글 다듬기",
                "route": "/ready-to-use/korean-editor/",
            },
            {
                "id": "ready-to-use-self-development",
                "label": "자기 개발 학습 계획 프롬프트",
                "description": "목표와 현재 수준, 사용 가능한 시간에 맞춰 현실적인 학습 계획을 짜주는 프롬프트 예제",
                "route": "/ready-to-use/self-development/",
            },
            {
                "id": "ready-to-use-universal-handoff",
                "label": "AI 작업 이어가기",
                "description": "긴 대화를 작업 인계서로 변환하여 어느 AI에서든 이어서 작업할 수 있게 만드는 범용 프롬프트",
                "route": "/ready-to-use/universal-handoff/",
            },
        ],
    },
    {
        "id": "ai-assistant",
        "label": "나만의 AI 만들기",
        "description": "Project·Gem 등에 사용할 맞춤형 역할과 지침 만들기",
        "order": 3,
        "items": [
            {
                "id": "ai-assistant-hallucination-minimizer",
                "label": "할루시네이션 최소화 프롬프트",
                "description": "불확실한 부분을 숨기지 않게 하는 짧은 지침",
                "route": "/ai-assistant/hallucination-minimizer/",
            },
            {
                "id": "ai-assistant-gemini-verifier",
                "label": "Gemini 지식 검증 지침서",
                "description": "Gemini GEMs 및 Projects 전용 지식 검증 전문가 지침",
                "route": "/ai-assistant/gemini-verifier/",
            },
            {
                "id": "ai-assistant-vacation-planner",
                "label": "여름휴가 여행 플래너 지침서",
                "description": "실습용 국내 여름휴가 여행 플래너 GEM·Project 전용 지침서",
                "route": "/ai-assistant/vacation-planner-guide/",
            },
            {
                "id": "ai-assistant-gemini-canvas-map",
                "label": "Gemini 캔버스 대화형 여행 지도",
                "description": "Gemini Canvas를 활용한 단일 HTML Leaflet 대화형 여행 지도 생성 프롬프트",
                "route": "/ai-assistant/gemini-canvas-map/",
            },
            {
                "id": "ai-assistant-korean-editor",
                "label": "한국어 다듬기 전문 편집자",
                "description": "실습용 자연스러운 한국어 전문 편집자 GEM·Project 전용 지침서",
                "route": "/ai-assistant/korean-editor-guide/",
            },
            {
                "id": "ai-assistant-language-tutor",
                "label": "외국어 회화 코치 지침서",
                "description": "번역을 최소화하고 흐름을 이어가며 맞춤형으로 회화를 훈련시키는 파트너 지침서",
                "route": "/ai-assistant/language-tutor-guide/",
            },
            {
                "id": "ai-assistant-self-development-coach",
                "label": "현실적인 자기계발 코치 지침서",
                "description": "실천 가능한 작은 단위로 목표를 나누고 지속할 수 있도록 돕는 맞춤형 코치 지침서",
                "route": "/ai-assistant/self-development-coach/",
            },
        ],
    },
    {
        "id": "image-ai",
        "label": "이미지 만들기",
        "description": "이미지 생성·편집에 사용할 프롬프트 만들기와 실습",
        "order": 4,
        "items": [

            {
                "id": "image-ai-typography",
                "label": "손글씨 타이포그래피 만들기",
                "description": "원하는 문구를 입력해 마커로 그린 듯한 삐뚤빼뚤하고 귀여운 레터링 이미지를 만들어 보세요.",
                "route": "/image-ai/typography/",
            },
            {
                "id": "image-ai-recipe-infographic",
                "label": "모던 레시피 인포그래픽 생성",
                "description": "원하는 음식 이름을 입력해 감각적이고 모던한 세로형 레시피 인포그래픽 이미지를 만들어 보세요.",
                "route": "/image-ai/recipe-infographic/",
            },
            {
                "id": "image-ai-3d-career-character",
                "label": "나만의 3D 직업 캐릭터 만들기",
                "description": "내 사진과 직업을 바탕으로 다양한 모습의 3D 캐릭터 포스터 프롬프트를 만들어 보세요.",
                "route": "/image-ai/3d-career-character/",
            },
            {
                "id": "image-ai-resume-profile",
                "label": "AI 이력서·프로필 사진 생성",
                "description": "내 사진을 기반으로 다양한 의상과 구도의 전문적인 프로필 사진을 제작해 보세요.",
                "route": "/image-ai/resume-profile/",
            }
        ],
    },
)


@dataclass(slots=True, frozen=True)
class NavigationSubItem:
    """A sub-item entry under a main navigation section."""

    id: str
    label: str
    description: str
    route: str

    def to_public_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "route": self.route,
        }


@dataclass(slots=True, frozen=True)
class NavigationSection:
    """A confirmed top-level navigation section."""

    id: str
    label: str
    description: str
    order: int
    items: tuple[NavigationSubItem, ...] = ()

    def to_public_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "order": self.order,
            "items": [item.to_public_dict() for item in self.items],
        }


@dataclass(slots=True)
class NavigationData:
    """The validated navigation contract."""

    version: int
    sections: tuple[NavigationSection, ...]

    def to_public_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "sections": [section.to_public_dict() for section in self.sections],
        }


def load_navigation(data_dir: Path) -> NavigationData:
    navigation_path = data_dir / "navigation.json"
    if not navigation_path.is_file():
        raise BuildError(
            "Load navigation data",
            "data/navigation.json is missing",
            path=navigation_path,
            data_file=navigation_path,
        )

    try:
        payload = json.loads(navigation_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BuildError(
            "Load navigation data",
            f"data/navigation.json is not valid JSON: {exc.msg}",
            path=navigation_path,
            data_file=navigation_path,
        ) from exc

    if not isinstance(payload, dict):
        raise BuildError(
            "Load navigation data",
            "navigation data must be a JSON object",
            path=navigation_path,
            data_file=navigation_path,
        )

    version = payload.get("version")
    if version != EXPECTED_VERSION:
        raise BuildError(
            "Load navigation data",
            f"navigation version must be {EXPECTED_VERSION}",
            path=navigation_path,
            data_file=navigation_path,
            field="version",
        )

    sections = payload.get("sections")
    if not isinstance(sections, list):
        raise BuildError(
            "Load navigation data",
            "navigation sections must be a JSON array",
            path=navigation_path,
            data_file=navigation_path,
            field="sections",
        )
    if len(sections) != len(EXPECTED_SECTIONS):
        raise BuildError(
            "Load navigation data",
            f"navigation must define exactly {len(EXPECTED_SECTIONS)} sections",
            path=navigation_path,
            data_file=navigation_path,
            field="sections",
        )

    parsed_sections: list[NavigationSection] = []
    for expected, section_data in zip(EXPECTED_SECTIONS, sections, strict=True):
        if not isinstance(section_data, dict):
            raise BuildError(
                "Load navigation data",
                "each navigation section must be a JSON object",
                path=navigation_path,
                data_file=navigation_path,
            )

        allowed_keys = {"id", "label", "description", "order", "items"}
        unexpected_keys = set(section_data) - allowed_keys
        missing_keys = allowed_keys - set(section_data)
        if unexpected_keys or missing_keys:
            details = []
            if missing_keys:
                details.append(f"missing keys: {', '.join(sorted(missing_keys))}")
            if unexpected_keys:
                details.append(f"unexpected keys: {', '.join(sorted(unexpected_keys))}")
            raise BuildError(
                "Load navigation data",
                "navigation section fields do not match the expected contract"
                + (" (" + "; ".join(details) + ")" if details else ""),
                path=navigation_path,
                data_file=navigation_path,
            )

        if section_data["id"] != expected["id"]:
            raise BuildError(
                "Load navigation data",
                f"navigation section id must be {expected['id']}",
                path=navigation_path,
                data_file=navigation_path,
                field="id",
            )
        if section_data["label"] != expected["label"]:
            raise BuildError(
                "Load navigation data",
                f"navigation section label must be {expected['label']}",
                path=navigation_path,
                data_file=navigation_path,
                field="label",
            )
        if section_data["description"] != expected["description"]:
            raise BuildError(
                "Load navigation data",
                f"navigation section description must be {expected['description']}",
                path=navigation_path,
                data_file=navigation_path,
                field="description",
            )
        if section_data["order"] != expected["order"]:
            raise BuildError(
                "Load navigation data",
                f"navigation section order must be {expected['order']}",
                path=navigation_path,
                data_file=navigation_path,
                field="order",
            )

        raw_items = section_data.get("items", [])
        expected_items = expected.get("items", [])
        if not isinstance(raw_items, list):
            raise BuildError(
                "Load navigation data",
                f"navigation section items must be a list for section: {section_data['id']}",
                path=navigation_path,
                data_file=navigation_path,
                field="items",
            )
        if len(raw_items) != len(expected_items):
            raise BuildError(
                "Load navigation data",
                f"navigation items count mismatch for section: {section_data['id']}",
                path=navigation_path,
                data_file=navigation_path,
                field="items",
            )

        parsed_items: list[NavigationSubItem] = []
        for exp_item, item_data in zip(expected_items, raw_items, strict=True):
            if not isinstance(item_data, dict):
                raise BuildError(
                    "Load navigation data",
                    "each navigation sub-item must be a JSON object",
                    path=navigation_path,
                    data_file=navigation_path,
                )
            if item_data.get("id") != exp_item["id"]:
                raise BuildError(
                    "Load navigation data",
                    f"navigation sub-item id mismatch: {item_data.get('id')}",
                    path=navigation_path,
                    data_file=navigation_path,
                )
            parsed_items.append(
                NavigationSubItem(
                    id=item_data["id"],
                    label=item_data["label"],
                    description=item_data["description"],
                    route=item_data["route"],
                )
            )

        parsed_sections.append(
            NavigationSection(
                id=section_data["id"],
                label=section_data["label"],
                description=section_data["description"],
                order=section_data["order"],
                items=tuple(parsed_items),
            )
        )

    return NavigationData(version=EXPECTED_VERSION, sections=tuple(parsed_sections))
