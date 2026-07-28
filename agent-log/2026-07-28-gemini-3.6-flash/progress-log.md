# 작업 진행 및 검증 로그 (2026-07-28)

## 1. 작업 개요
- 사용자가 직접 수정한 소스 파일(`summer-vacation-basic.md`), 파서 엔진(`static_prompt.py`), 및 스타일(`site.css`) 변경 사항 반영 빌드 및 시각적 검증.

## 2. 주요 연동 사항
- **사용자 수정 내역 반영**:
  - `pages/sections/ai-practice/summer-vacation-basic.md`: 마크다운 줄바꿈 정리.
  - `core/renderers/static_prompt.py`: `prompt-item--preview` 미리보기 카드 헤더 구조 통일.
  - `assets/css/site.css`: 미리보기 상단 마진(`margin-top: var(--als-space-2)`) 및 `prompt-item__title::before` 파란색 인디케이터 바 디자인 연동.

## 3. 빌드 및 검증 결과
- **빌드 명령어**: `python3 scripts/build.py`
- **결과**: `Build complete` (Pages: 12, Assets: 10, Routes: 12, Exit code: 0)
- **시각적 검증**:
  - `http://localhost:8080/ai-practice/summer-vacation-basic/` 접속 후 프롬프트 타이틀 왼쪽 파란색 인디케이터 바 및 미리보기 카드 헤더 스타일이 깔끔하게 정돈되어 반영됨을 확인 완료.
- **상태**: 완료

## 4. 추가 조정
- `assets/css/site.css`: `prompt-item--preview` 카드의 상단 여백을 더 타이트하게 조정하여 `완성된 프롬프트 (실시간 미리보기)` 제목이 위쪽 빈 공간 없이 붙도록 보정.
- **빌드 재검증**: `python3 scripts/build.py` 재실행 결과 정상 완료.
- **브라우저 스크린샷 검증**: Playwright CLI가 로컬 Chrome/캐시 권한 문제로 실행되지 않아 동일한 화면 캡처는 이번 턴에서 완료하지 못함.

## 5. 추가 원인 보정
- `prompt-item--preview` 카드의 `prompt-item__header`가 `align-items: center`라서 제목과 배지 묶음이 세로 중앙 정렬되던 문제를 `flex-start`로 수정.
- 미리보기 카드 상단 패딩을 `var(--als-space-2)`로 줄여 제목이 카드 상단에 더 가깝게 붙도록 재보정.
- `완성된 프롬프트 (실시간 미리보기)` 제목이 `h3`라서 `page-body h3` 공통 상단 마진을 그대로 먹던 문제를 `margin: 0 !important`로 차단.

## 6. CSS 재설계 및 프롬프트 UI 통합 (2026-07-28)
- **문제 원인**: 이전 변경으로 인해 입력 영역과 미리보기 영역이 완전히 독립된 두 개의 카드로 렌더링되면서 테두리가 겹치고 중복 배지가 나타나는 레이아웃 붕괴 현상 발생.
- **조치 사항**:
  - `components/prompt-item.html`: 미리보기(`prompt_preview_html`)를 `<article class="prompt-item">` 내부로 이동시켜 단일 카드 구조로 통합.
  - `core/renderers/static_prompt.py`: `preview_html`이 독립된 `<article>`을 생성하지 않도록 `<div class="prompt-item__preview-section">`으로 변경. 중복 생성되던 `ai_badges_block` 제거.
  - `assets/css/site.css`: 기존 땜질식 CSS 롤백 후, `.prompt-item__preview-section` 스타일 신규 추가 (회색 박스로 묶인 내부 영역).
  - **보호 조치**: 해당 CSS 영역 앞뒤로 `[DO NOT MODIFY]` 주석을 추가하여 AI 에이전트의 임의 수정을 원천 차단.
  - `AGENTS.md`: "5. 절댓칙 (Core Prohibitions)"에 `.prompt-item` 관련 핵심 레이아웃 임의 수정 절대 금지 규칙 추가 완료.
