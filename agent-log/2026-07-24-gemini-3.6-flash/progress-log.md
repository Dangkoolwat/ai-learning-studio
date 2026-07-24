# Task Progress Log: Email Preview Slider Navigation Fix (2026-07-24)

## 1. 개요
- **목적**: `http://localhost:8000/ready-to-use/email/` 미리보기 이미지 슬라이더의 화살표(`< >`) 및 하단 네비게이션 점(dots) 클릭 미작동 버그 수정
- **대상 파일**:
  - `assets/js/image-slider.js`
  - `assets/css/site.css`

## 2. 변경 내역
- `assets/js/image-slider.js`:
  - `querySelector`로 단일 추출하던 `data-slider-prev`, `data-slider-next` 요소를 `querySelectorAll`로 전체 추출하여 모든 슬라이드의 화살표 버튼에 이벤트 바인딩.
  - `goTo()` 스크롤 위치 계산 방식을 `getBoundingClientRect()` 기반의 상대 위치 계산식(`viewport.scrollLeft + (slideRect.left - viewportRect.left)`)으로 보정.
- `assets/css/site.css`:
  - `.image-slider__viewport`에 `position: relative` 속성 추가.

## 3. 검증 결과
- `python3 scripts/build.py` 빌드 실행 정상 완료 (Pages: 12, Assets: 10, Routes: 12)
- dist/ 하위 정적 빌드 산출물 생성 확인 완료

