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
    {   'description': 'AI 입문자와 기초 활용자가 프롬프트 복사, 요청 정리, 이미지 AI 실습을 차근차근 배우는 한국어 학습 사이트',
        'id': 'home',
        'lang': 'ko',
        'navigation': False,
        'order': 0,
        'route': '/',
        'section': None,
        'source': 'pages/index.md',
        'status': 'published',
        'title': 'AI Learning Studio',
        'type': 'landing'},
    {   'description': '같은 주제에 여러 프롬프트 방식을 적용하고 결과 차이 비교하기',
        'id': 'ai-practice',
        'lang': 'ko',
        'navigation': True,
        'order': 1,
        'route': '/ai-practice/',
        'section': 'ai-practice',
        'source': 'pages/sections/ai-practice.md',
        'status': 'published',
        'title': '프롬프트 단계별 체험하기',
        'type': 'static-prompt'},
    {   'description': '여름휴가 계획이라는 같은 주제를 여러 프롬프트 방식으로 바꾸며 최종 프롬프트를 완성합니다.',
        'id': 'ai-practice-summer-vacation-basic',
        'lang': 'ko',
        'navigation': True,
        'order': 2,
        'route': '/ai-practice/summer-vacation-basic/',
        'section': 'ai-practice',
        'source': 'pages/sections/ai-practice/summer-vacation-basic.md',
        'status': 'published',
        'title': '여름휴가 계획 세우기 (프롬프트 기초편)',
        'type': 'static-prompt'},
    {   'description': '의정부 숨은 명소 1일 코스라는 같은 주제를 여러 프롬프트 방식으로 바꾸며 최종 프롬프트를 완성합니다.',
        'id': 'ai-practice-uijeongbu-oneday-tour',
        'lang': 'ko',
        'navigation': True,
        'order': 3,
        'route': '/ai-practice/uijeongbu-oneday-tour/',
        'section': 'ai-practice',
        'source': 'pages/sections/ai-practice/uijeongbu-oneday-tour.md',
        'status': 'published',
        'title': '의정부 숨은 명소 찾기',
        'type': 'static-prompt'},
    {   'description': '결과 품질을 높이는 한 줄 프롬프트 모음집',
        'id': 'prompt-snippets',
        'lang': 'ko',
        'navigation': True,
        'order': 4,
        'route': '/prompt-snippets/',
        'section': 'prompt-snippets',
        'source': 'pages/sections/prompt-snippets.md',
        'status': 'published',
        'title': '프롬프트 한 스푼',
        'type': 'static-prompt'},
    {   'description': '한 줄 추가로 답변의 깊이와 품질 높이기',
        'id': 'prompt-snippets-improve-results',
        'lang': 'ko',
        'navigation': True,
        'order': 5,
        'route': '/prompt-snippets/improve-results/',
        'section': 'prompt-snippets',
        'source': 'pages/sections/prompt-snippets/improve-results.md',
        'status': 'published',
        'title': '결과를 더 좋게 만들기 ⭐',
        'type': 'static-prompt'},
    {   'description': 'AI가 작성한 내용의 논리적 오류나 누락 확인',
        'id': 'prompt-snippets-review-answers',
        'lang': 'ko',
        'navigation': True,
        'order': 6,
        'route': '/prompt-snippets/review-answers/',
        'section': 'prompt-snippets',
        'source': 'pages/sections/prompt-snippets/review-answers.md',
        'status': 'published',
        'title': 'AI 답변 검토하기',
        'type': 'static-prompt'},
    {   'description': '거짓 정보를 방지하고 팩트 중심의 결과 얻기',
        'id': 'prompt-snippets-reduce-hallucination',
        'lang': 'ko',
        'navigation': True,
        'order': 7,
        'route': '/prompt-snippets/reduce-hallucination/',
        'section': 'prompt-snippets',
        'source': 'pages/sections/prompt-snippets/reduce-hallucination.md',
        'status': 'published',
        'title': '할루시네이션 줄이기 ⭐',
        'type': 'static-prompt'},
    {   'description': '막막할 때 창의적인 영감과 브레인스토밍',
        'id': 'prompt-snippets-get-ideas',
        'lang': 'ko',
        'navigation': True,
        'order': 8,
        'route': '/prompt-snippets/get-ideas/',
        'section': 'prompt-snippets',
        'source': 'pages/sections/prompt-snippets/get-ideas.md',
        'status': 'published',
        'title': '다양한 아이디어 얻기',
        'type': 'static-prompt'},
    {   'description': '글을 표, 불릿 포인트 등 한눈에 들어오게 변환',
        'id': 'prompt-snippets-format-clearly',
        'lang': 'ko',
        'navigation': True,
        'order': 9,
        'route': '/prompt-snippets/format-clearly/',
        'section': 'prompt-snippets',
        'source': 'pages/sections/prompt-snippets/format-clearly.md',
        'status': 'published',
        'title': '보기 쉽게 정리하기',
        'type': 'static-prompt'},
    {   'description': '독자의 눈높이와 지식 수준에 맞춰 내용 재작성',
        'id': 'prompt-snippets-change-level',
        'lang': 'ko',
        'navigation': True,
        'order': 10,
        'route': '/prompt-snippets/change-level/',
        'section': 'prompt-snippets',
        'source': 'pages/sections/prompt-snippets/change-level.md',
        'status': 'published',
        'title': '설명 수준 바꾸기',
        'type': 'static-prompt'},
    {   'description': '방대한 분량에서 엑기스만 빠르게 뽑아내기',
        'id': 'prompt-snippets-summarize-core',
        'lang': 'ko',
        'navigation': True,
        'order': 11,
        'route': '/prompt-snippets/summarize-core/',
        'section': 'prompt-snippets',
        'source': 'pages/sections/prompt-snippets/summarize-core.md',
        'status': 'published',
        'title': '요약과 핵심 정리',
        'type': 'static-prompt'},
    {   'description': '두 가지 이상의 대상을 다각도로 비교 분석하기',
        'id': 'prompt-snippets-compare-analyze',
        'lang': 'ko',
        'navigation': True,
        'order': 12,
        'route': '/prompt-snippets/compare-analyze/',
        'section': 'prompt-snippets',
        'source': 'pages/sections/prompt-snippets/compare-analyze.md',
        'status': 'published',
        'title': '비교와 분석',
        'type': 'static-prompt'},
    {   'description': '어색한 문장을 자연스럽고 매끄러운 글로 교정',
        'id': 'prompt-snippets-refine-text',
        'lang': 'ko',
        'navigation': True,
        'order': 13,
        'route': '/prompt-snippets/refine-text/',
        'section': 'prompt-snippets',
        'source': 'pages/sections/prompt-snippets/refine-text.md',
        'status': 'published',
        'title': '글 다듬기',
        'type': 'static-prompt'},
    {   'description': '끊긴 답변을 잇거나 흐름을 살려 추가 작업 요청',
        'id': 'prompt-snippets-continue-work',
        'lang': 'ko',
        'navigation': True,
        'order': 14,
        'route': '/prompt-snippets/continue-work/',
        'section': 'prompt-snippets',
        'source': 'pages/sections/prompt-snippets/continue-work.md',
        'status': 'published',
        'title': '이어서 작업하기',
        'type': 'static-prompt'},
    {   'description': '내가 원하는 걸 모를 때 AI에게 역질문 유도',
        'id': 'prompt-snippets-ask-better',
        'lang': 'ko',
        'navigation': True,
        'order': 15,
        'route': '/prompt-snippets/ask-better/',
        'section': 'prompt-snippets',
        'source': 'pages/sections/prompt-snippets/ask-better.md',
        'status': 'published',
        'title': 'AI에게 작업 요청 잘하기',
        'type': 'static-prompt'},
    {   'description': '수정이나 작성 전에 문제점과 놓친 부분부터 파악합니다.',
        'id': 'prompt-snippets-diagnose-first',
        'lang': 'ko',
        'navigation': True,
        'order': 16,
        'route': '/prompt-snippets/diagnose-first/',
        'section': 'prompt-snippets',
        'source': 'pages/sections/prompt-snippets/diagnose-first.md',
        'status': 'published',
        'title': '먼저 진단받기 ⭐',
        'type': 'static-prompt'},
    {   'description': '내 계획이나 생각에서 미처 고려하지 못한 사각지대를 찾아냅니다.',
        'id': 'prompt-snippets-find-missing',
        'lang': 'ko',
        'navigation': True,
        'order': 17,
        'route': '/prompt-snippets/find-missing/',
        'section': 'prompt-snippets',
        'source': 'pages/sections/prompt-snippets/find-missing.md',
        'status': 'published',
        'title': '내가 놓친 부분 찾기',
        'type': 'static-prompt'},
    {   'description': '잘 안 풀리는 일의 원인을 단계별로 쪼개어 진단합니다.',
        'id': 'prompt-snippets-find-problem',
        'lang': 'ko',
        'navigation': True,
        'order': 18,
        'route': '/prompt-snippets/find-problem/',
        'section': 'prompt-snippets',
        'source': 'pages/sections/prompt-snippets/find-problem.md',
        'status': 'published',
        'title': '어디에서 문제가 생겼는지 찾기',
        'type': 'static-prompt'},
    {   'description': '내 글이나 제안이 상대방에게 어떻게 들릴지 객관적으로 점검합니다.',
        'id': 'prompt-snippets-change-perspective',
        'lang': 'ko',
        'navigation': True,
        'order': 19,
        'route': '/prompt-snippets/change-perspective/',
        'section': 'prompt-snippets',
        'source': 'pages/sections/prompt-snippets/change-perspective.md',
        'status': 'published',
        'title': '상대방 입장에서 다시 보기',
        'type': 'static-prompt'},
    {   'description': '내 결정이 확실한지 점검하기 위해 가장 논리적인 반론을 미리 들어봅니다.',
        'id': 'prompt-snippets-listen-opposing',
        'lang': 'ko',
        'navigation': True,
        'order': 20,
        'route': '/prompt-snippets/listen-opposing/',
        'section': 'prompt-snippets',
        'source': 'pages/sections/prompt-snippets/listen-opposing.md',
        'status': 'published',
        'title': '반대 의견 들어보기',
        'type': 'static-prompt'},
    {   'description': '이미 잘 만들어진 원본을 완전히 다른 용도나 형식으로 바꿉니다.',
        'id': 'prompt-snippets-reuse-content',
        'lang': 'ko',
        'navigation': True,
        'order': 21,
        'route': '/prompt-snippets/reuse-content/',
        'section': 'prompt-snippets',
        'source': 'pages/sections/prompt-snippets/reuse-content.md',
        'status': 'published',
        'title': '결과물 다양하게 재활용하기',
        'type': 'static-prompt'},
    {   'description': '필요한 조건만 선택해 프롬프트를 만들고 바로 사용하기',
        'id': 'ready-to-use',
        'lang': 'ko',
        'navigation': True,
        'order': 22,
        'route': '/ready-to-use/',
        'section': 'ready-to-use',
        'source': 'pages/sections/ready-to-use.md',
        'status': 'published',
        'title': '바로 써보기',
        'type': 'static-prompt'},
    {   'description': '원하는 용도와 말투를 선택해 빠르고 자연스럽게 글을 다듬어 보세요.',
        'id': 'ready-to-use-korean-editor',
        'lang': 'ko',
        'navigation': True,
        'order': 23,
        'route': '/ready-to-use/korean-editor/',
        'section': 'ready-to-use',
        'source': 'pages/sections/ready-to-use/korean-editor.md',
        'status': 'published',
        'title': '맞춤형 한국어 교정',
        'type': 'static-prompt'},
    {   'description': '목표와 현재 수준, 사용 가능한 시간에 맞춰 현실적인 학습 계획을 짜주는 프롬프트 예제',
        'id': 'ready-to-use-self-development',
        'lang': 'ko',
        'navigation': True,
        'order': 24,
        'route': '/ready-to-use/self-development/',
        'section': 'ready-to-use',
        'source': 'pages/sections/ready-to-use/self-development.md',
        'status': 'published',
        'title': '자기 개발 학습 계획',
        'type': 'static-prompt'},
    {   'description': '긴 대화를 작업 인계서로 변환하여 어느 AI에서든 끊김 없이 이어서 작업할 수 있게 만드는 범용 프롬프트',
        'id': 'ready-to-use-universal-handoff',
        'lang': 'ko',
        'navigation': True,
        'order': 25,
        'route': '/ready-to-use/universal-handoff/',
        'section': 'ready-to-use',
        'source': 'pages/sections/ready-to-use/universal-handoff.md',
        'status': 'published',
        'title': 'AI 작업 이어가기',
        'type': 'static-prompt'},
    {   'description': '공식 영양 기준을 참고하여 조건에 맞는 레시피와 칼로리 정보를 생성하는 프롬프트',
        'id': 'ready-to-use-recipe-generator',
        'lang': 'ko',
        'navigation': True,
        'order': 26,
        'route': '/ready-to-use/recipe-generator/',
        'section': 'ready-to-use',
        'source': 'pages/sections/ready-to-use/recipe-generator.md',
        'status': 'published',
        'title': '뚝딱 완성! 맞춤 레시피 가이드',
        'type': 'static-prompt'},
    {   'description': 'Project·Gem 등에 사용할 맞춤형 역할과 지침 만들기',
        'id': 'ai-assistant',
        'lang': 'ko',
        'navigation': True,
        'order': 27,
        'route': '/ai-assistant/',
        'section': 'ai-assistant',
        'source': 'pages/sections/ai-assistant.md',
        'status': 'published',
        'title': '나만의 AI 만들기',
        'type': 'static-prompt'},
    {   'description': '사실을 지어내지 않게 하고, 불확실하면 확인이 필요하다고 말하게 하는 짧은 지침 프롬프트입니다.',
        'id': 'ai-assistant-hallucination-minimizer',
        'lang': 'ko',
        'navigation': True,
        'order': 28,
        'route': '/ai-assistant/hallucination-minimizer/',
        'section': 'ai-assistant',
        'source': 'pages/sections/ai-assistant/hallucination-minimizer.md',
        'status': 'published',
        'title': '할루시네이션 최소화',
        'type': 'static-prompt'},
    {   'description': 'Gemini GEMs 및 Projects 전용 지식 검증 전문가(Knowledge Verification Expert) 지침 프롬프트입니다.',
        'id': 'ai-assistant-gemini-verifier',
        'lang': 'ko',
        'navigation': True,
        'order': 29,
        'route': '/ai-assistant/gemini-verifier/',
        'section': 'ai-assistant',
        'source': 'pages/sections/ai-assistant/gemini-verifier.md',
        'status': 'published',
        'title': 'Gemini 지식 검증',
        'type': 'static-prompt'},
    {   'description': '실습에 바로 활용하는 국내외 맞춤형 여행 플래너 GEM·Project 전용 지침 프롬프트입니다.',
        'id': 'ai-assistant-vacation-planner',
        'lang': 'ko',
        'navigation': True,
        'order': 30,
        'route': '/ai-assistant/vacation-planner-guide/',
        'section': 'ai-assistant',
        'source': 'pages/sections/ai-assistant/vacation-planner-guide.md',
        'status': 'published',
        'title': '맞춤형 여행 플래너',
        'type': 'static-prompt'},
    {   'description': 'Gemini Canvas를 활용해 웹 브라우저에서 바로 작동하는 단일 HTML Leaflet 대화형 여행 지도를 만드는 프롬프트입니다.',
        'id': 'ai-assistant-gemini-canvas-map',
        'lang': 'ko',
        'navigation': True,
        'order': 31,
        'route': '/ai-assistant/gemini-canvas-map/',
        'section': 'ai-assistant',
        'source': 'pages/sections/ai-assistant/gemini-canvas-map.md',
        'status': 'published',
        'title': 'Gemini 캔버스 대화형 여행 지도',
        'type': 'static-prompt'},
    {   'description': '실습에 바로 활용하는 자연스러운 한국어 전문 편집자 GEM·Project 전용 지침 프롬프트입니다.',
        'id': 'ai-assistant-korean-editor',
        'lang': 'ko',
        'navigation': True,
        'order': 32,
        'route': '/ai-assistant/korean-editor-guide/',
        'section': 'ai-assistant',
        'source': 'pages/sections/ai-assistant/korean-editor-guide.md',
        'status': 'published',
        'title': '자연스러운 한국어 다듬기 지침서',
        'type': 'static-prompt'},
    {   'description': '번역을 최소화하고 흐름을 이어가며 맞춤형으로 회화를 훈련시키는 1:1 외국어 파트너 지침 프롬프트입니다.',
        'id': 'ai-assistant-language-tutor',
        'lang': 'ko',
        'navigation': True,
        'order': 33,
        'route': '/ai-assistant/language-tutor-guide/',
        'section': 'ai-assistant',
        'source': 'pages/sections/ai-assistant/language-tutor-guide.md',
        'status': 'published',
        'title': '외국어 회화 코치',
        'type': 'prompt-builder'},
    {   'description': '목표를 실천 가능한 작은 단위로 나누고, 무리하지 않게 지속할 수 있도록 돕는 1:1 맞춤형 코치 시스템 프롬프트입니다.',
        'id': 'ai-assistant-self-development-coach',
        'lang': 'ko',
        'navigation': True,
        'order': 34,
        'route': '/ai-assistant/self-development-coach/',
        'section': 'ai-assistant',
        'source': 'pages/sections/ai-assistant/self-development-coach.md',
        'status': 'published',
        'title': '현실적인 자기계발 코치',
        'type': 'static-prompt'},
    {   'description': '글이나 음성으로 AI와 천천히 인터뷰하며, 삶의 한 장면을 나다운 글로 남기는 지침서입니다.',
        'id': 'ai-assistant-life-story-interviewer',
        'lang': 'ko',
        'navigation': True,
        'order': 35,
        'route': '/ai-assistant/life-story-interviewer/',
        'section': 'ai-assistant',
        'source': 'pages/sections/ai-assistant/life-story-interviewer.md',
        'status': 'published',
        'title': '편안하게 대화하며 쓰는 나의 이야기',
        'type': 'markdown-prompt'},
    {   'description': '이미지 생성·편집에 사용할 프롬프트 만들기와 실습',
        'id': 'image-ai',
        'lang': 'ko',
        'navigation': True,
        'order': 36,
        'route': '/image-ai/',
        'section': 'image-ai',
        'source': 'pages/sections/image-ai.md',
        'status': 'published',
        'title': '이미지 만들기',
        'type': 'static-prompt'},
    {   'description': '원하는 문구를 입력해 마커로 그린 듯한 삐뚤빼뚤하고 귀여운 레터링 이미지를 만들어 보세요.',
        'id': 'image-ai-typography',
        'lang': 'ko',
        'navigation': True,
        'order': 37,
        'route': '/image-ai/typography/',
        'section': 'image-ai',
        'source': 'pages/sections/image-ai/typography.md',
        'status': 'published',
        'title': '손글씨 타이포그래피 만들기',
        'type': 'static-prompt'},
    {   'description': '원하는 음식 이름을 입력해 감각적이고 모던한 세로형 레시피 인포그래픽 이미지를 만들어 보세요.',
        'id': 'image-ai-recipe-infographic',
        'lang': 'ko',
        'navigation': True,
        'order': 38,
        'route': '/image-ai/recipe-infographic/',
        'section': 'image-ai',
        'source': 'pages/sections/image-ai/recipe-infographic.md',
        'status': 'published',
        'title': '모던 레시피 인포그래픽 생성',
        'type': 'prompt-builder'},
    {   'description': '내 사진과 직업을 바탕으로 다양한 모습의 3D 캐릭터 포스터 프롬프트를 만들어 보세요.',
        'id': 'image-ai-3d-career-character',
        'lang': 'ko',
        'navigation': True,
        'order': 39,
        'route': '/image-ai/3d-career-character/',
        'section': 'image-ai',
        'source': 'pages/sections/image-ai/3d-career-character.md',
        'status': 'published',
        'title': '나만의 3D 직업 캐릭터 만들기',
        'type': 'static-prompt'},
    {   'description': '내 사진을 기반으로 다양한 의상과 구도의 전문적인 프로필 사진을 제작해 보세요.',
        'id': 'image-ai-resume-profile',
        'lang': 'ko',
        'navigation': True,
        'order': 40,
        'route': '/image-ai/resume-profile/',
        'section': 'image-ai',
        'source': 'pages/sections/image-ai/resume-profile.md',
        'status': 'published',
        'title': 'AI 이력서·프로필 사진 생성',
        'type': 'static-prompt'},
    {   'description': '사진을 업로드하고 원하는 스타일과 분위기를 선택해 나만의 완벽한 SNS 프로필 이미지를 만들어 보세요.',
        'id': 'image-ai-sns-profile',
        'lang': 'ko',
        'navigation': True,
        'order': 41,
        'route': '/image-ai/sns-profile/',
        'section': 'image-ai',
        'source': 'pages/sections/image-ai/sns-profile.md',
        'status': 'published',
        'title': '맞춤형 SNS 프로필 만들기',
        'type': 'static-prompt'},
    {   'description': '원하는 문장을 입력해 종이 조각을 이어 붙인 아날로그 수작업 느낌의 콜라주 이미지를 만들어 보세요.',
        'id': 'image-ai-paper-collage',
        'lang': 'ko',
        'navigation': True,
        'order': 42,
        'route': '/image-ai/paper-collage/',
        'section': 'image-ai',
        'source': 'pages/sections/image-ai/paper-collage.md',
        'status': 'published',
        'title': '글자 조각 콜라주 만들기',
        'type': 'static-prompt'},
    {   'description': '평범한 폰카 사진을 전문 에디터의 손길이 닿은 듯한 고품질 스튜디오 화보 느낌으로 보정해 보세요.',
        'id': 'image-ai-photo-retouch',
        'lang': 'ko',
        'navigation': True,
        'order': 43,
        'route': '/image-ai/photo-retouch/',
        'section': 'image-ai',
        'source': 'pages/sections/image-ai/photo-retouch.md',
        'status': 'published',
        'title': '폰카 사진이 스튜디오 화보로',
        'type': 'static-prompt'},
    {   'description': '출발지와 목적지, 몸 상태와 짐의 정도를 입력하면 계단과 가파른 길을 피한 편한 이동 경로를 찾아줍니다.',
        'id': 'ready-to-use-uijeongbu-route-finder',
        'lang': 'ko',
        'navigation': True,
        'order': 44,
        'route': '/ready-to-use/uijeongbu-route-finder/',
        'section': 'ready-to-use',
        'source': 'pages/sections/ready-to-use/uijeongbu-route-finder.md',
        'status': 'published',
        'title': '의정부 편한 길 찾기',
        'type': 'static-prompt'},
    {   'description': '복잡한 마음을 털어놓고 싶을 때, 원하는 방식(위로, 정리, 해결책)에 맞춰 AI와 편안하게 대화할 수 있는 프롬프트입니다.',
        'id': 'ready-to-use-healing-chat',
        'lang': 'ko',
        'navigation': True,
        'order': 45,
        'route': '/ready-to-use/healing-chat/',
        'section': 'ready-to-use',
        'source': 'pages/sections/ready-to-use/healing-chat.md',
        'status': 'published',
        'title': '마음을 가볍게 정리하는 힐링 대화',
        'type': 'static-prompt'},
    {   'description': '경조사 종류와 관계, 참석 여부, 경제적 상황을 입력하면 최신 국내 조사와 공식 자료를 확인해 적절한 금액과 전달 방법을 추천합니다.',
        'id': 'ready-to-use-event-budget-calculator',
        'lang': 'ko',
        'navigation': True,
        'order': 46,
        'route': '/ready-to-use/event-budget-calculator/',
        'section': 'ready-to-use',
        'source': 'pages/sections/ready-to-use/event-budget-calculator.md',
        'status': 'published',
        'title': '상황에 맞는 경조사비 결정',
        'type': 'static-prompt'},
    {   'description': '장례식장에 처음 방문하는 사회초년생을 위해 복장부터 조문 순서, 예절, 피해야 할 행동까지 쉽고 정확하게 안내하는 프롬프트입니다.',
        'id': 'ready-to-use-funeral-etiquette',
        'lang': 'ko',
        'navigation': True,
        'order': 47,
        'route': '/ready-to-use/funeral-etiquette/',
        'section': 'ready-to-use',
        'source': 'pages/sections/ready-to-use/funeral-etiquette.md',
        'status': 'published',
        'title': '사회초년생을 위한 장례식장 예절',
        'type': 'markdown-prompt'},
    {   'description': '메뉴 사진과 옵션을 조합하여 잡지 화보 같은 고품질 프리미엄 푸드 포스터를 제작해 보세요.',
        'id': 'image-ai-food-poster',
        'lang': 'ko',
        'navigation': True,
        'order': 48,
        'route': '/image-ai/food-poster/',
        'section': 'image-ai',
        'source': 'pages/sections/image-ai/food-poster.md',
        'status': 'published',
        'title': '프리미엄 푸드 포스터 만들기',
        'type': 'static-prompt'},
    {   'description': 'AI가 사진을 보고, 사람이 확인하고, 대화를 이어가며 레시피를 완성합니다.',
        'id': 'ai-practice-fridge-recipe',
        'lang': 'ko',
        'navigation': True,
        'order': 49,
        'route': '/ai-practice/fridge-recipe/',
        'section': 'ai-practice',
        'source': 'pages/sections/ai-practice/fridge-recipe.md',
        'status': 'published',
        'title': '사진으로 레시피 찾기',
        'type': 'static-prompt'},
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
