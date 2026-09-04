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

## 6. 마크다운 파서 들여쓰기 기반 복합 리스트 (OL/UL) 전면 개편
- [x] 모델 적합성 점검 및 승인:
  - 작업 위험도: 고위험 (High) - 코어 파서 렌더러 개편
  - 3-step Sequential Thinking 수행 및 `implementation_plan.md` 사용자 사전 승인 획득
- [x] 복합 리스트 상태 머신 구현 (`core/renderers/base.py`):
  - `_ListItem` 클래스 도입: 메인 텍스트와 함께 자식 블록(`child_blocks`) 및 서브 리스트(`sub_list_items`)를 계층적으로 캡슐화
  - 들여쓰기(선행 공백 >= 2) 감지: 활성 리스트 항목 아래에 작성된 코드 블록(` ``` `), 설명 문단(`<p>`), 서브 리스트(`- `, `\d+\.`)를 부모 `<li>`의 자식 요소로 안전하게 바인딩
  - 빈 줄 처리: 리스트 항목 내부의 빈 줄 1개에 대해 상위 리스트를 닫지 않고 유지하도록 개선
  - 하위 호환성 100% 유지 (기존 76개 페이지의 Flat 리스트 변경 없음)
- [x] 리스트 CSS 스타일 보강 (`assets/css/site.css`):
  - `li > p`: 상하 마진(0.35rem / 0.45rem) 최적화
  - `li > pre`: 리스트 내부 코드 블록 상하 여백 최적화
  - `li > ul`, `li > ol`: 서브 리스트 들여쓰기 패딩(1.25rem) 추가
- [x] 테스트 및 검증:
  - 신규 단위 테스트 추가 (`tests/test_composite_list_parser.py`): 4개 테스트 케이스 (Flat 리스트, 들여쓰기 문단, 들여쓰기 코드 블록, 중첩 리스트) 모두 PASS
  - 전체 단위 테스트 실행 (`python3 -m unittest discover tests`): 85 tests passed (OK)
  - 프롬프트 무결성 전수 감사 (`python3 scripts/audit_prompts.py`): 76개 페이지 전체 통과 (OK)
  - 정적 사이트 전수 빌드 (`python3 scripts/build.py`): 76개 페이지 정상 빌드 (Exit 0)
  - `dist/ai-assistant/core-direct/index.html`: `1.`, `2.` 순번 아래에 코드 블록이 자식으로 들어가 단일 `<ol>`로 정상 렌더링 확인

## 7. 전체 사이드 이펙트(Side Effect) 정밀 교차 검증
- [x] 76개 마크다운 파일 전체 HTML 태그 매칭 무결성 검증:
  - `<ol>`, `<ul>`, `<li>`, `<pre>`, `<code>`, `<div>`, `<p>` 정밀 정규식 검사 결과 76개 전체 파일 100% 균형 일치 (Unclosed/Mismatched 태그 0건)
- [x] 이전 파서(HEAD) 대비 76개 페이지 HTML 출력 차분(diff) 전수 분석:
  - 총 76개 중 59개 페이지: 100% 동일한 HTML 출력 유지 (Zero Side Effect)
  - 차이가 발생한 17개 페이지 정밀 분석:
    1. `ready-to-use.md` & `ai-practice.md`: 빈 줄로 인해 `<ol>`이 항목마다 강제로 닫혀 '1., 1., 1.'로 리셋되던 기존 버그가 단일 `<ol>`의 1~6번, 1~7번 정상 연속 번호로 자동 치유됨 확인
    2. `ai-assistant` 가이드 문서 5종(`gemini-verifier.md`, `korean-editor-guide.md` 등): 상위 항목 아래에 들여쓰기된 서브리스트가 상위 항목과 동일 레벨로 플랫하게 펼쳐지던 기존 결함이 올바른 2차 계층 중첩 리스트(`<ul><li>...<ul>...</ul></li></ul>`)로 정상 렌더링 확인
    3. `ready-to-use` 분석 프롬프트 6종(`photo-analysis.md`, `architecture-analysis.md` 등): 💡 실전 활용 팁의 1, 2, 3번 항목 내 서브 불릿 및 후속 질문이 번호 끊김 없이 단일 `<ol>` 내부에 안착됨 확인
    4. `prompt-snippets` 3종(`pre-mortem.md` 등): 들여쓰기된 불릿이 정상 중첩 구조로 개선됨 확인
- [x] 브라우저 스크린샷 런타임 렌더링 전수 교차 검증 (5개 대표 페이지):
  1. `ready-to-use/`: '이렇게 활용해 보세요' 1~6번 번호 리스트 연속성 PASS (`task1_ready_to_use_list_1788501026537.png`)
  2. `ai-practice/`: '프롬프트는 어떻게 완성될까요?' 1~7번 번호 리스트 연속성 PASS (`task2_ai_practice_list_1788501051990.png`)
  3. `prompt-snippets/pre-mortem/`: '💡 AI 활용 TIP' 중첩 불릿 및 들여쓰기 정렬 PASS (`task3_pre_mortem_tip_nested_list_1788501095991.png`)
  4. `ready-to-use/photo-analysis/`: '💡 실전 200% 활용 팁' 1, 2, 3번 번호 및 서브 불릿 조화 PASS (`task4_photo_analysis_tip_list_1788501177462.png`)
  5. `ai-assistant/gemini-verifier/`: 플랫폼별 추가 방법 서브 불릿 계층 정렬 PASS (`task5_gemini_verifier_subbullets_1788501203861.png`)
- [x] 자동화 테스트 스위트:
  - `python3 scripts/audit_prompts.py`: EXIT 0 (76개 페이지, 43개 에셋 통과)
  - `python3 scripts/build.py`: EXIT 0 (Pages: 76, Routes: 76 빌드 완료)
  - `python3 -m unittest discover tests`: Ran 85 tests (OK)

## 8. 페이지 헤더 카드(.page-intro) 설명문 좌우 여백 균형 개선
- [x] 원인 분석:
  - 상단 헤더 카드(`padding: 2.25rem 2.5rem`, 좌우 40px) 내부의 설명문(`.page-description`)에 `max-width: 68ch` 제한이 걸려 있어, 넓은 카드 너비 대비 텍스트가 좌측에 갇혀 우측에 거대한 빈 공간이 형성되는 비대칭 현상 확인
  - 상하 간격 수치: 제목과 설명문 간 `margin: 0.85rem 0 0` (약 13.6px), 행간 `line-height: 1.6` (약 26.8px)
- [x] 사용자 확인 및 반영:
  - 사용자 옵션 선택: 설명문 최대 너비(68ch) 해제 및 가로 100% 확장
  - `assets/css/site.css`: `.page-description`의 `max-width: none; width: 100%; word-break: keep-all;` 적용
- [x] 브라우저 검증:
  - `local_page_intro_balanced_1788505800669.png`: 설명문 텍스트가 카드의 좌우 40px 패딩을 대칭적으로 채우며 우측 빈 공간 불균형 완전 해소 확인
- [x] 자동화 검증:
  - `python3 scripts/audit_prompts.py`: EXIT 0
  - `python3 scripts/build.py`: EXIT 0
  - `python3 -m unittest discover tests`: Ran 85 tests (OK)

## 9. 전 화면(모바일·태블릿·데스크톱) 반응형(Fluid Responsive) 고도화
- [x] 모바일/태블릿 시각 결함 분석:
  - 40px(2.5rem) 고정 패딩으로 인해 375px 모바일 화면에서 가용 텍스트 영역이 295px로 좁아지고 답답한 여백 발생
  - 뷰포트 크기에 따른 텍스트 불균형 줄바꿈(orphaned word) 현상 확인
- [x] 유동형 clamp 및 모던 타이포그래피 규칙 적용 (`assets/css/site.css`):
  - `.page-intro`: 패딩을 `clamp(1.25rem, 3.5vw, 2.25rem) clamp(1.25rem, 4vw, 2.5rem)`로 전환 (모바일 20px -> 태블릿 ~30px -> 데스크톱 40px)
  - `.practice-step-card`: 패딩을 동일한 `clamp()`로 동기화하고, 마진을 `clamp(1rem, 2.5vw, 1.5rem) 0 !important`로 반응형화
  - `.page-title`: `font-size: clamp(1.45rem, 2.8vw, 2.35rem)`, `word-break: keep-all; text-wrap: balance;` 적용
  - `.page-description`: `margin: clamp(0.6rem, 1.5vw, 0.85rem) 0 0`, `font-size: clamp(0.95rem, 1.2vw, 1.05rem)`, `text-wrap: balance;` 적용
- [x] 멀티 뷰포트 브라우저 실화면 렌더링 검증:
  - 모바일(375px): 패딩 20px 축소로 카드 내부 가용 공간 대폭 확대, `text-wrap: balance`로 2줄 대칭 균형 줄바꿈 PASS (`responsive_mobile_header_1788506102674.png`)
  - 태블릿(768px): 패딩 30px, 설명문 1줄 최적 안착 및 좌우 여백 대칭 PASS (`responsive_tablet_header_1788506125176.png`)
  - 데스크톱(1440px): 패딩 40px의 시원하고 품격 있는 여백 및 완벽 정렬 PASS (`responsive_desktop_header_1788506129670.png`)
- [x] 자동화 테스트 스위트:
  - `python3 scripts/audit_prompts.py`: EXIT 0 (76개 페이지 통과)
  - `python3 scripts/build.py`: EXIT 0 (Pages: 76, Routes: 76 정상 빌드 완료)
  - `python3 -m unittest discover tests`: Ran 85 tests (OK)


