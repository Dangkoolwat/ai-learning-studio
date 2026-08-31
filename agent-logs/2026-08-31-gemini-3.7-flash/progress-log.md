# Task Progress Log: 풍경 사진을 크레용 여행 포스터로 바꾸기 신규 페이지 등록 및 static-prompt 이중 박스 제거

- Date: 2026-08-31
- Model: Gemini 3.7 Flash (High)
- Target Page: `pages/sections/image-ai/crayon-travel-poster.md`
- Title: `풍경 사진을 크레용 여행 포스터로 바꾸기`
- Route: `/image-ai/crayon-travel-poster/`
- Source: `X @xiaoxiaodong01`

---

## 1. 계획 및 사전 검토
- [x] 원본 Threads 및 개선 프롬프트 비교 분석
- [x] 꿀팁 6종 및 하단 강조 문구 구성안 확정
- [x] Implementation Plan 작성 및 사용자 승인 획득

## 2. 구현 및 피드백 반영
- [x] `pages/sections/image-ai/crayon-travel-poster.md` 신규 파일 작성
- [x] `data/page-registry.json` 항목 추가 및 메타데이터 동기화 (order: 61)
- [x] `data/navigation.json` 항목 추가 (featured: true)
- [x] 사용자 작성 최소화 및 글자 출력 위치 분리 피드백 반영
- [x] 문구 옵션 키워드 간소화: `[AI가 사진 분위기에 맞춰 자동 영문 작성 / 없음]`
- [x] ChatGPT Image 2 과잉 렌더링 방지를 위한 `### 4. 일러스트 영역` 정밀 지침 교체 반영
- [x] 페이지 제목 변경 반영: `풍경 사진을 크레용 여행 포스터로 바꾸기`
- [x] 예제 이미지 5종 등록 및 WebP 최적화 (`assets/images/image-ai/crayon-travel-poster/`)
- [x] 예제 이미지 슬라이더 순서 재배치 (기존 2번 세탁소 -> 1번, 기존 5번 전신주 -> 2번)
- [x] 실전 활용 꿀팁 독립 카드(섹션) 분리 구성 적용
- [x] **`static-prompt` 렌더러 이중 박스(Nested Card) 평탄화 로직 적용** (`core/renderers/static_prompt.py`)
- [x] **이미지 AI 전체 15개 프롬프트 페이지 꿀팁 섹션 상단 독립 카드 표준화 적용 (`소개 카드` -> `↓` -> `💡 꿀팁 카드` -> `↓` -> `🛠️ 프롬프트 카드`)**
- [x] **마크다운 베이스 렌더러 개선**: `실전 활용 꿀팁` 카드에 `.practice-step-card--tips` 클래스 자동 태깅 및 빈 카드 자동 스킵 (`core/renderers/base.py`)
- [x] **💡 실전 활용 꿀팁 카드 전용 시각적 악센트(Visual Accent) 스타일링 구현**: 앰버 캡슐 뱃지, 은은한 앰버 틴트 배경, 포인트 테두리 추가 (`assets/css/site.css`)
- [x] **마지막 방문 URL 자동 복원 및 홈 진입 스마트 라우팅 구현**:
  - `templates/partials/head.html`: 재접속 시 이전 서브메뉴 자동 복원 및 홈 명시적 진입 시 홈 유지 IIFE 구현
  - `assets/js/navigation.js`: 서브메뉴 방문 시 실시간 경로 기록 및 상단 로고(`.site-brand`) 클릭 시 홈 상태(`'/'`) 갱신 처리
- [x] 전체 72개 페이지 일괄 빌드 및 사이드 이펙트 전수 검증
- [x] 프롬프트 진단(`scripts/audit_prompts.py`) 통과 검증 (42개 에셋 검증)
- [x] 빌드 파이프라인(`scripts/build.py`) 72개 페이지 및 52개 에셋 정상 생성 검증
- [x] 73개 유닛 테스트 전체 통과 확인 (`python3 -m unittest discover -s tests`)
- [x] 브라우저 서브에이전트 기반 3대 라우팅 시나리오(자동 복원, 홈 클릭 진입, 홈 상태 유지) 전수 검증 완료

## 3. 검증 결과
- `python3 scripts/build.py`: Exit Code 0 (Pages: 72, Assets: 52, Routes: 72)
- `python3 scripts/audit_prompts.py`: Exit Code 0 (All prompt audits passed successfully)
- `python3 -m unittest discover -s tests`: Ran 73 tests in 1.76s, OK

## 4. AGENTS.md 에이전트 거버넌스 규칙 정립 (2026-08-31 추가)
- [x] `6.4 작업 전 모델 적합성 점검 (사전 게이트)` 신규 규칙 제정 및 추가
  - 구현·수정 작업 전 위험도/추론 난이도 분석 및 모델 적합성 선판단 의무화
  - 고위험 작업(아키텍처, 데이터 계약, 다중 모듈, 빌드/배포 등) 하위 모델 단독 수정 엄격 차단
  - 모델 불일치 시 `[모델 적합성 점검]` 표준 포맷 선보고 및 승인 대기
  - 저위험 작업도 1.5절 사전 승인 게이트 유지 및 PoC 결과의 최종 코드 무단 반영 차단
- [x] 정적 빌드 검증 (`python3 scripts/build.py`) 완료 (72개 페이지 정상 생성)

