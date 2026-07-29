# AGENTS.md 슬림화 및 모듈화 작업 로그

- **작성일**: 2026-07-22
- **작업자**: Gemini 3.6 Flash (Senior Architect)
- **목적**: 728줄의 비대한 `AGENTS.md`를 얇은 라우터로 전환하고 세부 지침을 `docs/` 이하 파일로 분리하여 토큰 절감 및 모듈화 달성.

## 1. 진행 상황 (Progress)
- [x] 다이어트 계획 수립 및 사용자 승인 완료
- [x] `docs/` 세부 가이드라인 파일 분리 생성 완료
  - [x] `docs/design-guidelines.md`
  - [x] `docs/prompt-page-guidelines.md`
  - [x] `docs/content-guidelines.md`
  - [x] `docs/seo-guidelines.md`
  - [x] `docs/accessibility-guidelines.md`
  - [x] `docs/agent-policy/coding-standards.md`
  - [x] `docs/agent-policy/tooling-efficiency.md`
- [x] `AGENTS.md` 라우터 구조로 축소 개편 (728줄 -> 105줄, 85.5% 감소)
- [x] `python3 scripts/build.py` 빌드 검증 성공

## 2. 세부 변경 내역 (Changes)
- `AGENTS.md`: 얇은 라우터 구조(v5.0-Router)로 개편. 라우팅 표(Policy Triggers Table), 핵심 아키텍처, 절댓칙, 토큰 절약 전략만 명확히 유지.
- `docs/` 하위 모듈 생성: 디자인, 프롬프트 페이지, 데이터, SEO, 접근성, 코딩 표준, 토큰 절약 정책 문서 분리 작성.

## 3. 검증 결과 (Validation)
- `python3 scripts/build.py` 실행 결과 정상 통과 (Pages: 5, Assets: 5, Routes: 5).
- 파일 링크 유효성 확인 완료.
