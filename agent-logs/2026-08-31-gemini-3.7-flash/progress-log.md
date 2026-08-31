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
- [x] `docs/agent-policy/model-routing.md` 전용 정책 문서 신설 (거버넌스 완결)
  - 위험도 3단계 (High / Medium / Low) 판정 기준 및 예외/승격 규정(마크다운, 공통 템플릿) 명시
  - `[모델 적합성 점검]` 보고 양식 및 상위 모델 부재 시 Fallback/Override 보완 검증 정책 수립
  - 검증 모델의 실행 권한 경계 확립 (소스·Git 수정 금지 vs 테스트·빌드·브라우저 검증 허용)
  - `[검증 결과]` 표준 템플릿(PASS / FAIL / BLOCKED) 및 FAIL 재검증 루프 확립
- [x] `AGENTS.md` Thin Router 다이어트 및 Lazy-Loading 정책 완비
  - 2절 매핑 표에 `docs/agent-policy/model-routing.md` 라우팅 포인터 추가
  - 6.4/6.5절 세부 규칙을 4줄 요약으로 축소하고 전용 정책 문서로 분리 이관
  - 7절의 마크다운 세부 규칙을 `docs/prompt-page-guidelines.md`로 전면 이관 완료
- [x] 전체 무결성 검증 완료
  - `git diff --check`: PASS
  - `python3 scripts/build.py`: PASS (72개 정적 페이지 정상 생성)
  - `python3 scripts/audit_prompts.py`: PASS (42개 에셋 및 프롬프트 검증)
  - `python3 -m unittest discover -s tests`: Ran 73 tests, ALL OK

## 5. 거버넌스 정밀 보강 (검증 독립성, Bootstrap 예외, 운영문서 위험도 분리) (2026-08-31 추가)
- [x] `docs/agent-policy/model-routing.md` 보강
  - Capability 기반 High-Reasoning Tier 정의 (특정 모델명 종속 탈피)
  - 검증 모드 엄격 분리: Independent Higher-Tier Verification (동일 세션 후속 턴 독립성 배제) vs Self Compensatory Verification
  - 고위험 작업의 셀프 검증을 상위 검증으로 허위 보고하는 행위 원천 금지 및 사용자 Override 없는 자체 보상 검증 완료 불가 명시
  - `[검증 결과]` 보고 템플릿에 Verifier Mode, Task/Session ID, Working-Tree Ref, PASS Evidence Summary 필드 추가
  - 저위험(Low Risk) 범위에서 운영 계약 문서(`AGENTS.md`, `docs/agent-policy/`, `agent-logs/`) 제외 명시
- [x] `AGENTS.md` 보강
  - 2절에 `[Discovery Bootstrap 예외]` 명문화 (`pwd`, `list_dir`, `grep_search`, Serena 활성화 및 지정 파일 확인)
  - 6.4절 고위험 범위 명문화 및 사후 검증 문구 정렬 (`Substantive changes MUST be verified by an independent higher-tier verification model. If unavailable, completion may proceed only after explicit user override and documented Self Compensatory Verification. Self Compensatory PASS MUST NOT be reported as Independent Higher-Tier PASS.`)
- [x] 전체 무결성 검증 완료
  - `python3 scripts/build.py`: PASS (72 pages, 52 assets)
  - `python3 scripts/audit_prompts.py`: PASS
  - `python3 -m unittest discover -s tests`: Ran 73 tests, ALL OK
