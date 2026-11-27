# 작업 로그 (2026-11-27)

## 상태
- **상태**: 완료
- **작업 대상**: 프롬프트 한 스푼(`prompt-snippets`) — `파소나 법칙: 읽는 사람을 행동하게 만드는 글` 원 출처(`source`) 메타데이터 변경

## 변경 내역
- `pages/sections/prompt-snippets/pasona-persuasion.md`: Frontmatter `source`를 `자체제작`에서 `간다 마사노리, 稼ぐ言葉の法則, 2016 / 한국어판 돈이 되는 말의 법칙, 2018`로 변경 (짝 없는 끝 괄호 제거).

## 검증 결과 (단일 세션 보상 검증 / Self Compensatory)
- `python3 scripts/build.py`: 정상 완료 (`exit 0`, Pages: 83, Routes: 83).
- `python3 scripts/audit_prompts.py`: 83개 마크다운 페이지 및 56개 이미지 에셋 감사 통과 (`exit 0`).

---

## 후속 작업: 프롬프트 한 스푼 `📣 설득 & 말하기·쓰기 공식` 소그룹 분리 및 글쓰기 공식 3종(PREP·BAB·SCQA) 추가
- **상태**: 완료
- **변경 내역**:
  - `pages/sections/prompt-snippets/prep-framework.md`: `PREP 법칙: 결론부터 깔끔하게 말하고 쓰기` 신규 작성 (상황별 실전 예제 3종, 대표·추가 프롬프트, AI 활용 TIP).
  - `pages/sections/prompt-snippets/bab-storytelling.md`: `BAB 법칙: 변화를 보여주는 3단 스토리텔링` 신규 작성 (상황별 실전 예제 3종, 대표·추가 프롬프트, AI 활용 TIP).
  - `pages/sections/prompt-snippets/scqa-framework.md`: `SCQA 프레임워크: 논리적인 기획·보고 도입부` 신규 작성 (상황별 실전 예제 3종, 대표·추가 프롬프트, AI 활용 TIP, 원 출처 바바라 민토 명기).
  - `pages/sections/prompt-snippets/pasona-persuasion.md`: 상황별 실전 예제 2종 보강 및 PREP·BAB·SCQA 상호 비교 링크 연결.
  - `data/navigation.json`: `📣 설득 & 말하기·쓰기 공식` 소그룹 신설 (`elevator-pitch`, `pasona-persuasion` 이동 및 신규 3종 추가).
  - `data/page-registry.json`: `prep-framework`(`order: 68`), `bab-storytelling`(`order: 69`), `scqa-framework`(`order: 70`) 등록 및 제목·설명문 동기화.
  - `pages/sections/prompt-snippets.md`: 목적별 프롬프트 가이드맵에 `📣 설득 & 말하기·쓰기 공식` 추가.
- **검증 결과 (단일 세션 보상 검증 / Self Compensatory)**:
  - `python3 scripts/build.py`: 정상 완료 (`exit 0`, Pages: 86, Routes: 86).
  - `python3 scripts/audit_prompts.py`: 86개 마크다운 페이지 및 56개 이미지 에셋 감사 통과 (`exit 0`).
  - `python3 -m unittest discover -s tests`: 89개 테스트 통과 (`OK (skipped=3)`, `exit 0`).
  - 생성 HTML 확인: 신규 소그룹 사이드바, 인라인 콤보박스 미리보기, 하단 독립 `Source` 띠 박스 정상 렌더링 확인.

---

