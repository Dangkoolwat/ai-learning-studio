# 자기 개발 학습 계획 프롬프트 추가 작업 로그

## 1. 작업 개요
- **목적**: 자기 개발 학습 계획 프롬프트를 사이트의 `ready-to-use` 섹션에 등록
- **프롬프트 특징**: 선택지 및 자유 텍스트를 인라인으로 입력할 수 있는 스마트 콤보박스 적용 (`static-prompt` 형식)

## 2. 변경 내역
1. **신규 마크다운 페이지 생성**
   - 파일: `pages/sections/ready-to-use/self-development.md`
   - 내용: `[직장인 / 학생 / 프리랜서]` 및 `"[공부하고 싶은 분야]"` 등 프로젝트 가이드라인에 따른 옵션 선택 및 자유 입력 형식 반영
2. **페이지 레지스트리 수정 (`data/page-registry.json`)**
   - `ready-to-use-self-development` 페이지 객체 추가
3. **내비게이션 등록 (`data/navigation.json`)**
   - `ready-to-use` 카테고리 메뉴 목록에 라우트 추가
4. **Python 빌드 스크립트 계약 검증 갱신**
   - 파일: `core/navigation.py`, `core/page_registry.py`
   - 수정 이유: `EXPECTED_SECTIONS`와 `EXPECTED_PAGES` 하드코딩된 검증 목록에 새 페이지를 추가하여 계약 테스트(Contract Test)를 통과하도록 수정

## 3. 검증 결과
- **검증 스크립트**: `python3 scripts/build.py`
- **결과**: `Build complete. Pages: 16, Assets: 10, Routes: 16`
- **사이드 이펙트 체크**: 레이아웃 변경이 아닌 신규 마크다운 페이지 추가이므로 기존 공통 컴포넌트나 UI 여백의 부작용은 없음.

## 4. 후속 사항
- 추가적인 배포(deploy) 없이 작업 완료. Handoff 필요 없음.

## 5. CSS 레이아웃 (Line-height) 추가 수정
- **목적**: 인라인 칩이 포함된 프롬프트 영역의 상하 여백 확보
- **수정 대상**: `assets/css/site.css`
- **변경점**: `.prompt-item__content code`의 `line-height` 값을 `var(--als-line-height-relaxed)`에서 `2.2`로 변경하여 시각적 답답함 해소
- **검증**: 빌드(`python3 scripts/build.py`) 완료

## 6. 프롬프트 블록 레이아웃 (Margin-top) 개선
- **목적**: 마크다운 텍스트와 하단 프롬프트 박스(.prompt-item) 간의 상하 간격(숨통) 확보
- **수정 대상**: `assets/css/site.css`
- **변경점**: `.prompt-item` 선택자에 `margin-top: var(--als-space-8)`를 추가하여 마크다운 본문과 겹쳐 보이는 문제 및 타임라인형 프롬프트 실습 페이지의 가독성 개선
- **검증**: 빌드(`python3 scripts/build.py`) 완료

## 7. '현실적인 자기계발 코치 지침서' 추가
- **목적**: 사용자가 제시한 자기계발 코치 지침서와 AI 제어 피드백(Stop 조건 등)을 반영하여 신규 가이드라인 추가
- **신규 파일**: `pages/sections/ai-assistant/self-development-coach.md`
- **변경점**: 네비게이션 및 페이지 레지스트리에 항목 추가 및 하드코딩된 EXPECTED_PAGES 정합성 통과 작업 진행
- **검증**: 빌드(`python3 scripts/build.py`) 완료
## [2026-07-29] UI 라운딩 박스 가로 스크롤 이슈 수정
- **수정 파일**: `assets/css/site.css`, `data/page-registry.json`, `core/page_registry.py`, `pages/sections/ai-assistant/self-development-coach.md`
- **수정 내용**:
  - `site.css`의 `.prompt-item__content` 및 `.prompt-item__preview-box` 등 프롬프트 관련 텍스트 박스에 `word-break: break-all;` 및 `overflow-wrap: anywhere;`를 추가하여 한국어 문장이 박스 밖으로 넘어가지 않고 자동 줄바꿈되도록 강제 수정. (가로 스크롤 제거 목적)
  - `page-registry.json`과 마크다운의 `title` 필드를 `현실적인 자기계발 코치 지침서`로 통일시켜 빌드 시 발생하는 Validation Error 해결.
- **검증**: `python3 scripts/build.py` 정상 통과 확인.

## [2026-07-29] 사이드 이펙트 롤백 및 마크다운 구문 오류 수정 (근본 원인 해결)
- **수정 파일**: `assets/css/site.css` (롤백), `pages/sections/ai-assistant/self-development-coach.md` (수정)
- **수정 내용**:
  - 이전 작업에서 `.prompt-item__content`에 글로벌 CSS 속성을 추가하여 가로 스크롤을 막으려 했으나, 다른 페이지 프롬프트에 사이드 이펙트 우려가 있다는 사용자 피드백 접수.
  - 근본 원인 파악 결과: CSS 문제가 아니라, `self-development-coach.md`에서 프롬프트 구역 선언 시 백틱 4개(` ````prompt `)를 사용하고 `title/description/---` 형식을 생략하여, 자체 파서가 아닌 일반 마크다운 `<pre>` 코드 블록으로 잘못 렌더링된 것이 원인(파란색 세로줄 및 스크롤바 발생 원인)이었음.
  - `site.css`에 추가했던 코드를 원복(Rollback)하여 사이드 이펙트 제거.
  - `self-development-coach.md`의 프롬프트 구역을 정상적인 3개 백틱(` ```prompt `)과 필수 헤더(`title`, `description`, `---`)를 포함하는 포맷으로 수정 완료. 이제 정상적인 라운딩 박스 컴포넌트로 렌더링됨.
- **검증**: `python3 scripts/build.py` 실행 완료.
