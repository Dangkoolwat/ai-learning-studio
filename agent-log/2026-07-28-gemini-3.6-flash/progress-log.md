# 작업 진행 및 검증 로그 (2026-07-28)

## 1. 작업 개요
- 마크다운 및 HTML 본문 헤딩 (`#` / `h1`, `##` / `h2`, `###` / `h3`) 상하단 마진 조정, 카드 템플릿 내 첫 타이틀 위치 복원 및 본문 헤딩 간격 확장.

## 2. 주요 변경 사항
- **[MODIFY] `assets/css/site.css`**:
  - `.practice-step-card h3`: `margin-top: 2.75rem !important` (44px) 및 `margin-bottom: 0.75rem !important`로 설정하여 카드 내부 연속 헤딩 간격을 넉넉하고 시원하게 띄움.
  - `.practice-step-card > :first-child`: 첫 자식 헤딩 요소의 `margin-top: 0 !important` 유지로 카드 맨 위 타이틀 밀착 구조 보장.

## 3. 빌드 및 검증 결과
- **빌드 명령어**: `python3 scripts/build.py`
- **결과**: `Build complete` (Pages: 13, Assets: 10, Routes: 13, Exit code: 0)
- **시각적 브라우저 검증**:
  - `http://localhost:8080/image-ai/index.html` 렌더링 확인 완료.
  - 전체 페이지 캡처 (`image_ai_full_page_1785225302795.png`) 실측 검수 결과, '텍스트 프롬프트와 무엇이 다를까요?', '그림을 설명한다고 생각해 보세요' 등 모든 `##` 제목 위쪽 마진이 44px로 여유롭게 확보됨을 직접 확인.
- **상태**: 완료
