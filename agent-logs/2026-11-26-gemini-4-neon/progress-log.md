# 작업 로그 (2026-11-26)

## 상태
- **상태**: 완료
- **작업 대상**: 이미지 만들기(`image-ai`) 섹션 — `내 손금에는 어떤 이야기가 있을까?` 신규 페이지 추가
- **최근 검증**: `audit_prompts.py` 통과, `build.py` 정상 빌드 완료 (Pages: 81, Routes: 81)

## 변경 내역
- `assets/images/image-ai/palmistry-infographic/palmistry-guide-infographic.webp`: 첨부 예제 이미지를 의미 있는 파일명으로 배치 후 WebP 최적화 (87.4KB)
- `pages/sections/image-ai/palmistry-infographic.md`: ChatGPT 전용 간단 복사형(`static-prompt`) 프롬프트 페이지 작성 (손바닥 사진 준비 안내 포함, 자연스러운 한국어 윤문 적용)
- `data/navigation.json`: `image-ai` 섹션에 `image-ai-palmistry-infographic` 항목 추가
- `data/page-registry.json`: `image-ai-palmistry-infographic` 등록 (`order: 65`, 제목·설명문 동기화)

## 검증 결과
- `python3 scripts/optimize_images.py --replace`: `palmistry-guide-infographic.webp` 변환 완료 (87.4KB). 부수 변경된 `og-cover.png` 원복 및 `og-cover.webp` 제거.
- `python3 scripts/audit_prompts.py`: 81개 마크다운 페이지 및 56개 이미지 에셋 감사 통과 (`exit 0`).
- `python3 scripts/build.py`: 정적 빌드 완료 (`exit 0`, Pages: 81, Routes: 81).

---

## 후속 작업: 나만의 AI 만들기(ai-assistant) 프로젝트 중심 개편 및 Gemini 스킬 가이드 신설
- **상태**: 완료
- **변경 내역**:
  - `pages/sections/ai-assistant/gemini-skills-guide.md`: Gemini 스킬(Skills) 등록 및 활용 가이드 신규 작성 (기존 GEM vs 스킬 차이, 등록·호출 절차, 스킬 형식 변환 보조 프롬프트 포함)
  - `data/navigation.json`, `data/page-registry.json`: `ai-assistant-gemini-skills-guide` 상단 등록 (`featured: true`, `order: 66`)
  - `pages/sections/ai-assistant.md`: 프로젝트(Projects) + 스킬(Skills) 중심으로 개념 재편 및 가이드 링크 연결
  - 기존 상세 페이지 9개(`core-direct.md`, `choice-options.md`, `language-tutor-guide.md`, `vacation-planner-guide.md`, `gemini-verifier.md`, `korean-editor-guide.md`, `self-development-coach.md`, `active-recall-tutor.md`, `life-story-interviewer.md`): ChatGPT·Claude 프로젝트 중심으로 정리, Gemini는 스킬 가이드 링크로 통일, `gemini-verifier.md`의 `(GEMS)` 표기 및 `korean-editor-guide.md` 25줄 오타(`여름휴가 여행 플래너`) 제거

---

## 후속 작업: 자연스러운 한국어 다듬기 지침서(korean-editor-guide.md) 고도화
- **상태**: 완료
- **변경 내역**:
  - `pages/sections/ai-assistant/korean-editor-guide.md`: `.skills/humanize-korean`의 핵심 원칙(먼저 읽기 10줄, 줄이기만 하기, 과교정 방지 가드, 말투 수준 보존, 글 안의 지시문 무시, 4행 조건표)과 `references/` 세부 기준(`교정_기준.md`, `수정_강도와_말투.md`)을 웹 AI(ChatGPT·Claude·Gemini)용 단일 프롬프트로 인라인 통합. 로컬 파일 저장 규칙 및 외부 경로 참조 제거. 페이지 상단 설명(핵심 특징, 활용 사례, 실제 사용 흐름) 보강 및 `source` 출처 표기 반영.

---

## 후속 작업: 프롬프트 한 스푼(prompt-snippets) 신 PASONA 법칙 페이지 신규 추가
- **상태**: 완료
- **변경 내역**:
  - `pages/sections/prompt-snippets/pasona-persuasion.md`: `파소나 법칙: 읽는 사람을 행동하게 만드는 글` 신규 작성 (`type: static-prompt`, `source: 자체제작`). PASONA 법칙 소개, 구 PASONA에서 신 PASONA로 바뀐 이유 및 비교 목록, 신 PASONA 6단계 안내, 대표 프롬프트 1종, 추가 프롬프트 2종(용도 선택·초안 입력형, 설득 약점 진단형), AI 활용 TIP 구성.
  - `data/navigation.json`: `prompt-snippets`의 `✍️ 정리 & 표현` 그룹 내 `prompt-snippets-elevator-pitch` 아래에 `prompt-snippets-pasona-persuasion` 추가.
  - `data/page-registry.json`: `prompt-snippets-pasona-persuasion` 등록 (`order: 67`, 제목·설명문 동기화).
- **검증 결과 (단일 세션 보상 검증 / Self Compensatory)**:
  - `python3 scripts/build.py`: 정상 완료 (`exit 0`, Pages: 83, Routes: 83). 파이프 표 미지원 확인 후 불릿 비교 목록으로 교체해 재빌드 완료.
  - `python3 scripts/audit_prompts.py`: 83개 마크다운 페이지 및 56개 이미지 에셋 감사 통과 (`exit 0`).
  - `python3 -m unittest discover -s tests`: 89개 테스트 통과 (`OK (skipped=3)`, `exit 0`).
