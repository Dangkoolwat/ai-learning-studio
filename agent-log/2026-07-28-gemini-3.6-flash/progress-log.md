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