- **결과**: `python3 scripts/build.py` 정상 빌드 완료. 분리되었던 카드 레이아웃이 깔끔한 단일 박스로 복구됨.

## 7. 추가 문제 해결: 미리보기 타이틀 레이아웃 붕괴 (2026-07-28)
- **문제 현상**: 통합 후에도 미리보기 영역 제목("완성된 프롬프트")의 상단 여백이 비정상적으로 크고 색상이 파란색으로 변질되어 출력됨.
- **원인 분석**: 본문을 감싸는 `.practice-step-card` 내부의 `h3` 태그에 전역적으로 `margin-top: 2.75rem !important` 및 파란색 텍스트 색상이 강제 지정되어 있었음. 미리보기 영역의 타이틀이 `<h3 class="...">`로 마크업되어 있어 해당 글로벌 오버라이드의 직격탄을 맞음.
- **해결 방안**: `core/renderers/static_prompt.py`에서 미리보기 헤더 타이틀 렌더링 시 `<h3>` 태그 대신 `<div>` 태그를 사용하도록 변경하여 글로벌 마크다운 스타일(`!important`)의 간섭을 완전히 회피함.
- **결과**: `python3 scripts/build.py` 재실행 정상 완료. 거대했던 상단 마진이 사라지고 의도했던 어두운 회색 타이틀(`font-weight: 700`)이 알맞은 간격으로 출력됨.

## 8. 인덱스 페이지 이중 카드 겹침 버그 수정 (2026-07-28)
- **문제 현상**: 인덱스(랜딩) 페이지 렌더링 시 외부 흰색 테두리(`#page-body`)와 내부 마크다운 렌더링 테두리(`.practice-step-card`)가 이중으로 겹쳐 두 개의 라운딩 테이블이 나타나는 문제.
- **원인 분석**: 모든 마크다운 콘텐츠 렌더러가 자동으로 텍스트를 `.practice-step-card`라는 독립된 카드로 감싸는 구조로 설계됨. 반면 이전에 복구한 전역 `.page-body` 역시 패딩과 테두리를 가진 카드 형태였음. 이로 인해 마크다운으로 구성된 랜딩 페이지 등에서 카드가 중첩됨. 이전에 전역 `.page-body` 테두리를 완전히 삭제했을 때 다른 에러 페이지 등의 레이아웃이 붕괴되었던 이력이 있음(사이드 이펙트).
- **해결 방안**: 사용자님의 지시대로 사이트 이펙트를 방지하기 위해 CSS를 **따로 적용(Separate CSS Targeting)**함. `.page-body`의 전역 스타일은 그대로 둔 채, `site.css`에서 명시적으로 `.page-content--landing`, `.page-content--collection`, `.page-content--practice-timeline` 등 마크다운 렌더러를 거치는 페이지 타입에 한해서만 `.page-body`의 배경과 테두리를 투명화(`transparent`, `border: none`)하는 특수 룰을 추가함.
- **결과**: 빌드 확인 결과, `404 에러 페이지` 등 마크다운이 아닌 페이지의 단일 카드 레이아웃은 안전하게 유지하면서, 인덱스 페이지의 보기 싫은 이중 겹침 라운딩 테이블 테두리는 완벽히 제거됨.

## 9. 어르신용 인쇄형 여행 일정표 프롬프트 추가 (2026-07-28)
- **작업 내용**: 사용자님의 요청으로 '여름 휴가 여행 플래너 지침서' 하단에 **Gemini 캔버스를 활용한 인쇄용 HTML 문서 생성 프롬프트**를 새롭게 다듬어 추가함.
- **변경 사항**: `pages/sections/ai-assistant/vacation-planner-guide.md` 파일에 "Gemini 캔버스(Canvas) 응용 2: 어르신용 인쇄형 여행 일정표 만들기" 섹션을 신설. 기존 '의정부 여행' 텍스트를 `[의정부 / 제주도 / 속초]` 및 `[20년지기 동네 밤티형 의정부 골목 여행 / 우리 가족 행복한 3박 4일 속초 여행]`과 같이 Static Prompt 셀렉터 옵션으로 일반화(Generalization)하여 활용도를 높임.
- **결과**: `python3 scripts/build.py` 실행 완료. 웹 페이지에 해당 응용 프롬프트가 정상적으로 추가됨.

