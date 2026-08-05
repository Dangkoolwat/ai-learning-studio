# 작업 로그 (2026-08-05)

## 1. SNS 프로필 프롬프트 템플릿 최종본 적용
- **수정 사항**: `pages/sections/image-ai/sns-profile.md` 텍스트 교체.

## 2. 핫픽스: 스타일 표현 방식 옵션 칩 누락 현상 수정
- **수정 사항**: `pages/sections/image-ai/sns-profile.md` 칩 렌더링 버그 수정.

## 3. 출력 개수 지시문 고도화 (AI 방어 로직)
- **수정 사항**: AI 서버 리미트 에러 방지용 지시문 세분화.

## 4. UI 편의성 개선: 사용자 가이드(Tip) 블록 위치 조정
- **수정 사항**: 사용자 안내 팁 최하단 이동 및 렌더링 수정.

## 5. 이력서 프로필 템플릿 UI 고도화
- **수정 사항**: `resume-profile.md` 정적 프롬프트(`static-prompt`) 도입.

## 6. [신규] 프롬프트 조미료 (Prompt Snippets) 대분류 신설
- **초기 모델**: 임시로 한 줄 팁을 모아둔 단일 모음집 페이지(`collection.md`) 제작.

## 7. 프롬프트 조미료 구조 전면 개편 (11개 개별 상세 페이지로 분리)
- **개요**: 사용자님의 "조미료 라이브러리" 설계 원칙(6단계 템플릿 구조)에 맞춰, 단일 모음집을 삭제하고 11개의 명확한 개별 상세 페이지로 분리 및 확장.
- **아키텍처 변경**:
  - `pages/sections/prompt-snippets/collection.md` 삭제
  - `navigation.json` 및 `page-registry.json` 업데이트 (11개 라우트 등록)
  - `core/navigation.py`, `core/page_registry.py` 동기화 (총 페이지 수 40개로 확장)
- **콘텐츠 신규 생성 (11개)**:
  1. `improve-results.md` (결과를 더 좋게 만들기)
  2. `review-answers.md` (AI 답변 검토하기)
  3. `reduce-hallucination.md` (할루시네이션 줄이기)
  4. `get-ideas.md` (다양한 아이디어 얻기)
  5. `format-clearly.md` (보기 쉽게 정리하기)
  6. `change-level.md` (설명 수준 바꾸기)
  7. `summarize-core.md` (요약과 핵심 정리)
  8. `compare-analyze.md` (비교와 분석)
  9. `refine-text.md` (글 다듬기)
  10. `continue-work.md` (이어서 작업하기)
  11. `ask-better.md` (AI에게 질문 잘하기)
- **구조 준수**: 각 페이지마다 [페이지 제목], [언제 사용하나요?], [이렇게 요청해 보세요.], [추가 프롬프트], [함께 사용하면 좋은 프롬프트], [TIP]의 6단계 구조를 엄격하게 적용하여 텍스트 및 프롬프트 블록(`prompt`) 작성.
- **검증**: 정적 빌드 100% 성공(40 Pages).
