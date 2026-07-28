# 작업 진행 및 검증 로그 (2026-07-28)

## 1. 작업 개요
- `프롬프트 단계별 체험하기` (`ai-practice`) 서브 메뉴에서 `여름휴가 계획 세우기 (기초편)`을 제외한 나머지 2개 서브메뉴(`제로샷에서 최종 프롬프트까지`, `프롬프트 기법 비교하기`) 삭제 및 파이프라인 정리.

## 2. 주요 변경 사항
- **[DELETE] `pages/sections/ai-practice/zero-to-final.md` & `prompt-techniques.md`**:
  - 미사용 마크다운 소스 파일 정리 및 삭제.
- **[MODIFY] `data/navigation.json` & `data/page-registry.json`**:
  - 내비게이션 메뉴 및 레지스트리 항목에서 `ai-practice-zero-to-final`과 `ai-practice-prompt-techniques` 제거, `order` 번호 전체 순차 보정.
- **[MODIFY] `core/navigation.py` & `core/page_registry.py`**:
  - 빌드 시스템 11개 정적 라우트 계약 동기화.

## 3. 빌드 및 검증 결과
- **빌드 명령어**: `python3 scripts/build.py`
- **결과**: `Build complete` (Pages: 11, Assets: 10, Routes: 11, Exit code: 0)
- **시각적 브라우저 검증**:
  - `http://localhost:8080/ai-practice/` 접속 검증 완료.
  - 스크린샷 캡처 검수 완료 (`sidebar_navigation_verification.png`). `여름휴가 계획 세우기 (기초편)` 메뉴만 정상적으로 남고 나머지 2개 항목이 삭제된 상태 확인 완료.
- **상태**: 완료