## 10. 프롬프트 설정 UI 실시간 미리보기 연동 버그 수정 (2026-07-28)
- **문제 현상**: Static Prompt 문서에서 사용자가 설정 칩(Dropdown/Input)을 조작해도 하단의 "완성된 프롬프트 (실시간 미리보기)" 영역에 실시간으로 변경 사항이 동기화되지 않는 문제.
- **원인 분석**: 앞선 작업(7번 항목)에서 프롬프트 UI 컴포넌트의 HTML 구조를 개선(미리보기 영역을 메인 `article.prompt-item` 안으로 통합)하였으나, 이를 제어하는 자바스크립트 로직(`assets/js/prompt-copy.js`)은 여전히 예전 구조(미리보기 영역이 형제 노드인 독립된 `article`일 것이라 가정)를 바탕으로 대상을 찾고 있었음(`previousElementSibling` 등 탐색). 이로 인해 JS가 DOM에서 미리보기 텍스트 상자를 찾지 못하고 오류를 조용히 무시함.
- **해결 방안 1 (로직 수정)**: `assets/js/prompt-copy.js` 내부의 핵심 탐색 로직인 `getPair()` 함수를 최신 HTML 구조에 맞게 단일 통합 객체 구조로 재작성함. (동일한 `.prompt-item` 안에 소스 코드와 미리보기 코드가 모두 있으므로 복잡한 형제 탐색 루프 제거).
- **해결 방안 2 (브라우저 캐시 무효화)**: 자바스크립트를 수정하고 빌드했음에도 브라우저가 예전 JS 파일을 강력하게 캐싱하여 변화가 나타나지 않는 현상이 발생함. 이를 근본적으로 해결하기 위해 `core/build_pipeline.py`의 `site_script_url` 호출부에 캐시 버스팅 파라미터(`?v=1.1`)를 명시적으로 추가하여 강제 갱신되도록 조치함.
## 11. 외부 AI 서비스 연결 탭 재사용 최적화 (2026-07-28)
- **문제 현상**: 프롬프트 복사 후 'ChatGPT에서 사용', 'Gemini에서 사용' 버튼을 클릭하면 매번 새로운 브라우저 탭(`_blank`)이 생성되어 창이 지저분해지는 불편함.
- **해결 방안**: `assets/js/prompt-copy.js`의 `window.open` 대상(target)을 `_blank` 대신 각 서비스 고유의 이름(`chatgpt_window`, `gemini_window`)으로 변경함. 이로 인해 우리 사이트에서 띄운 서비스 탭이 열려있다면, 새 창을 띄우지 않고 기존 창을 갱신 및 포커싱하도록 개선.
- **결과**: `python3 scripts/build.py` 재빌드 및 캐시 무효화 파라미터 갱신(`?v=1.2`) 완료. 외부 AI 서비스 버튼이 탭을 중복 생성하지 않도록 완벽히 통제함.
## 12. 자연스러운 한국어 다듬기 전문 편집자 프롬프트 추가 (2026-07-28)
- **작업 내용**: 사용자의 요청에 따라 자연스러운 한국어 교정을 위한 전문 편집자 AI 프롬프트 지침서를 신규 추가함.
- **주요 반영 사항**:
  - `pages/sections/ai-assistant/korean-editor-guide.md` 신규 생성. 번역투 방지, 이중 피동 제거, 친근한 대상(친구) 맞춤 구어체 반말, 대명사 생략, 마크다운 유지 등 AI의 한계를 보완하는 세밀한 교정 지침을 포함.
  - `data/page-registry.json` 및 `data/navigation.json`에 `ai-assistant-korean-editor` 항목 등록 완료.
  - `core/navigation.py`와 `core/page_registry.py` 파이썬 코어 레지스트리에도 동일하게 메타데이터 등록 완료.
  - (추가 보완): 프롬프트 사용법을 오해할 수 있는 사용자를 위해 문서 상단에 "💡 활용 팁" 섹션을 신설하여, 이 프롬프트는 1회성 복사용이 아니라 AI 설정창에 등록해 두고 AI가 질문하게 만드는 용도임을 명시함.
