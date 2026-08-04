# Progress Log (2026-08-04)

## 1. Goal
Implement `markdown-prompt` page type to render markdown prompt content directly as plain, unparsed text inside the code block without interactive chips, while retaining the copy button functionality and avoiding side effects with the existing component architecture.

## 2. Implementation Plan (Executed)
- **Rollback**: Cleaned up the initial complex implementation to avoid side-effects.
- **Registration**: 
  - Added `markdown-prompt` to `APPROVED_RENDERER_IDS` (`core/renderer_models.py`).
  - Added `markdown-prompt` to `PUBLIC_PAGE_TYPES` and updated page registry data (`core/page_registry.py`, `data/page-registry.json`).
- **Validation update**:
  - Updated `core/renderer_validation.py` to expect same component sections for `markdown-prompt` as `static-prompt`.
- **Renderer creation (`core/renderers/markdown_prompt.py`)**:
  - Copied the logic of `static_prompt.py` identically to retain all UI architecture stability.
  - Substituted the body parsing step so that it uses `escape_html(prompt_block.body)` and forces `has_inline_controls = False`.
  - Registered renderer in `core/page_renderers.py`.

## 3. Verification
- `python3 scripts/build.py` ran successfully.
- Verified visual output via `browser_subagent` and confirmed that the prompt's `[블로그 / 보고서 / 메일 ...]` syntax is rendered natively as plain text instead of being parsed as interactive chips, matching the design request perfectly.

[Status / Files Changed / Verification / Handoff Status]
- **Status**: 완료
- **Files Changed**:
  - `core/page_renderers.py`
  - `core/page_registry.py`
  - `core/renderer_models.py`
  - `core/renderer_validation.py`
  - `core/renderers/markdown_prompt.py` (New)
  - `data/page-registry.json`
  - `pages/sections/ready-to-use/korean-editor.md`
- **Verification**: `python3 scripts/build.py` 정상 빌드 성공 및 UI 스크린샷 렌더링 확인 완료.
- **Handoff Status**: 대기

## 2. '나의 인생 이야기 인터뷰어' 페이지 추가 완료
- `ai-assistant` 섹션 하위에 신규 페이지 추가 (`ai-assistant-life-story-interviewer`).
- `data/page-registry.json`, `core/page_registry.py`, `data/navigation.json`에 모두 정상 등록 및 Order 정리 완벽 매핑.
- 사용자가 직접 제공한 마크다운을 `markdown-prompt` 타입으로 생성 (`pages/sections/ai-assistant/life-story-interviewer.md`).
- 브라우저 스크린샷 검증을 통해 ChatGPT 프롬프트 블록이 복사 버튼과 함께 raw text로 정상 렌더링됨을 확인.

## 3. 페이지 타이틀 변경 (나의 인생 이야기 인터뷰어 -> 편안하게 대화하며 쓰는 나의 이야기)
- 사용자의 피드백에 따라 감성적인 톤으로 페이지 타이틀 변경.
- 변경된 파일: `data/navigation.json`, `data/page-registry.json`, `core/page_registry.py`, `pages/sections/ai-assistant/life-story-interviewer.md`.
- 정상 빌드 확인 완료.

## 4. '의정부 숨은 명소 1일 코스 만들기 (기초편)' 실습 페이지 추가
-  섹션에 `ai-practice-uijeongbu-oneday-tour` 페이지 신규 추가.
- 사용자가 작성한 구조화된 마크다운 프롬프트를 바탕으로 `type: static-prompt` 적용하여 렌더링 검증.
- 영문 오탈자(`uijeingbu` -> `uijeongbu`) 수정 적용.
- 레지스트리와 네비게이션을 업데이트하고 order를 자동 재조정하여 저장소에 성공적으로 통합.
- 브라우저 스크린샷 캡처를 통해 인라인 옵션 칩(`[가능역]`, `[9시]` 등)이 올바르게 인터랙티브 드롭다운으로 변환됨을 확인.

