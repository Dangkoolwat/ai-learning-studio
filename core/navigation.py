"""Navigation contract helpers for AI Learning Studio."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from core.errors import BuildError


EXPECTED_VERSION = 1
EXPECTED_SECTIONS = (
    {   'description': '같은 주제에 여러 프롬프트 방식을 적용하고 결과 차이 비교하기',
        'id': 'ai-practice',
        'items': [   {   'description': '여름휴가 계획이라는 같은 주제를 여러 프롬프트 방식으로 바꾸며 최종 프롬프트 완성하기',
                         'id': 'ai-practice-summer-vacation-basic',
                         'label': '여름휴가 계획 세우기 (기초편)',
                         'route': '/ai-practice/summer-vacation-basic/'},
                     {   'description': '의정부 숨은 명소 1일 코스라는 같은 주제를 여러 프롬프트 방식으로 바꾸며 최종 프롬프트를 완성하기',
                         'id': 'ai-practice-uijeongbu-oneday-tour',
                         'label': '의정부 숨은 명소 찾기(기초편)',
                         'route': '/ai-practice/uijeongbu-oneday-tour/'},
                     {   'description': '냉장고 속 재료 사진을 기반으로 맞춤 레시피를 제안하고, 대화를 나누며 요리 가이드를 완성해 보세요.',
                         'id': 'ai-practice-fridge-recipe',
                         'label': '사진으로 레시피 찾기',
                         'route': '/ai-practice/fridge-recipe/'}],
        'label': '프롬프트 단계별 체험하기',
        'order': 1},
    {   'description': '결과 품질을 높이는 한 줄 프롬프트 모음집',
        'id': 'prompt-snippets',
        'items': [   {   'description': '한 줄 추가로 답변의 깊이와 품질 높이기',
                         'id': 'prompt-snippets-improve-results',
                         'label': '결과를 더 좋게 만들기 ⭐',
                         'route': '/prompt-snippets/improve-results/'},
                     {   'description': 'AI가 작성한 내용의 논리적 오류나 누락 확인',
                         'id': 'prompt-snippets-review-answers',
                         'label': 'AI 답변 검토하기',
                         'route': '/prompt-snippets/review-answers/'},
                     {   'description': '거짓 정보를 방지하고 팩트 중심의 결과 얻기',
                         'id': 'prompt-snippets-reduce-hallucination',
                         'label': '할루시네이션 줄이기 ⭐',
                         'route': '/prompt-snippets/reduce-hallucination/'},
                     {   'description': '막막할 때 창의적인 영감과 브레인스토밍',
                         'id': 'prompt-snippets-get-ideas',
                         'label': '다양한 아이디어 얻기',
                         'route': '/prompt-snippets/get-ideas/'},
                     {   'description': '글을 표, 불릿 포인트 등 한눈에 들어오게 변환',
                         'id': 'prompt-snippets-format-clearly',
                         'label': '보기 쉽게 정리하기',
                         'route': '/prompt-snippets/format-clearly/'},
                     {   'description': '독자의 눈높이와 지식 수준에 맞춰 내용 재작성',
                         'id': 'prompt-snippets-change-level',
                         'label': '설명 수준 바꾸기',
                         'route': '/prompt-snippets/change-level/'},
                     {   'description': '방대한 분량에서 엑기스만 빠르게 뽑아내기',
                         'id': 'prompt-snippets-summarize-core',
                         'label': '요약과 핵심 정리',
                         'route': '/prompt-snippets/summarize-core/'},
                     {   'description': '두 가지 이상의 대상을 다각도로 비교 분석하기',
                         'id': 'prompt-snippets-compare-analyze',
                         'label': '비교와 분석',
                         'route': '/prompt-snippets/compare-analyze/'},
                     {   'description': '어색한 문장을 자연스럽고 매끄러운 글로 교정',
                         'id': 'prompt-snippets-refine-text',
                         'label': '글 다듬기',
                         'route': '/prompt-snippets/refine-text/'},
                     {   'description': '끊긴 답변을 잇거나 흐름을 살려 추가 작업 요청',
                         'id': 'prompt-snippets-continue-work',
                         'label': '이어서 작업하기',
                         'route': '/prompt-snippets/continue-work/'},
                     {   'description': '내가 원하는 걸 모를 때 AI에게 역질문 유도',
                         'id': 'prompt-snippets-ask-better',
                         'label': 'AI에게 작업 요청 잘하기',
                         'route': '/prompt-snippets/ask-better/'},
                     {   'description': '수정이나 작성 전에 문제점과 놓친 부분부터 파악합니다.',
                         'id': 'prompt-snippets-diagnose-first',
                         'label': '먼저 진단받기 ⭐',
                         'route': '/prompt-snippets/diagnose-first/'},
                     {   'description': '내 계획이나 생각에서 미처 고려하지 못한 사각지대를 찾아냅니다.',
                         'id': 'prompt-snippets-find-missing',
                         'label': '내가 놓친 부분 찾기',
                         'route': '/prompt-snippets/find-missing/'},
                     {   'description': '잘 안 풀리는 일의 원인을 단계별로 쪼개어 진단합니다.',
                         'id': 'prompt-snippets-find-problem',
                         'label': '어디에서 문제가 생겼는지 찾기',
                         'route': '/prompt-snippets/find-problem/'},
                     {   'description': '내 글이나 제안이 상대방에게 어떻게 들릴지 객관적으로 점검합니다.',
                         'id': 'prompt-snippets-change-perspective',
                         'label': '상대방 입장에서 다시 보기',
                         'route': '/prompt-snippets/change-perspective/'},
                     {   'description': '내 결정이 확실한지 점검하기 위해 가장 논리적인 반론을 미리 들어봅니다.',
                         'id': 'prompt-snippets-listen-opposing',
                         'label': '반대 의견 들어보기',
                         'route': '/prompt-snippets/listen-opposing/'},
                     {   'description': '이미 잘 만들어진 원본을 완전히 다른 용도나 형식으로 바꿉니다.',
                         'id': 'prompt-snippets-reuse-content',
                         'label': '결과물 다양하게 재활용하기',
                         'route': '/prompt-snippets/reuse-content/'},
                     {   'description': '당장의 결과뿐만 아니라 그 결과에 이어서 생길 수 있는 2차·3차 연쇄 파급효과까지 짚어봅니다.',
                         'id': 'prompt-snippets-second-order-effect',
                         'label': '그다음 영향까지 생각하기 ⭐',
                         'route': '/prompt-snippets/second-order-effect/'},
                     {   'description': '내 생각이나 계획 밑바닥에 당연하게 깔려 있는 숨은 전제를 들춰냅니다.',
                         'id': 'prompt-snippets-audit-assumptions',
                         'label': '내가 당연하다고 생각한 가정 찾기',
                         'route': '/prompt-snippets/audit-assumptions/'},
                     {   'description': '선택으로 얻는 것뿐만 아니라 대신 포기해야 하는 가치와 대가를 함께 비교합니다.',
                         'id': 'prompt-snippets-evaluate-tradeoff',
                         'label': '선택할 때 무엇을 포기해야 하는지 확인',
                         'route': '/prompt-snippets/evaluate-tradeoff/'},
                     {   'description': '내 글이나 생각에 선입견이나 편향이 섞여 있는지 단정하지 않고 확인합니다.',
                         'id': 'prompt-snippets-detect-biases',
                         'label': '내 판단이 한쪽으로 치우쳤는지 확인',
                         'route': '/prompt-snippets/detect-biases/'}],
        'label': '프롬프트 한 스푼',
        'order': 2},
    {   'description': '필요한 조건만 선택해 프롬프트를 만들고 바로 사용하기',
        'id': 'ready-to-use',
        'items': [   {   'description': '글의 성격에 맞춰 문맥과 흐름이 자연스럽게 다듬는 한국어 교정 도우미',
                         'id': 'ready-to-use-korean-editor',
                         'label': '1회용 맞춤형 한국어 교정',
                         'route': '/ready-to-use/korean-editor/'},
                     {   'description': '목표와 현재 수준, 사용 가능한 시간에 맞춰 현실적인 학습 계획을 짜주는 프롬프트 예제',
                         'id': 'ready-to-use-self-development',
                         'label': '자기 개발 학습 계획',
                         'route': '/ready-to-use/self-development/'},
                     {   'description': 'AI와의 긴 대화가 끊겼을 때 이전 맥락을 압축해 다른 대화방으로 넘기는 프롬프트',
                         'id': 'ready-to-use-universal-handoff',
                         'label': 'AI 작업 이어가기',
                         'route': '/ready-to-use/universal-handoff/'},
                     {   'description': '공식 영양 기준을 참고하여 조건에 맞는 레시피와 칼로리 정보를 생성하는 프롬프트',
                         'id': 'ready-to-use-recipe-generator',
                         'label': '뚝딱 완성! 맞춤 레시피 가이드',
                         'route': '/ready-to-use/recipe-generator/'},
                     {   'description': '출발지와 목적지, 몸 상태와 짐의 정도를 입력하면 계단과 가파른 길을 피한 편한 이동 경로를 찾아줍니다.',
                         'id': 'ready-to-use-uijeongbu-route-finder',
                         'label': '의정부 편한 길 찾기',
                         'route': '/ready-to-use/uijeongbu-route-finder/'},
                     {   'description': '복잡한 마음을 털어놓고 싶을 때, 원하는 방식(위로, 정리, 해결책)에 맞춰 AI와 편안하게 대화할 수 있는 '
                                        '프롬프트입니다.',
                         'id': 'ready-to-use-healing-chat',
                         'label': '마음을 가볍게 정리하는 힐링 대화',
                         'route': '/ready-to-use/healing-chat/'},
                     {   'description': '경조사 종류와 관계, 참석 여부, 경제적 상황을 입력하면 최신 국내 조사와 공식 자료를 확인해 적절한 금액과 '
                                        '전달 방법을 추천합니다.',
                         'id': 'ready-to-use-event-budget-calculator',
                         'label': '상황에 맞는 경조사비 결정',
                         'route': '/ready-to-use/event-budget-calculator/'},
                     {   'description': '장례식장에 처음 방문하는 사회초년생을 위해 복장부터 조문 순서, 예절, 피해야 할 행동까지 쉽고 정확하게 '
                                        '안내하는 프롬프트입니다.',
                         'id': 'ready-to-use-funeral-etiquette',
                         'label': '사회초년생을 위한 장례식장 예절',
                         'route': '/ready-to-use/funeral-etiquette/'}],
        'label': '바로 써보기',
        'order': 3},
    {   'description': 'Project·Gem 등에 사용할 맞춤형 역할과 지침 만들기',
        'id': 'ai-assistant',
        'items': [   {   'description': '불확실한 부분을 숨기지 않게 하는 짧은 지침',
                         'id': 'ai-assistant-hallucination-minimizer',
                         'label': '할루시네이션 최소화',
                         'route': '/ai-assistant/hallucination-minimizer/'},
                     {   'description': 'Gemini가 도출한 결과물의 출처와 지식의 신뢰성을 교차 검증하는 분석 도구',
                         'id': 'ai-assistant-gemini-verifier',
                         'label': 'Gemini 지식 검증',
                         'route': '/ai-assistant/gemini-verifier/'},
                     {   'description': '여행 주제와 기간을 입력하면 팩트 중심의 1일 동선 및 지도 링크를 추천하는 여행 도우미',
                         'id': 'ai-assistant-vacation-planner',
                         'label': '맞춤형 여행 플래너',
                         'route': '/ai-assistant/vacation-planner-guide/'},
                     {   'description': 'Gemini 캔버스 기능을 활용해 대화하며 반응형 웹 여행 지도를 직접 구현하고 시각화하는 제작 가이드',
                         'id': 'ai-assistant-gemini-canvas-map',
                         'label': 'Gemini 캔버스 대화형 여행 지도',
                         'route': '/ai-assistant/gemini-canvas-map/'},
                     {   'description': '자연스러운 한국어 문체, 어조, 흐름을 살려 전문 에디터처럼 글을 윤문하는 교정 지침서',
                         'id': 'ai-assistant-korean-editor',
                         'label': '자연스러운 한국어 다듬기 지침서',
                         'route': '/ai-assistant/korean-editor-guide/'},
                     {   'description': '번역을 최소화하고 흐름을 이어가며 맞춤형으로 회화를 훈련시키는 파트너 지침서',
                         'id': 'ai-assistant-language-tutor',
                         'label': '외국어 회화 코치',
                         'route': '/ai-assistant/language-tutor-guide/'},
                     {   'description': '사용자의 환경과 조건에 맞춰 무리하지 않고 실천 가능한 현실적인 자기계발 코칭 가이드',
                         'id': 'ai-assistant-self-development-coach',
                         'label': '현실적인 자기계발 코치',
                         'route': '/ai-assistant/self-development-coach/'},
                     {   'description': '글이나 음성으로 AI와 천천히 인터뷰하며, 삶의 한 장면을 나다운 글로 남기는 지침서입니다.',
                         'id': 'ai-assistant-life-story-interviewer',
                         'label': '편안하게 대화하며 쓰는 나의 이야기',
                         'route': '/ai-assistant/life-story-interviewer/'},
                     {   'description': '질문과 피드백으로 내가 아는 것과 모르는 것을 직접 확인하는 맞춤형 학습 코치',
                         'id': 'ai-assistant-active-recall-tutor',
                         'label': '1:1 Active Recall 학습 코치',
                         'route': '/ai-assistant/active-recall-tutor/'}],
        'label': '나만의 AI 만들기',
        'order': 4},
    {   'description': '이미지 생성·편집에 사용할 프롬프트 만들기와 실습',
        'id': 'image-ai',
        'items': [   {   'description': '원하는 문구를 입력해 마커로 그린 듯한 삐뚤빼뚤하고 귀여운 레터링 이미지를 만들어 보세요.',
                         'id': 'image-ai-typography',
                         'label': '손글씨 타이포그래피 만들기',
                         'route': '/image-ai/typography/'},
                     {   'description': '원하는 음식 이름을 입력해 감각적이고 모던한 세로형 레시피 인포그래픽 이미지를 만들어 보세요.',
                         'id': 'image-ai-recipe-infographic',
                         'label': '모던 레시피 인포그래픽 생성',
                         'route': '/image-ai/recipe-infographic/'},
                     {   'description': '내 사진과 직업을 바탕으로 다양한 모습의 3D 캐릭터 포스터 프롬프트를 만들어 보세요.',
                         'id': 'image-ai-3d-career-character',
                         'label': '나만의 3D 직업 캐릭터 만들기',
                         'route': '/image-ai/3d-career-character/'},
                     {   'description': '인물 사진을 활용해 신뢰감 있고 깔끔한 분위기의 이력서 및 비즈니스 프로필 사진을 제작합니다.',
                         'id': 'image-ai-resume-profile',
                         'label': 'AI 전문 프로필 사진 생성',
                         'route': '/image-ai/resume-profile/'},
                     {   'description': '사진을 업로드하고 원하는 스타일과 분위기를 선택해 나만의 완벽한 SNS 프로필 이미지를 만들어 보세요.',
                         'id': 'image-ai-sns-profile',
                         'label': '맞춤형 SNS 프로필 만들기',
                         'route': '/image-ai/sns-profile/'},
                     {   'description': '잡지, 문자 조각, 사진을 아날로그 감성으로 찢어 붙인 듯한 개성 있는 신문/종이 콜라주 아트를 만듭니다.',
                         'id': 'image-ai-paper-collage',
                         'label': '글자 조각 콜라주 만들기',
                         'route': '/image-ai/paper-collage/'},
                     {   'description': '평범한 폰카 사진을 전문 에디터의 손길이 닿은 듯한 고품질 스튜디오 화보 느낌으로 보정해 보세요.',
                         'id': 'image-ai-photo-retouch',
                         'label': '폰카 사진이 스튜디오 화보로',
                         'route': '/image-ai/photo-retouch/'},
                     {   'description': '메뉴 사진과 옵션을 조합하여 잡지 화보 같은 고품질 프리미엄 푸드 포스터를 제작해 보세요.',
                         'id': 'image-ai-food-poster',
                         'label': '프리미엄 푸드 포스터 만들기',
                         'route': '/image-ai/food-poster/'},
                     {   'description': '사진을 어린아이가 검은 펜과 색연필로 따라 그린 것처럼 바꿔보세요.',
                         'id': 'image-ai-child-doodle',
                         'label': '사진을 어린이 손그림으로 바꾸기',
                         'route': '/image-ai/child-doodle/'},
                     {   'description': '사진 속 인물을 알아볼 수 있는 특징은 살리고, 흰 종이에 검은 펜으로 대충 그린 듯한 엉뚱한 낙서 캐릭터로 바꿔보세요.',
                         'id': 'image-ai-silly-doodle',
                         'label': '인물을 엉뚱한 낙서 캐릭터로 바꾸기',
                         'route': '/image-ai/silly-doodle/'}],
        'label': '이미지 만들기',
        'order': 5},
)


@dataclass(frozen=True)
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


@dataclass(frozen=True)
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


@dataclass
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
    for expected, section_data in zip(EXPECTED_SECTIONS, sections):
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
        for exp_item, item_data in zip(expected_items, raw_items):
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