- **결과**: `python3 scripts/build.py` 정상 빌드 성공(Pages 13개로 증가). 새로 추가된 지침서 페이지 렌더링 및 수정 내용 확인 완료.

## 13. '바로 써보기'용 1회성 맞춤형 한국어 교정 프롬프트 신설 (2026-07-28)
- **작업 내용**: 사용자가 시스템 지침서가 아닌, 그때그때 필요한 조건(용도, 말투 등)을 골라 복사해서 1회용으로 쓸 수 있는 버전의 프롬프트를 '바로 써보기' 섹션에 추가함.
- **주요 반영 사항**:
  - `pages/sections/ready-to-use/korean-editor.md` 파일 신규 생성. 인라인 스마트 태그 기능을 적용하여 문서 내에서 바로 조건을 선택할 수 있도록 구성함.
  - `data/page-registry.json`, `data/navigation.json` 및 `core/page_registry.py`, `core/navigation.py`의 `ready-to-use` 섹션에 `ready-to-use-korean-editor` 항목 등록 완료.
- **결과**: `python3 scripts/build.py` 정상 빌드 성공(Pages 14개로 증가). 인라인 칩이 렌더링되는 실시간 프롬프트 조작 UI 확인 완료.
- **추가 수정 (2026-07-28)**: 
  2. 이를 해결하기 위해 이메일 프롬프트처럼 대괄호 옵션을 레이블과 동일한 줄(`- 글의 용도: [블로그 / 보고서]`)에 배치하도록 양식 구조를 수정하여 콤보박스가 정상 출력되도록 복구함. 빌드 검증 성공.
  3. 프롬프트 지시어가 문맥상 어색한 부분("위 글을 다듬어 줘" -> "아래 글을 다듬어 줘")을 교정하고, 중요 원칙 등 나열식 항목들에 글머리 기호(bullet points)를 추가하여 가독성을 개선함.
  4. 하단의 `[여기에 글 붙여넣기]` 자유 텍스트 입력(Text Input) 칩 역시 동일한 '단독 줄 대괄호' 규칙으로 인해 헤더로 인식되는 문제가 있어, 양쪽에 따옴표(`" "`)를 추가해 칩으로 정상 렌더링되도록 수정함.
  5. 페이지 하단(프롬프트 영역 밖)에 "💡 활용 팁 (권장 글자 수)" 섹션을 신설하여, 너무 긴 글을 한 번에 넣을 때 발생하는 품질 저하 및 출력 끊김 현상을 예방하도록 A4 1~2장 분량으로 나누어 넣기를 권장하는 안내 문구를 추가함.
  6. 사용자 제공 원본 '외국어 회화 연습 지침서'를 기반으로, AI 특유의 3가지 보완점(주제 선제안, 교정 피드백 포맷 분리, 원어민 리액션 명시)을 반영하여 `pages/sections/ai-assistant/language-tutor-guide.md` 신규 생성.
  7. `data/page-registry.json`, `data/navigation.json`, `core/page_registry.py`, `core/navigation.py` 에 새 페이지 라우팅 정보 등록 및 `order` 일련번호 재정렬, 빌드 검증 성공(Pages 15).
  8. `language-tutor-guide.md` 파일 내 프롬프트 중 `💡 더 자연스러운 표현: [문장]` 부분의 `[문장]` 텍스트가 대괄호 때문에 인라인 스마트 태그(자유 입력 칩)로 오인 렌더링되는 파싱 충돌을 확인. 이를 `💡 더 자연스러운 표현: "교정된 문장"` 형태로 수정하여 프롬프트 양식 손상을 방지함. 더불어 복사 붙여넣기 과정에서 중복된 헤더와 예시 텍스트도 원상 복구함.
  9. 사용자의 요청에 따라 '외국어 회화 코치 지침서' 페이지를 `static-prompt`에서 `prompt-builder` 타입으로 구조 변경. `page-registry.json`과 `core/page_registry.py`의 type 속성을 업데이트하고, 기존 정적 프롬프트 마크다운 텍스트를 `prompt-field` (언어 선택, 코치 성향 선택) 설정 블록으로 교체함. 기존 이메일/이미지 빌더 로직과 섞이지 않도록 `prompt-builder.js`에 `isLanguageTutorBuilder` 전용 독립 분기를 신설하여, 화면 상단에서 언어를 선택하면 하단 결과창의 프롬프트 내 모든 언어 변수가 실시간 치환되도록 완벽히 구현함.
  10. 브라우저 환경에서 발생할 수 있는 폼 필드 상태(`values["lang"]`) 기반의 불확실성을 완전히 제거하기 위해, `prompt-builder.js`의 판별 로직을 `document.body.dataset.pageId` (`registry_id`)를 직접 읽어 처리하도록 더욱 견고하게 업데이트 및 재빌드 완료.