## 4. '의정부 숨은 명소 1일 코스 만들기 (기초편)' 실습 페이지 추가
- `ai-practice` 섹션에 `ai-practice-uijeongbu-oneday-tour` 페이지 신규 추가.
- 사용자가 작성한 구조화된 마크다운 프롬프트를 바탕으로 `type: static-prompt` 적용하여 렌더링 검증.
- 영문 오탈자(`uijeingbu` -> `uijeongbu`) 수정 적용.
- 레지스트리와 네비게이션을 업데이트하고 order를 자동 재조정하여 저장소에 성공적으로 통합.
- 브라우저 스크린샷 캡처를 통해 인라인 옵션 칩(`[가능역]`, `[9시]` 등)이 올바르게 인터랙티브 드롭다운으로 변환됨을 확인.

## 5. 실습 페이지 타이틀 간소화
- 기존: \`의정부 숨은 명소 1일 코스 만들기 (프롬프트 기초편)\`
- 변경: 본문 및 레지스트리 \`의정부 숨은 명소 찾기\`, 네비게이션 좌측 메뉴 \`의정부 숨은 명소 찾기(기초편)\`
- 변경 파일: \`data/navigation.json\`, \`core/navigation.py\`, \`data/page-registry.json\`, \`core/page_registry.py\`, \`uijeongbu-oneday-tour.md\`

## [2026-08-04] 맞춤형 레시피 생성기 구현

### 계획
- `core/page_registry.py` 및 `data/page-registry.json`에 `ready-to-use-recipe-generator` 추가.
- `core/navigation.py` 및 `data/navigation.json`에 메뉴 추가.
- `pages/sections/ready-to-use/recipe-generator.md` 프롬프트 파일 생성 (사용자의 영양/칼로리 계산 규칙 반영).

### 실행 로그
- **[x]** 4개의 레지스트리 및 내비게이션 파일 업데이트 완료.
- **[x]** 마크다운 프롬프트 템플릿 작성 및 속성값(`type: static-prompt`) 지정 완료.

### 검증
- `python3 scripts/build.py` 실행 결과: 23개 페이지 빌드 성공.
- 로컬 서버(`scripts/serve.py`) 구동 후 브라우저 서브에이전트를 통해 스크린샷 캡처 및 화면 레이아웃 정상 렌더링 확인 완료.

### 후속 수정 (Follow-up)
- **이슈**: 프롬프트 본문을 감싸는 ` ```prompt ` 코드블록 누락으로 UI 상에서 선택형 칩 컴포넌트가 올바르게 렌더링되지 않음.
- **수정**: `pages/sections/ready-to-use/recipe-generator.md` 내 프롬프트 내용을 ` ```prompt ` 블록으로 감싸고, 내부 `title`과 `description` 메타데이터를 추가.
- **검증**: `python3 scripts/build.py` 재실행 완료.

### 후속 수정 2 (Follow-up)
- **변경 사항**: 
  - `인원` 선택 옵션 추가 (1명/2명/3명/4명).
  - `먹는 사람` 옵션을 `먹는 사람 또는 식사 목적`으로 구체화 및 항목 수정.
  - 출력 형식을 기존 9개에서 10개로 분리하여 `예상 영양정보` 항목을 독립적으로 표기.
  - 레시피 제공 후 대체 재료 및 레시피 조정을 안내하는 안내 멘트 규칙 추가.
- **검증**: `python3 scripts/build.py` 정상 완료.

### 후속 수정 3 (Follow-up)
- **변경 사항**: 메뉴 제목 및 페이지 타이틀을 `맞춤형 레시피 생성기`에서 `뚝딱 완성! 맞춤 레시피 가이드`로 전면 교체.
- **적용 대상**: `data/navigation.json`, `data/page-registry.json`, `core/navigation.py`, `core/page_registry.py`, `pages/sections/ready-to-use/recipe-generator.md`
- **검증**: `python3 scripts/build.py` 정상 완료.

### 후속 수정 4 (Follow-up)
- **변경 사항**: 프롬프트의 `[출력 형식]` 부분 최상단에 마크다운(Markdown) 형식으로 가독성 좋게 출력하라는 명시적인 AI 지시사항 추가.
- **적용 대상**: `pages/sections/ready-to-use/recipe-generator.md`
- **검증**: `python3 scripts/build.py` 정상 완료.

### 후속 수정 5 (Follow-up)
- **변경 사항**: 프롬프트 내부의 섹션 제목들(`[입력 조건]`, `[출력 형식]` 등)이 URL 파라미터로 넘겨지거나 일부 환경에서 복사될 때 HTTP 400 에러(Malformed Request)를 유발하는 문제를 방지하기 위해, 모든 대괄호(`[]`) 섹션 제목을 마크다운 헤더(`###`) 형식으로 일괄 변경.
- **적용 대상**: `pages/sections/ready-to-use/recipe-generator.md`
- **검증**: `python3 scripts/build.py` 정상 완료.

