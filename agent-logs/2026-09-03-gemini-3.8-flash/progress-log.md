# Task Progress Log (2026-09-03)

## 1. Task Objective
- **P0 긴급 과제**:
  - 플랫폼 중립적 사이트맵 절대 URL 및 소셜 메타태그(OG/Twitter) 정상화
  - 배포 시 기존 캐시 무효화 및 새 페이지 보장을 위한 정적 자산(CSS/JS) 해시 캐시 버스팅(Cache-Busting) 자동화
- **P1 중요 과제**:
  - `docs/seo-guidelines.md` 계약 준수를 위한 Schema.org JSON-LD(`WebSite`, `BreadcrumbList`, `LearningResource`) 구조화 데이터 자동 생성
  - 웹 접근성(WCAG 2.2) 보완: 모바일 드로어 및 도움말 모달 키보드 포커스 트랩 + 초점 복원, 프롬프트 빌더 복사 시 `aria-live` 음성 피드백 보강, 이미지 라이트박스 키보드(Enter/Space) 조작 및 초점 복구 지원
- **P2 및 잔여 최적화 과제**:
  - 사이드바 실시간 검색 0건(Empty State) 시 "일치하는 메뉴가 없습니다." 피드백 표시
  - 사이드바 검색어 일치 텍스트 실시간 하이라이팅(`<mark class="search-highlight">`) 구현
  - 소셜 공유 전용 1200x630 고해상도 대표 배너 에셋(`assets/images/og-cover.png`) 생성 및 `summary_large_image` 연동
  - `vercel.json`에 현대적 Content-Security-Policy (CSP) 보안 헤더 적용
  - `docs/seo-guidelines.md` 및 `docs/deployment-guidelines.md` 공식 규격 동기화

## 2. Execution Checklist
- [x] **[P0]** `core/build_pipeline.py`에 플랫폼 중립적 `resolve_site_base_url` 및 `build_social_meta_html` 구현
- [x] **[P0]** `scripts/build.py`에 `--site-url` CLI 파라미터 추가 및 파이프라인 연동
- [x] **[P0]** `core/build_pipeline.py`에 `calculate_asset_hash` 구현 및 CSS/JS URL에 `?v=[hash]` 자동 주입
- [x] **[P1-A]** `core/build_pipeline.py`에 `build_json_ld_script_html` 구현 및 템플릿/검증 파이프라인 연동
- [x] **[P1-A]** `core/template_models.py`, `core/template_engine.py`, `templates/partials/head.html`에 `{{ json_ld_script_html }}` 통합
- [x] **[P1-B]** `assets/js/image-lightbox.js`: 이미지에 `tabindex="0"`, `role="button"`, `Enter`/`Space` 키보드 인터랙션 및 모달 닫힘 시 초점 복구 구현
- [x] **[P1-B]** `assets/js/prompt-builder.js` & `components/prompt-builder.html`: 도움말 팝업 포커스 트랩/복구 및 클립보드 복사 시 `aria-live="polite"` 음성 알림 구현
- [x] **[P1-B]** `assets/js/navigation.js`: 모바일 네비게이션 드로어 키보드 포커스 트랩(`Tab`/`Shift+Tab`) 및 닫힘 시 토글 버튼 초점 복구 구현
- [x] **[P2]** `assets/js/navigation.js` & `assets/css/site.css`: 검색 결과 0건 안내(`.site-nav-search__empty`) 구현
- [x] **[P2]** `vercel.json`: Content-Security-Policy (CSP) 헤더 추가
- [x] **[추가과제 1]** `assets/images/og-cover.png`: 1200x630 대표 썸네일 배너 생성 및 `summary_large_image` 메타태그 연동
- [x] **[추가과제 2]** `assets/js/navigation.js` & `assets/css/site.css`: 실시간 검색어 텍스트 하이라이트(`.search-highlight`) 구현
- [x] **[추가과제 3]** `docs/seo-guidelines.md` & `docs/deployment-guidelines.md`: 베이스 URL 감지, 캐시 버스팅, JSON-LD 스펙 공식 문서화
- [x] **[검증]** `.venv/bin/pytest` 81개 테스트 전체 통과 (Ran 81 tests, OK)
- [x] **[검증]** `.venv/bin/ruff check core scripts tests` All checks passed (린트 100% 클린)
- [x] **[검증]** `python3 scripts/audit_prompts.py --strict` 75개 페이지 및 44개 에셋 검사 통과
- [x] **[검증]** `python3 scripts/build.py` 75개 페이지 정적 출판 무결성 검증
- [x] **[검증]** `python3 scripts/build.py --check` 드라이런 검증 통과

## 3. Verification Results
- **단위 테스트**: `Ran 81 tests in 2.01s, OK` (모든 기존 및 신규 테스트 100% 통과)
- **린터 검사**: `ruff check core scripts tests` -> `All checks passed!`
- **프롬프트 무결성 감사**: `audit_prompts.py --strict` -> `All prompt audits passed successfully!`
- **빌드 검증**: `dist/` 출판 완료, `build-manifest.json` 내 `release_readiness_status: ready` 확인
- **자산 캐시 검증**: `site.css` 수정 시 해시값이 즉시 자동 갱신되어 배포 즉시 브라우저 캐시 무효화 보장
- **소셜 메타데이터 검증**: 카카오톡/페이스북/트위터용 1200x630 `og-cover.png`와 `summary_large_image` 태그 완벽 렌더링 확인
