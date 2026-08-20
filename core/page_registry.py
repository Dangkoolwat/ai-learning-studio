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
    {'id': 'home', 'title': 'AI Learning Studio', 'description': 'AI 입문자와 기초 활용자가 프롬프트 복사, 요청 정리, 이미지 AI 실습을 차근차근 배우는 한국어 학습 사이트', 'route': '/', 'source': 'pages/index.md', 'type': 'landing', 'section': None, 'order': 0, 'navigation': False, 'status': 'published', 'lang': 'ko'},
    {'id': 'ai-practice', 'title': '프롬프트 단계별 체험하기', 'description': '같은 주제에 여러 프롬프트 방식을 적용하고 결과 차이 비교하기', 'route': '/ai-practice/', 'source': 'pages/sections/ai-practice.md', 'type': 'static-prompt', 'section': 'ai-practice', 'order': 1, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ai-practice-summer-vacation-basic', 'title': '여름휴가 계획 세우기 (프롬프트 기초편)', 'description': '여름휴가 계획이라는 같은 주제를 여러 프롬프트 방식으로 바꾸며 최종 프롬프트를 완성합니다.', 'route': '/ai-practice/summer-vacation-basic/', 'source': 'pages/sections/ai-practice/summer-vacation-basic.md', 'type': 'static-prompt', 'section': 'ai-practice', 'order': 2, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ai-practice-uijeongbu-oneday-tour', 'title': '의정부 숨은 명소 찾기', 'description': '의정부 숨은 명소 1일 코스라는 같은 주제를 여러 프롬프트 방식으로 바꾸며 최종 프롬프트를 완성합니다.', 'route': '/ai-practice/uijeongbu-oneday-tour/', 'source': 'pages/sections/ai-practice/uijeongbu-oneday-tour.md', 'type': 'static-prompt', 'section': 'ai-practice', 'order': 3, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'prompt-snippets', 'title': '프롬프트 한 스푼', 'description': '결과 품질을 높이는 한 줄 프롬프트 모음집', 'route': '/prompt-snippets/', 'source': 'pages/sections/prompt-snippets.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'order': 4, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'prompt-snippets-improve-results', 'title': '결과를 더 좋게 만들기 ⭐', 'description': '한 줄 추가로 답변의 깊이와 품질 높이기', 'route': '/prompt-snippets/improve-results/', 'source': 'pages/sections/prompt-snippets/improve-results.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'order': 5, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'prompt-snippets-review-answers', 'title': 'AI 답변 검토하기', 'description': 'AI가 작성한 내용의 논리적 오류나 누락 확인', 'route': '/prompt-snippets/review-answers/', 'source': 'pages/sections/prompt-snippets/review-answers.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'order': 6, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'prompt-snippets-reduce-hallucination', 'title': '할루시네이션 줄이기 ⭐', 'description': '거짓 정보를 방지하고 팩트 중심의 결과 얻기', 'route': '/prompt-snippets/reduce-hallucination/', 'source': 'pages/sections/prompt-snippets/reduce-hallucination.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'order': 7, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'prompt-snippets-get-ideas', 'title': '다양한 아이디어 얻기', 'description': '막막할 때 창의적인 영감과 브레인스토밍', 'route': '/prompt-snippets/get-ideas/', 'source': 'pages/sections/prompt-snippets/get-ideas.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'order': 8, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'prompt-snippets-format-clearly', 'title': '보기 쉽게 정리하기', 'description': '글을 표, 불릿 포인트 등 한눈에 들어오게 변환', 'route': '/prompt-snippets/format-clearly/', 'source': 'pages/sections/prompt-snippets/format-clearly.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'order': 9, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'prompt-snippets-change-level', 'title': '설명 수준 바꾸기', 'description': '독자의 눈높이와 지식 수준에 맞춰 내용 재작성', 'route': '/prompt-snippets/change-level/', 'source': 'pages/sections/prompt-snippets/change-level.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'order': 10, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'prompt-snippets-summarize-core', 'title': '요약과 핵심 정리', 'description': '방대한 분량에서 엑기스만 빠르게 뽑아내기', 'route': '/prompt-snippets/summarize-core/', 'source': 'pages/sections/prompt-snippets/summarize-core.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'order': 11, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'prompt-snippets-compare-analyze', 'title': '비교와 분석', 'description': '두 가지 이상의 대상을 다각도로 비교 분석하기', 'route': '/prompt-snippets/compare-analyze/', 'source': 'pages/sections/prompt-snippets/compare-analyze.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'order': 12, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'prompt-snippets-refine-text', 'title': '글 다듬기', 'description': '어색한 문장을 자연스럽고 매끄러운 글로 교정', 'route': '/prompt-snippets/refine-text/', 'source': 'pages/sections/prompt-snippets/refine-text.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'order': 13, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'prompt-snippets-continue-work', 'title': '이어서 작업하기', 'description': '끊긴 답변을 잇거나 흐름을 살려 추가 작업 요청', 'route': '/prompt-snippets/continue-work/', 'source': 'pages/sections/prompt-snippets/continue-work.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'order': 14, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'prompt-snippets-ask-better', 'title': 'AI에게 작업 요청 잘하기', 'description': '내가 원하는 걸 모를 때 AI에게 역질문 유도', 'route': '/prompt-snippets/ask-better/', 'source': 'pages/sections/prompt-snippets/ask-better.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'order': 15, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'prompt-snippets-diagnose-first', 'title': '먼저 진단받기 ⭐', 'description': '수정이나 작성 전에 문제점과 놓친 부분부터 파악합니다.', 'route': '/prompt-snippets/diagnose-first/', 'source': 'pages/sections/prompt-snippets/diagnose-first.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'navigation': True, 'status': 'published', 'lang': 'ko', 'order': 16},
    {'id': 'prompt-snippets-find-missing', 'title': '내가 놓친 부분 찾기', 'description': '내 계획이나 생각에서 미처 고려하지 못한 사각지대를 찾아냅니다.', 'route': '/prompt-snippets/find-missing/', 'source': 'pages/sections/prompt-snippets/find-missing.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'navigation': True, 'status': 'published', 'lang': 'ko', 'order': 17},
    {'id': 'prompt-snippets-find-problem', 'title': '어디에서 문제가 생겼는지 찾기', 'description': '잘 안 풀리는 일의 원인을 단계별로 쪼개어 진단합니다.', 'route': '/prompt-snippets/find-problem/', 'source': 'pages/sections/prompt-snippets/find-problem.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'navigation': True, 'status': 'published', 'lang': 'ko', 'order': 18},
    {'id': 'prompt-snippets-change-perspective', 'title': '상대방 입장에서 다시 보기', 'description': '내 글이나 제안이 상대방에게 어떻게 들릴지 객관적으로 점검합니다.', 'route': '/prompt-snippets/change-perspective/', 'source': 'pages/sections/prompt-snippets/change-perspective.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'navigation': True, 'status': 'published', 'lang': 'ko', 'order': 19},
    {'id': 'prompt-snippets-listen-opposing', 'title': '반대 의견 들어보기', 'description': '내 결정이 확실한지 점검하기 위해 가장 논리적인 반론을 미리 들어봅니다.', 'route': '/prompt-snippets/listen-opposing/', 'source': 'pages/sections/prompt-snippets/listen-opposing.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'navigation': True, 'status': 'published', 'lang': 'ko', 'order': 20},
    {'id': 'prompt-snippets-reuse-content', 'title': '결과물 다양하게 재활용하기', 'description': '이미 잘 만들어진 원본을 완전히 다른 용도나 형식으로 바꿉니다.', 'route': '/prompt-snippets/reuse-content/', 'source': 'pages/sections/prompt-snippets/reuse-content.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'navigation': True, 'status': 'published', 'lang': 'ko', 'order': 21},
    {'id': 'prompt-snippets-second-order-effect', 'title': '그다음 영향까지 생각하기 ⭐', 'description': '당장의 결과뿐만 아니라 그 결과에 이어서 생길 수 있는 2차·3차 연쇄 파급효과까지 짚어봅니다.', 'route': '/prompt-snippets/second-order-effect/', 'source': 'pages/sections/prompt-snippets/second-order-effect.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'navigation': True, 'status': 'published', 'lang': 'ko', 'order': 22},
    {'id': 'prompt-snippets-audit-assumptions', 'title': '내가 당연하다고 생각한 가정 찾기', 'description': '내 생각이나 계획 밑바닥에 당연하게 깔려 있는 숨은 전제를 들춰냅니다.', 'route': '/prompt-snippets/audit-assumptions/', 'source': 'pages/sections/prompt-snippets/audit-assumptions.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'navigation': True, 'status': 'published', 'lang': 'ko', 'order': 23},
    {'id': 'prompt-snippets-evaluate-tradeoff', 'title': '선택할 때 무엇을 포기해야 하는지 확인', 'description': '선택으로 얻는 것뿐만 아니라 대신 포기해야 하는 가치와 대가를 함께 비교합니다.', 'route': '/prompt-snippets/evaluate-tradeoff/', 'source': 'pages/sections/prompt-snippets/evaluate-tradeoff.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'navigation': True, 'status': 'published', 'lang': 'ko', 'order': 24},
    {'id': 'prompt-snippets-detect-biases', 'title': '내 판단이 한쪽으로 치우쳤는지 확인', 'description': '내 글이나 생각에 선입견이나 편향이 섞여 있는지 단정하지 않고 확인합니다.', 'route': '/prompt-snippets/detect-biases/', 'source': 'pages/sections/prompt-snippets/detect-biases.md', 'type': 'static-prompt', 'section': 'prompt-snippets', 'navigation': True, 'status': 'published', 'lang': 'ko', 'order': 25},
    {'id': 'ready-to-use', 'title': '바로 써보기', 'description': '필요한 조건만 선택해 프롬프트를 만들고 바로 사용하기', 'route': '/ready-to-use/', 'source': 'pages/sections/ready-to-use.md', 'type': 'static-prompt', 'section': 'ready-to-use', 'order': 26, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ready-to-use-korean-editor', 'title': '1회용 맞춤형 한국어 교정', 'description': '글의 성격에 맞춰 문맥과 흐름이 자연스럽게 다듬는 한국어 교정 도우미', 'route': '/ready-to-use/korean-editor/', 'source': 'pages/sections/ready-to-use/korean-editor.md', 'type': 'static-prompt', 'section': 'ready-to-use', 'order': 27, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ready-to-use-self-development', 'title': '자기 개발 학습 계획', 'description': '목표와 현재 수준, 사용 가능한 시간에 맞춰 현실적인 학습 계획을 짜주는 프롬프트 예제', 'route': '/ready-to-use/self-development/', 'source': 'pages/sections/ready-to-use/self-development.md', 'type': 'static-prompt', 'section': 'ready-to-use', 'order': 28, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ready-to-use-universal-handoff', 'title': 'AI 작업 이어가기', 'description': 'AI와의 긴 대화가 끊겼을 때 이전 맥락을 압축해 다른 대화방으로 넘기는 프롬프트', 'route': '/ready-to-use/universal-handoff/', 'source': 'pages/sections/ready-to-use/universal-handoff.md', 'type': 'static-prompt', 'section': 'ready-to-use', 'order': 29, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ready-to-use-recipe-generator', 'title': '뚝딱 완성! 맞춤 레시피 가이드', 'description': '공식 영양 기준을 참고하여 조건에 맞는 레시피와 칼로리 정보를 생성하는 프롬프트', 'route': '/ready-to-use/recipe-generator/', 'source': 'pages/sections/ready-to-use/recipe-generator.md', 'type': 'static-prompt', 'section': 'ready-to-use', 'order': 30, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ai-assistant', 'title': '나만의 AI 만들기', 'description': 'Project·Gem 등에 사용할 맞춤형 역할과 지침 만들기', 'route': '/ai-assistant/', 'source': 'pages/sections/ai-assistant.md', 'type': 'static-prompt', 'section': 'ai-assistant', 'order': 31, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ai-assistant-hallucination-minimizer', 'title': '할루시네이션 최소화', 'description': '사실을 지어내지 않게 하고, 불확실하면 확인이 필요하다고 말하게 하는 짧은 지침 프롬프트입니다.', 'route': '/ai-assistant/hallucination-minimizer/', 'source': 'pages/sections/ai-assistant/hallucination-minimizer.md', 'type': 'static-prompt', 'section': 'ai-assistant', 'order': 32, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ai-assistant-gemini-verifier', 'title': 'Gemini 지식 검증', 'description': 'Gemini가 도출한 결과물의 출처와 지식의 신뢰성을 교차 검증하는 분석 도구', 'route': '/ai-assistant/gemini-verifier/', 'source': 'pages/sections/ai-assistant/gemini-verifier.md', 'type': 'static-prompt', 'section': 'ai-assistant', 'order': 33, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ai-assistant-vacation-planner', 'title': '맞춤형 여행 플래너', 'description': '여행 주제와 기간을 입력하면 팩트 중심의 1일 동선 및 지도 링크를 추천하는 여행 도우미', 'route': '/ai-assistant/vacation-planner-guide/', 'source': 'pages/sections/ai-assistant/vacation-planner-guide.md', 'type': 'static-prompt', 'section': 'ai-assistant', 'order': 34, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ai-assistant-gemini-canvas-map', 'title': 'Gemini 캔버스 대화형 여행 지도', 'description': 'Gemini 캔버스 기능을 활용해 대화하며 반응형 웹 여행 지도를 직접 구현하고 시각화하는 제작 가이드', 'route': '/ai-assistant/gemini-canvas-map/', 'source': 'pages/sections/ai-assistant/gemini-canvas-map.md', 'type': 'static-prompt', 'section': 'ai-assistant', 'order': 35, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ai-assistant-korean-editor', 'title': '자연스러운 한국어 다듬기 지침서', 'description': '자연스러운 한국어 문체, 어조, 흐름을 살려 전문 에디터처럼 글을 윤문하는 교정 지침서', 'route': '/ai-assistant/korean-editor-guide/', 'source': 'pages/sections/ai-assistant/korean-editor-guide.md', 'type': 'static-prompt', 'section': 'ai-assistant', 'order': 36, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ai-assistant-language-tutor', 'title': '외국어 회화 코치', 'description': '번역을 최소화하고 흐름을 이어가며 맞춤형으로 회화를 훈련시키는 1:1 외국어 파트너 지침 프롬프트입니다.', 'route': '/ai-assistant/language-tutor-guide/', 'source': 'pages/sections/ai-assistant/language-tutor-guide.md', 'type': 'prompt-builder', 'section': 'ai-assistant', 'order': 37, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ai-assistant-self-development-coach', 'title': '현실적인 자기계발 코치', 'description': '사용자의 환경과 조건에 맞춰 무리하지 않고 실천 가능한 현실적인 자기계발 코칭 가이드', 'route': '/ai-assistant/self-development-coach/', 'source': 'pages/sections/ai-assistant/self-development-coach.md', 'type': 'static-prompt', 'section': 'ai-assistant', 'order': 38, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ai-assistant-life-story-interviewer', 'title': '편안하게 대화하며 쓰는 나의 이야기', 'description': '글이나 음성으로 AI와 천천히 인터뷰하며, 삶의 한 장면을 나다운 글로 남기는 지침서입니다.', 'route': '/ai-assistant/life-story-interviewer/', 'source': 'pages/sections/ai-assistant/life-story-interviewer.md', 'type': 'markdown-prompt', 'section': 'ai-assistant', 'order': 39, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ai-assistant-active-recall-tutor', 'title': '1:1 Active Recall 학습 코치', 'description': '질문과 피드백으로 내가 아는 것과 모르는 것을 직접 확인하는 맞춤형 학습 코치', 'route': '/ai-assistant/active-recall-tutor/', 'source': 'pages/sections/ai-assistant/active-recall-tutor.md', 'type': 'prompt-builder', 'section': 'ai-assistant', 'order': 40, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'image-ai', 'title': '이미지 만들기', 'description': '이미지 생성·편집에 사용할 프롬프트 만들기와 실습', 'route': '/image-ai/', 'source': 'pages/sections/image-ai.md', 'type': 'static-prompt', 'section': 'image-ai', 'order': 41, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'image-ai-typography', 'title': '손글씨 타이포그래피 만들기', 'description': '원하는 문구를 입력해 마커로 그린 듯한 삐뚤빼뚤하고 귀여운 레터링 이미지를 만들어 보세요.', 'route': '/image-ai/typography/', 'source': 'pages/sections/image-ai/typography.md', 'type': 'static-prompt', 'section': 'image-ai', 'order': 42, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'image-ai-recipe-infographic', 'title': '모던 레시피 인포그래픽 생성', 'description': '원하는 음식 이름을 입력해 감각적이고 모던한 세로형 레시피 인포그래픽 이미지를 만들어 보세요.', 'route': '/image-ai/recipe-infographic/', 'source': 'pages/sections/image-ai/recipe-infographic.md', 'type': 'prompt-builder', 'section': 'image-ai', 'order': 43, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'image-ai-3d-career-character', 'title': '나만의 3D 직업 캐릭터 만들기', 'description': '내 사진과 직업을 바탕으로 다양한 모습의 3D 캐릭터 포스터 프롬프트를 만들어 보세요.', 'route': '/image-ai/3d-career-character/', 'source': 'pages/sections/image-ai/3d-career-character.md', 'type': 'static-prompt', 'section': 'image-ai', 'order': 44, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'image-ai-resume-profile', 'title': 'AI 전문 프로필 사진 생성', 'description': '인물 사진을 활용해 신뢰감 있고 깔끔한 분위기의 이력서 및 비즈니스 프로필 사진을 제작합니다.', 'route': '/image-ai/resume-profile/', 'source': 'pages/sections/image-ai/resume-profile.md', 'type': 'static-prompt', 'section': 'image-ai', 'order': 45, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'image-ai-sns-profile', 'title': '맞춤형 SNS 프로필 만들기', 'description': '사진을 업로드하고 원하는 스타일과 분위기를 선택해 나만의 완벽한 SNS 프로필 이미지를 만들어 보세요.', 'route': '/image-ai/sns-profile/', 'source': 'pages/sections/image-ai/sns-profile.md', 'type': 'static-prompt', 'section': 'image-ai', 'order': 46, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'image-ai-paper-collage', 'title': '글자 조각 콜라주 만들기', 'description': '잡지, 문자 조각, 사진을 아날로그 감성으로 찢어 붙인 듯한 개성 있는 신문/종이 콜라주 아트를 만듭니다.', 'route': '/image-ai/paper-collage/', 'source': 'pages/sections/image-ai/paper-collage.md', 'type': 'static-prompt', 'section': 'image-ai', 'order': 47, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'image-ai-photo-retouch', 'title': '폰카 사진이 스튜디오 화보로', 'description': '평범한 폰카 사진을 전문 에디터의 손길이 닿은 듯한 고품질 스튜디오 화보 느낌으로 보정해 보세요.', 'route': '/image-ai/photo-retouch/', 'source': 'pages/sections/image-ai/photo-retouch.md', 'type': 'static-prompt', 'section': 'image-ai', 'order': 48, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ready-to-use-uijeongbu-route-finder', 'title': '의정부 편한 길 찾기', 'description': '출발지와 목적지, 몸 상태와 짐의 정도를 입력하면 계단과 가파른 길을 피한 편한 이동 경로를 찾아줍니다.', 'type': 'static-prompt', 'route': '/ready-to-use/uijeongbu-route-finder/', 'section': 'ready-to-use', 'order': 49, 'navigation': True, 'status': 'published', 'lang': 'ko', 'source': 'pages/sections/ready-to-use/uijeongbu-route-finder.md'},
    {'id': 'ready-to-use-healing-chat', 'title': '마음을 가볍게 정리하는 힐링 대화', 'description': '복잡한 마음을 털어놓고 싶을 때, 원하는 방식(위로, 정리, 해결책)에 맞춰 AI와 편안하게 대화할 수 있는 프롬프트입니다.', 'route': '/ready-to-use/healing-chat/', 'source': 'pages/sections/ready-to-use/healing-chat.md', 'type': 'static-prompt', 'section': 'ready-to-use', 'order': 50, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ready-to-use-event-budget-calculator', 'title': '상황에 맞는 경조사비 결정', 'description': '경조사 종류와 관계, 참석 여부, 경제적 상황을 입력하면 최신 국내 조사와 공식 자료를 확인해 적절한 금액과 전달 방법을 추천합니다.', 'route': '/ready-to-use/event-budget-calculator/', 'source': 'pages/sections/ready-to-use/event-budget-calculator.md', 'type': 'static-prompt', 'section': 'ready-to-use', 'order': 51, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ready-to-use-funeral-etiquette', 'title': '사회초년생을 위한 장례식장 예절', 'description': '장례식장에 처음 방문하는 사회초년생을 위해 복장부터 조문 순서, 예절, 피해야 할 행동까지 쉽고 정확하게 안내하는 프롬프트입니다.', 'route': '/ready-to-use/funeral-etiquette/', 'source': 'pages/sections/ready-to-use/funeral-etiquette.md', 'type': 'markdown-prompt', 'section': 'ready-to-use', 'order': 52, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'image-ai-food-poster', 'title': '프리미엄 푸드 포스터 만들기', 'description': '메뉴 사진과 옵션을 조합하여 잡지 화보 같은 고품질 프리미엄 푸드 포스터를 제작해 보세요.', 'route': '/image-ai/food-poster/', 'source': 'pages/sections/image-ai/food-poster.md', 'type': 'static-prompt', 'section': 'image-ai', 'order': 53, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'image-ai-child-doodle', 'title': '사진을 어린이 손그림으로 바꾸기', 'description': '사진을 어린아이가 검은 펜과 색연필로 따라 그린 것처럼 바꿔보세요.', 'route': '/image-ai/child-doodle/', 'source': 'pages/sections/image-ai/child-doodle.md', 'type': 'static-prompt', 'section': 'image-ai', 'order': 54, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'image-ai-silly-doodle', 'title': '인물을 엉뚱한 낙서 캐릭터로 바꾸기', 'description': '사진 속 인물을 알아볼 수 있는 특징은 살리고, 흰 종이에 검은 펜으로 대충 그린 듯한 엉뚱한 낙서 캐릭터로 바꿔보세요.', 'route': '/image-ai/silly-doodle/', 'source': 'pages/sections/image-ai/silly-doodle.md', 'type': 'static-prompt', 'section': 'image-ai', 'order': 55, 'navigation': True, 'status': 'published', 'lang': 'ko'},
    {'id': 'ai-practice-fridge-recipe', 'title': '사진으로 레시피 찾기', 'description': '냉장고 속 재료 사진을 기반으로 맞춤 레시피를 제안하고, 대화를 나누며 요리 가이드를 완성해 보세요.', 'route': '/ai-practice/fridge-recipe/', 'source': 'pages/sections/ai-practice/fridge-recipe.md', 'type': 'static-prompt', 'section': 'ai-practice', 'order': 56, 'navigation': True, 'status': 'published', 'lang': 'ko'},
)
EXPECTED_PAGE_IDS = tuple(page["id"] for page in EXPECTED_PAGES)
EXPECTED_SOURCE_FILES = tuple(page["source"] for page in EXPECTED_PAGES)
EXPECTED_ROUTE_MAP = {page["id"]: page["route"] for page in EXPECTED_PAGES}


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
