# AI Learning Studio 작업 로그 (2026-08-23)

## 작업 개요
7대 핵심 미비점, 후속 5종 미비점, 4종 권장사항 및 `requirements-dev.txt` 개발 환경 구축, 로컬 가상환경(`.venv`) 기반 Ruff 실제 검증(0 errors) 완료.

---

## 세부 수정 내역

1. **개발 의존성 명시 및 개발 가이드 보강 (`requirements-dev.txt`, `README.md`)**
   - `requirements-dev.txt` 생성: `ruff>=0.9.0`, `pytest>=8.0.0`
   - `README.md`: 가상환경 설정, `ruff check`, `pytest`/`unittest` 실행 가이드 추가

2. **로컬 실제 Ruff 린트 무결성 검증 (`.venv/bin/ruff check`)**
   - 로컬 가상환경(`.venv`) 생성 후 `pip install -r requirements-dev.txt` 완료
   - `ruff check core scripts tests` 실실행 결과: **All checks passed (0 errors)** 확인

3. **CI 파이프라인 및 PR 트리거 연동 (`.github/workflows/quality-check.yml`)**
   - `pull_request: branches: [main]` 트리거 추가
   - `pip install ruff` 및 `ruff check core scripts tests` 린트 단계 추가
   - `python3 -m unittest discover -s tests` 실행 단계 추가

4. **클립보드 복사 실패 피드백 버그 수정 (`assets/js/prompt-copy.js`, `assets/js/prompt-builder.js`)**
   - 복사 실패 분기 시 "복사 실패" 텍스트 및 "is-error" 상태 클래스 부여 분기 정상화

5. **코어 엔진 단위 테스트 스위트 전면 확충 (`tests/`)**
   - `tests/test_theme_engine.py`: 테마 파싱, 레지스트리 빌드, CSS 에셋 생성 검증
   - `tests/test_template_engine.py`: 템플릿 로딩, 본문 클래스 빌더, 상대 경로 해석, 변수 치환 검증
   - `tests/test_component_engine.py`: 컴포넌트 레지스트리 무결성, PageIntro, PromptItem, PromptBuilder 렌더링 검증
   - `tests/test_page_renderers.py`: 5개 렌더러(`static-prompt`, `prompt-builder`, `practice-timeline`, `markdown-prompt`, `landing`) 디스패치 및 렌더링 검증
   - `tests/test_build_pipeline.py`: 마크다운 변환, 소스 탐색, 에셋 검증, sitemap/robots 생성 검증
   - 단위 테스트 스위트: 기존 44개 -> **총 64개 테스트로 대폭 확장** 및 100% 통과

6. **Data First 원칙 준수 및 아키텍처 리팩토링 (`assets/js/prompt-builder.js`)**
   - JS 내부에 하드코딩되어 있던 ~150줄의 한국어 프롬프트 템플릿 및 `pageId` 분기 제거
   - 마크다운/HTML의 `<template id="prompt-builder-template">` 기반 순수 렌더러로 완전 통일

7. **문서 및 버전 동기화 (`PROJECT.md`, `README.md`, `.python-version`)**
   - `PROJECT.md`의 디렉터리 트리 최신화 및 9장 데이터 계약에 `navigation.json`과 `page-registry.json`의 실제 스키마 필드 명세 반영
   - `README.md`의 Python 배지를 3.12로 일치화
   - `.python-version` 파일 생성 (Python 3.12 핀)

8. **레거시 잔재 및 린트 코드 무결성 정리**
   - 일회성 마이그레이션 스크립트 `scripts/rename_spice_to_spoon.py` 삭제
   - 레거시 디렉터리 `docs/legacy/` 삭제
   - 빈 `css/` 디렉터리 삭제
   - 저장소 내 `.DS_Store` 13개 일괄 삭제
   - `assets/js/navigation.js` 및 `assets/js/theme-toggle.js`의 빈 catch 블록에 안전한 주석 및 설명 명시
   - `core/renderers/static_prompt.py`, `core/renderers/markdown_prompt.py`의 미완성 중복 함수 잔재 및 미사용 변수/import 정리

9. **Vercel 캐시 및 보안 헤더 최적화 (`vercel.json`)**
   - `/assets/(.*)` 캐시 헤더에서 `immutable` 제거 및 `public, max-age=86400, stale-while-revalidate=86400` 적용
   - `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload` (HSTS) 추가
   - 웹 보안 헤더(`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`) 완비

---

## 최종 검증 결과
- **Ruff 린트 로컬 실실행**: `.venv/bin/ruff check core scripts tests` -> **All checks passed! (0 errors)**
- **단위 테스트 (pytest & unittest)**: `.venv/bin/pytest` -> **64 passed in 1.46s (100% OK)**
- **정적 빌드 검증**: `python3 scripts/build.py && python3 scripts/build.py --check` -> **59개 페이지 정상 생성 및 16개 검증 단계 전체 통과**
