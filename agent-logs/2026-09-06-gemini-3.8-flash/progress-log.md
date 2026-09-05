# 작업 진행 로그 (2026-09-06)

## 1. 작업 개요
- **작업명**: AI Learning Studio 4대 핵심 보완 과제 구현
  1. JavaScript 캐시 갱신 정책 하위 모듈 전파 및 번들 결합 해시 반영
  2. 드롭다운 닫기 시 키보드 포커스 복원 (`prompt-copy.js`)
  3. CI 워크플로 브라우저 스모크 테스트 추가 (`tests/test_browser_smoke.py`, `.github/workflows/quality-check.yml`)
  4. 콘텐츠 가이드라인 문서 구조 현행화 (`docs/content-guidelines.md`)
- **모델**: Gemini 3.8 Flash (High)
- **위험도**: 고위험 (High) (배포 헤더, 빌드 파이프라인, CI 워크플로, 클라이언트 공통 스크립트 전반)
- **승인 상태**: 사용자 명시적 승인 완료 (`go`)

---

## 2. 세부 변경 내역

### 1) JavaScript 캐시 갱신 개선
- **`vercel.json`**:
  - `/assets/js/(.*)` 경로에 `Cache-Control: public, max-age=0, must-revalidate` 헤더 추가 (Vercel에서 JS 모듈의 ETag 304 조건부 재검증 강제, 캐시 고착 방지).
- **`core/build_pipeline.py`**:
  - `calculate_assets_bundle_hash(dir_path, pattern="*.js")` 신규 구현.
  - `assets/js/` 내 모든 `.js` 파일의 콘텐츠를 결합하여 해시를 산출하도록 `site_js_hash` 계산 로직 개선. 하위 모듈(`prompt-copy.js` 등)만 변경되어도 `site.js?v=...` 쿼리 해시가 자동 갱신됨.
- **`tests/test_build_pipeline.py`**:
  - `test_calculate_assets_bundle_hash` 단위 테스트 추가.

### 2) 드롭다운 닫기 시 키보드 포커스 복원 (접근성)
- **`assets/js/prompt-copy.js`**:
  - `activeDropdownChip` 변수를 통해 드롭다운을 연 칩 엘리먼트 추적.
  - `closeDropdown({ restoreFocus = false } = {})`로 포커스 복원 매개변수화.
  - `Escape` 키 입력 시 및 `applyValue` 시 `{ restoreFocus: true }`로 원래 칩에 `.focus()` 복원.
  - 바깥 영역 마우스 클릭(`mousedown`) 시에는 `{ restoreFocus: false }`로 사용자가 클릭한 대상의 포커스 유지.
  - 키보드 접근성(WCAG 2.2) 준수를 위해 `.itc` 칩 포커스 상태에서 `Enter` / `Space` 키 입력 시 드롭다운이 열리도록 핸들러 보강.

### 3) CI 브라우저 스모크 테스트 추가
- **`tests/test_browser_smoke.py`**:
  - Python Playwright 기반 브라우저 3대 시나리오 스모크 테스트 작성:
    1. 프롬프트 인라인 칩 옵션 선택 → 실시간 미리보기 코드 동기화 → 클립보드 복사 검증
    2. 드롭다운 오픈 후 `Escape` 키 입력 시 원래 칩(`.itc`)으로 포커스 복원 검증
    3. 모바일 뷰포트(375px)에서 햄버거 토글 버튼 클릭 시 `aria-expanded` 및 `data-navigation-state="open"` / 재클릭 시 `"closed"` 상태 전환 검증
  - Playwright 미설치 로컬 환경에서는 `@unittest.skipUnless`로 안전하게 스킵되어 기존 로컬 개발 환경 오염 방지.
- **`.github/workflows/quality-check.yml`**:
  - CI 파이프라인에 `playwright` 및 Chromium 설치, `python3 -m unittest tests/test_browser_smoke.py` 실행 단계 추가.
- **`requirements-dev.txt`**:
  - `playwright>=1.40.0` 개발 의존성 명시.

### 4) 필수 정책 문서 현행화
- **`docs/content-guidelines.md`**:
  - 레거시/가상의 파일 구조(`menu.json`, `pages.json`, `pages/<slug>/page.json`)를 현행 저장소 실제 구조(`navigation.json`, `page-registry.json`, `pages/index.md`, `pages/sections/**/*.md`, 템플릿 컴포넌트)로 갱신.
  - 오탈자("사이트 전깃 기본 메타정보" 등) 수정.

---

## 3. 검증 결과
- **코드 린트 (`ruff check core scripts tests`)**:
  - `All checks passed!` (Exit code 0)
- **단위 테스트 (`python3 -m unittest discover -s tests`)**:
  - `Ran 89 tests in 2.179s, OK (skipped=3)` (Exit code 0)
  - 기존 85개 테스트 통과 + 신규 `calculate_assets_bundle_hash` 테스트 통과 + 브라우저 스모크 테스트 3건은 로컬 환경에서 안전하게 skip
- **프롬프트 감사 (`scripts/audit_prompts.py --strict`)**:
  - `[*] Audited 77 markdown pages and 50 image assets. [OK] All prompt audits passed successfully!` (Exit code 0)
- **정적 빌드 및 체크 (`scripts/build.py`, `scripts/build.py --check`)**:
  - `Build complete. Pages: 77, Assets: 60, Routes: 77` (Exit code 0)
  - `dist/index.html` 내 `site.js?v=20acddd0`로 하위 모듈 변경 사항이 반영된 결합 해시 주입 확인 완료.

---

## 4. 최종 판정
- 상태: **단일 세션 보상 검증 완료 (Self Compensatory PASS)**