## 후속 작업: 프롬프트 한 스푼 방법론 5종 추가 (STAR·SBI·KPT·아이젠하워·5 Whys)
- **상태**: 완료
- **변경 내역**:
  - `pages/sections/prompt-snippets/star-framework.md`: `STAR 기법: 경험과 성과를 객관적으로 증명하기` 신규 작성 (`📣 설득 & 말하기·쓰기 공식`, 실전 예제 3종).
  - `pages/sections/prompt-snippets/sbi-feedback.md`: `SBI 피드백 공식: 기분 상하지 않게 피드백하기` 신규 작성 (`📣 설득 & 말하기·쓰기 공식`, CCL 출처, 실전 예제 3종).
  - `pages/sections/prompt-snippets/kpt-retrospective.md`: `KPT 회고: 프로젝트와 한 주를 다음 행동으로 정리하기` 신규 작성 (`🪞 회고 & 자산화`, 실전 예제 3종).
  - `pages/sections/prompt-snippets/eisenhower-matrix.md`: `아이젠하워 매트릭스: 긴급도와 중요도로 할 일 분류하기` 신규 작성 (`🧭 아이디어 & 판단`, 스티븐 코비 출처, 실전 예제 3종).
  - `pages/sections/prompt-snippets/five-whys.md`: `5 Whys: "왜?"를 5번 물어 근본 원인 찾기` 신규 작성 (`🔍 검토 & 문제 찾기`, 도요타 사키치 출처, 실전 예제 3종).
  - `data/navigation.json`, `data/page-registry.json`: 신규 5종 등록 (`order: 71~75`) 및 제목·설명문 동기화.
- **검증 결과 (단일 세션 보상 검증 / Self Compensatory)**:
  - `python3 scripts/build.py`: 정상 완료 (`exit 0`, Pages: 91, Routes: 91).
  - `python3 scripts/audit_prompts.py`: 91개 마크다운 페이지 및 56개 이미지 에셋 감사 통과 (`exit 0`).
  - `python3 -m unittest discover -s tests`: 89개 테스트 통과 (`OK (skipped=3)`, `exit 0`).
  - 생성 HTML 확인: 신규 5개 페이지 모두 인라인 콤보박스 미리보기 및 하단 독립 `Source` 띠 박스 정상 렌더링 확인.

---

## 후속 작업: 신규 5개 방법론 페이지 사용성 고도화 및 새 대화 첫 응답 테스트
- **상태**: 완료
- **변경 내역**:
  - 5개 페이지 공통(`five-whys.md`, `sbi-feedback.md`, `star-framework.md`, `eisenhower-matrix.md`, `kpt-retrospective.md`): 최상단에 `⚡ 바로 붙여 쓰는 한 줄` 프롬프트 카드 추가.
  - `five-whys.md`: 1문 1답 인터뷰를 대표 프롬프트로 승격(확인된 원인 / 더 알아볼 점 분리), 기존 일괄 분석을 추가 프롬프트(`가설 원인 초안`)로 이동.
  - `sbi-feedback.md`: 대표·추가 프롬프트에 구체적 상황·행동·영향 누락 시 선질문 가드 추가.
  - `star-framework.md`: `용도별 STAR`에 수치·성과 창작 금지 조건 추가 및 숫자 없는 성과 예시("내가 만든 인수인계표를 다음 담당자도 이어서 썼다") 반영.
  - `eisenhower-matrix.md`: `마감일과 목표를 함께 적기` 안내를 대표 프롬프트 바로 위로 이동.
  - `kpt-retrospective.md`: 대표 프롬프트를 Keep·Problem 모두에서 Try 1~3개를 도출하는 유연한 구조로 수정.
- **검증 결과 (단일 세션 보상 검증 / Self Compensatory)**:
  - `python3 scripts/build.py`: 정상 완료 (`exit 0`, Pages: 91, Routes: 91).
  - `python3 scripts/audit_prompts.py`: 91개 마크다운 페이지 및 56개 이미지 에셋 감사 통과 (`exit 0`).
  - 새 대화 첫 응답 테스트(독립 서브에이전트 2건): 5 Whys(`요즘 과제를 자꾸 늦게 내`)는 원인 단정 없이 최근 과제에 대한 1개 질문만 반환, SBI(`동료가 대충 한 것 같아`)는 사실 창작 없이 상황·직접 본 행동·실제 영향 3가지 선질문 반환 확인.
