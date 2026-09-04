# 작업 진행 로그 (2026-09-04)

## 1. 작업 개요
- **작업명**: 신규 프롬프트 페이지 추가 및 표준 형식화: "군더더기 없이 바로 핵심만"
- **위치**: `나만의 AI 만들기` (`ai-assistant`)
- **라우트**: `/ai-assistant/core-direct/`
- **페이지 유형**: `static-prompt`
- **출처**: `GitHub (@ayghri/i-have-adhd)`

## 2. 표준 형식화 및 작업 내역
- [x] Frontmatter 규격 동기화:
  - `ai_target: Gemini, ChatGPT, Claude` 명시
  - `type: static-prompt` 명시
  - `source: GitHub (@ayghri/i-have-adhd)` (타 페이지의 `Threads (@...)`와 동일한 플랫폼·계정 표준화)
- [x] 섹션 및 헤딩 구조를 기존 `ai-assistant` 대표 페이지(`gemini-verifier.md`, `self-development-coach.md`)와 완벽 일치:
  - H1 제목 및 핵심 인트로
  - `**💡 활용 팁**` 인라인 강조 블록
  - `## 지침서 핵심 특징` (4대 가치)
  - `## AI 서비스별 지침 추가 및 활용 방법` (1. Gemini GEMs, 2. ChatGPT 맞춤설정/Projects, 3. Claude Projects)
  - `## 일반 답변 vs 핵심 답변 비교`
  - `## 나만의 핵심 지침 프롬프트 복사하기` (`prompt` 코드 블록)
  - `## 💡 실전 200% 활용 꿀팁` (3대 요령)
- [x] 네비게이션 및 레지스트리 무결성 검증 완료
- [x] `python3 scripts/build.py`: EXIT 0 (Build complete, Pages: 76, Routes: 76)
- [x] `python3 scripts/audit_prompts.py`: EXIT 0 ([OK] All prompt audits passed successfully!)
- [x] `dist/ai-assistant/core-direct/index.html` 내 `Source : GitHub (@ayghri/i-have-adhd)` 표준 슬림 박스 렌더링 확인

## 3. markdown-prompt 렌더러 출처(Source) 독립 분리 버그 수정
- [x] 원인 분석: `core/renderers/markdown_prompt.py`에서 `PromptItemComponent`의 `prompt_source_html`에 `source_html`을 직접 넘겨 마크다운 본문 카드(`.practice-step-card`) 내부에 소스 박스가 갇히는 결함 확인
- [x] 수술적 수정:
  - `PromptItemComponent.prompt_source_html`을 `""`로 비움
  - 본문 플레이스홀더 치환 후 마크다운 본문 카드(`.practice-step-card`)가 닫힌 바깥 하단에 `source_html`을 독립 배치하도록 수정
- [x] 검증:
  - `dist/ai-assistant/life-story-interviewer/index.html` 내 `Source : 자체제작` 독립 슬림 박스 렌더링 확인
  - `dist/ready-to-use/funeral-etiquette/index.html` 내 `Source : 자체제작` 독립 슬림 박스 렌더링 확인
  - `python3 scripts/build.py`: EXIT 0 (Build complete, Pages: 76)
  - `python3 -m unittest discover tests`: 81 tests passed (OK)

## 4. core-direct.md 마크다운 렌더링 결함 수술적 수정
- [x] 원인 분석 및 해결:
  - 꿀팁 순번 누락: 마크다운 파서가 단락 간 빈 줄에 의해 `<ol>`을 닫아버려 번호가 끊기던 현상을 Flat 단일 라인 순번 목록(`1. `, `2. `, `3. `)으로 통합하여 단일 `<ol>` 태그 아래 정상적인 1, 2, 3 순번 렌더링 복원
  - 일반 AI 답변 줄나눔: 단락별 빈 줄을 유지하고 마지막 설명 문단(`*(장황한 설명...)*`)을 별도 문단으로 명확히 분리
  - 핵심 답변 코드 및 백틱 결함: 파서가 지원하지 않는 인용구(`>`)와 인라인 백틱(`` ` ``)을 제거하고, 코드 블록을 줄 맨 앞(` ```bash `, ` ```json `)으로 온전히 배치하여 백틱 기호 노출 없이 `<pre><code>` 코드 상자로 선명하게 렌더링되도록 수정. 순번 분절 방지를 위해 볼드 단계명(`**1단계: ...**`, `**2단계: ...**`) 적용
- [x] 검증:
  - `dist/ai-assistant/core-direct/index.html` 렌더링 결과 확인 완료
  - `python3 scripts/build.py`: EXIT 0 (Build complete, Pages: 76, Routes: 76)
  - `python3 scripts/audit_prompts.py`: EXIT 0
  - `python3 -m unittest discover tests`: 81 tests passed (OK)

## 5. 꿀팁 카드 표준 패턴 적용 및 CSS 코드 블록 스타일링
- [x] 꿀팁 카드 테마 복원:
  - `core/renderers/base.py`: 팁 카드 매칭 조건을 `any("활용 꿀팁" in b or "Quick Tips" in b for b in card_blocks)`로 개선하여 키워드 유연성 확보
  - `pages/sections/ai-assistant/core-direct.md`: 고품질 표준 패턴(`### 💡 실전 활용 꿀팁 (Quick Tips)` 배지 헤더 + `#### 1. 소제목` + `- 불릿 리스트`)으로 전환하여 둔탁한 H4 덩어리 제거 및 알약 배지 UI 복원
- [x] 코드 블록 시각 디자인 보강:
  - `assets/css/site.css`: `.practice-step-card pre` 및 `code` 전용 스타일 추가 (모던 쿨그레이 캔버스 배경, 테두리, JetBrains Mono 고대비 폰트 적용)
- [x] 검증:
  - `dist/ai-assistant/core-direct/index.html`: `practice-step-card--tips` 알약 배지 및 불릿 리스트 정상 렌더링 확인
  - `python3 scripts/build.py`: EXIT 0 (Build complete, Pages: 76, Routes: 76)
  - `python3 scripts/audit_prompts.py`: EXIT 0
  - `python3 -m unittest discover tests`: 81 tests passed (OK)