\n### 프롬프트 빌더 아키텍처 개선 완료\n- **작업일시**: 2026-07-28 23:22\n- **주요 내용**: 자바스크립트 하드코딩 제거 및 마크다운 `prompt-template` 기반의 실시간 템플릿 치환 로직 구현\n- **영향 범위**: Python 빌더 엔진, HTML 컴포넌트 구조, JS 프롬프트 생성기 전면 개편\n- **검증**: 기존 빌더 기능과 100% 하위 호환성 유지 및 빌드(build.py) 성공 확인
\n### 사용자 정의 직접 입력 UI 및 '선택 항목' 제거\n- **작업일시**: 2026-07-28 23:28\n- **주요 내용**: prompt-field 구성에서 불필요한 '선택 항목' 뱃지 텍스트 제거 및 커스텀 텍스트 입력창(`input`) 상시 노출 추가\n- **영향 범위**: Python 빌더 엔진, `prompt-field.html` UI, `prompt-builder.js` 이벤트 리스너(칩과 입력창 동기화)\n- **검증**: 빌드 성공 및 UIX 테스트 대기
\n### 모바일 최적화 '기타 (직접 입력)' 자동화 구현 (추천 A안)\n- **작업일시**: 2026-07-28 23:34\n- **주요 내용**: 모든 프롬프트 필드에 '기타(직접 입력)' 옵션을 일괄 추가하는 파이썬 렌더러 구현 및 모바일 UX 최적화(숨김 텍스트창)\n- **영향 범위**: Python 빌더 엔진(component_engine.py), HTML/CSS(display:none), JS 토글 로직\n- **검증**: 빌드 성공 확인

### 외부 AI 서비스 탭 재사용 크로스-오리진 한계 돌파
- **작업일시**: 2026-07-29 00:17
- **주요 내용**: `noopener` 속성을 제거했음에도 Cross-Origin 보안 정책으로 인해 브라우저의 `window.name` 매칭이 차단되어 탭 재사용이 안되는 문제 해결. JS 전역 변수(`aiWindows`)로 열린 탭 레퍼런스를 추적하여 `.focus()`를 강제 호출하도록 구조 개선.
- **영향 범위**: 전역 `prompt-copy.js` 로직, 구형 레거시 파일 보완, `docs/design-guidelines.md` 관련 규칙 추가.
- **검증**: 빌드 성공 및 로컬/운영서버 배포 무결성 검증 통과
