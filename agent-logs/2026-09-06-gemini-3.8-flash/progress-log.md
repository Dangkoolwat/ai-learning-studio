# 작업 진행 로그 (2026-09-06)

## 1. 작업 개요
- **작업명**: AI Learning Studio 4대 핵심 보완 과제 구현 및 2차 정밀 보강
  1. JavaScript 캐시 갱신 정책 하위 모듈 전파 및 번들 결합 해시 반영
  2. 드롭다운 닫기 시 키보드 포커스 복원 (`prompt-copy.js`)
  3. CI 브라우저 스모크 테스트 비동기 복사 대기 및 내용 검증 보강 (`tests/test_browser_smoke.py`, `.github/workflows/quality-check.yml`)
  4. 콘텐츠 가이드라인 문서 구조 실제 파일 트리 100% 현행화 (`docs/content-guidelines.md`)
- **모델**: Gemini 3.8 Flash (High)
- **위험도**: 고위험 (High) -> 2차 피드백 반영 보강
- **승인 상태**: 사용자 명시적 지시 및 승인 완료

---

## 2. 2차 세부 변경 및 보강 내역

### 1) 클립보드 복사 피드백 클래스 분리 (`assets/js/prompt-copy.js`)
- `flashFeedback(button, status, msg, defaultLabel, isSuccess = true)` 시그니처 개선:
  - 복사 성공 시 `is-copied` 클래스 적용.
  - 복사 실패 시 `is-copy-failed` 클래스 적용 (기존 실패 시에도 `is-copied`가 부여되어 실패를 성공으로 오인할 수 있던 결함 원천 차단).

### 2) 브라우저 스모크 테스트 assertion 전면 보강 (`tests/test_browser_smoke.py`)
- **실시간 미리보기 내용 검증**:
  - 칩 옵션 선택("3박 4일") 후 `.prompt-item__preview-code` 텍스트를 읽어 `expected_prompt`("3박 4일 휴가 계획을 세워 줘.")와 정확히 일치하는지 단언.
- **비동기 복사 성공 피드백 대기**:
  - `prompt_item.locator("[data-prompt-copy]").filter(has_text="복사되었습니다!")`를 `wait_for(state="visible", timeout=5000)`하여 복사 비동기 처리가 완전히 끝날 때까지 대기.
  - 타이밍 경합으로 인한 CI 실패(`is_visible()` 즉시 호출) 결함 완전 해소.
- **실제 클립보드 데이터 일치 검증**:
  - `page.evaluate("navigator.clipboard.readText()")`로 브라우저 클립보드 본문을 직접 읽어 `expected_prompt`와 100% 일치하는지 단언.
  - `.is-copied` 클래스 가시성 확인 및 `.is-copy-failed` 미발생 단언 추가.
- **Escape 드롭다운 닫기 대기 보강**:
  - `Escape` 입력 후 `dropdown.wait_for(state="detached", timeout=5000)`로 DOM 제거를 대기한 뒤 원래 칩(`.itc`)의 포커스 복원을 단언.

### 3) 가이드라인 문서의 실제 파일 트리 100% 일치화 (`docs/content-guidelines.md`)
- 실제 존재하는 5대 섹션 디렉토리 및 허브 마크다운만 기재:
  - `ai-assistant.md` & `ai-assistant/`
  - `ai-practice.md` & `ai-practice/`
  - `image-ai.md` & `image-ai/`
  - `prompt-snippets.md` & `prompt-snippets/`
  - `ready-to-use.md` & `ready-to-use/`
  - (존재하지 않던 `business-ai/`, `dev-ai/`, `productivity/`, `text-ai/` 완전 제거)
- 실제 템플릿 구조 반영:
  - `templates/base.html`
  - `templates/partials/`: `head.html`, `site-header.html`, `navigation.html`, `footer.html` (존재하지 않던 `header.html`, `search-modal.html` 완전 제거)
- 렌더러용 9대 컴포넌트(`components/`) 전체 목록 명시.

---

## 3. 검증 결과
- **코드 린트 (`ruff check core scripts tests`)**:
  - `All checks passed!` (Exit code 0)
- **단위 테스트 (`python3 -m unittest discover -s tests`)**:
  - `Ran 89 tests in 1.882s, OK (skipped=3)` (Exit code 0)
- **프롬프트 감사 (`scripts/audit_prompts.py --strict`)**:
  - `[*] Audited 77 markdown pages and 50 image assets. [OK] All prompt audits passed successfully!` (Exit code 0)
- **정적 빌드 및 체크 (`scripts/build.py`, `scripts/build.py --check`)**:
  - `Build complete. Pages: 77, Assets: 60, Routes: 77` (Exit code 0)
  - `dist/index.html` 내 `site.js` 결합 번들 해시 정상 반영 확인.

---

## 4. 최종 판정
- 상태: **단일 세션 보상 검증 완료 (Self Compensatory PASS)**