### 후속 수정 6 (Follow-up)
- **변경 사항**: 프롬프트 라이브러리 전체(`.md`)에서 구역을 나누는 목적으로 사용된 대괄호(`[ ]`) 섹션 제목들을 모두 마크다운 헤더(`###`) 형식으로 안전하게 일괄 변환 완료. 
- **예외 처리 검증**: AI에게 지시하기 위한 출력 폼 형태의 괄호(`[원래 표현]`, `[고친 표현]`, `[단계 제목]` 등)나, 사용자가 입력 옵션을 고르는 형태(`[블로그 / 메일]`)는 치환되지 않고 원래대로 유지되도록 엄격히 예외 처리함.
- **적용 대상**: `korean-editor-guide.md`, `vacation-planner-guide.md`, `self-development-coach.md`, `recipe-infographic.md`, `gemini-canvas-map.md`
- **검증**: `python3 scripts/build.py` 정상 완료.

### 맞춤형 여행 플래너 통합 구현 완료
- **변경 사항**: 기존 여름휴가 전용 플래너를 국내외 범용으로 전환 (제목 및 메뉴명: `맞춤형 여행 플래너 지침서`로 변경)
- **기능 추가**: 해외여행 필수 점검 요소 (비자, 여권 만료일, 환전/환율, 시차, 로밍/유심 등) 확인 항목 추가 반영
- **적용 파일**: `vacation-planner-guide.md`, `navigation.json`, `page-registry.json`, `navigation.py`, `page_registry.py`
- **검증**: `python3 scripts/build.py` 정상 통과

### 신규 페이지 추가: 의정부 편한 길 찾기
- **변경 사항**: 사용자가 제안한 [의정부 편한 길 찾기 프롬프트]를 신규 생성 및 레지스트리 등록
- **경로**: `pages/sections/ready-to-use/uijeongbu-route-finder.md`
- **검증**: `python3 scripts/build.py` 정상 통과 (총 24개 페이지 렌더링 확인)

### 신규 페이지 추가: 마음을 가볍게 정리하는 힐링 대화
- **변경 사항**: 사용자가 제안한 [마음을 가볍게 정리하는 힐링 대화 프롬프트]를 신규 생성 및 레지스트리 등록
- **경로**: `pages/sections/ready-to-use/healing-chat.md`
- **검증**: `python3 scripts/build.py` 정상 통과 (총 25개 페이지 렌더링 확인)
- **버전 관리**: Git Commit 및 원격 레포지토리 Push 완료

### 힐링 대화 프롬프트 업데이트
- **변경 사항**: [사용자 주도 원칙] 섹션 추가 (감정 확인, 동의 구하기 등 4가지 지침)
- **경로**: `pages/sections/ready-to-use/healing-chat.md`
- **버전 관리**: 빌드 테스트 정상 통과 및 Git Push 완료
