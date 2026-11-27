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


---

## 후속 작업: 신규 섹션 `프롬프트 패턴 연습` 1단계 (섹션 허브 + 시범 페이지 `Question Refinement`) 구축
- **상태**: 완료
- **변경 내역**:
  - `pages/sections/prompt-patterns.md`: 신규 섹션 허브 및 16개 패턴 지도(입문 7 · 활용 5 · 심화 4), White 외(2023) arXiv:2302.11382 v1 기준 안내 및 본문 5분류 vs 표 6분류 주석 작성.
  - `pages/sections/prompt-patterns/question-refinement.md`: 시범 페이지 `질문 다듬기 · Question Refinement` 신규 작성 (`static-prompt` 6단계 공통 틀, 5단계 인라인 스마트 콤보박스 3종, `프롬프트 한 스푼` 연결 동선, Frontmatter `source` 표기).
  - `data/navigation.json`: `prompt-patterns` 섹션(`order: 2`) 및 `🌱 입문` 그룹 내 시범 페이지 추가, 기존 하위 섹션 `order` 순차 조정(`3~6`).
  - `data/page-registry.json`: `prompt-patterns`(`order: 79`), `prompt-patterns-question-refinement`(`order: 80`) 등록 및 `title`·`description`·`route` 동기화.
  - `pages/index.md`: 홈 안내 목록에 `프롬프트 패턴 연습` 링크 추가.
- **검증 결과 (단일 세션 보상 검증 / Self Compensatory)**:
  - `python3 scripts/build.py`: 정상 완료 (`exit 0`, Pages: 96, Assets: 66, Routes: 96).
  - `python3 scripts/audit_prompts.py`: 96개 마크다운 페이지 및 56개 이미지 에셋 감사 통과 (`exit 0`).
  - `python3 -m unittest discover -s tests`: 89개 테스트 통과 (`OK (skipped=3)`, `exit 0`).
  - 생성 HTML(`dist/prompt-patterns/question-refinement/index.html`) 확인: 사이드바 2번째 섹션·`🌱 입문` 그룹, 1·2단계 기본 프롬프트 카드, 5단계 인라인 스마트 콤보박스 및 실시간 미리보기 박스, 페이지 최하단 단일 `Source` 슬림 띠 박스(`.prompt-item__source`) 정상 렌더링 확인.
  - 브라우저 실시간 스크린샷 검증: `검증 불가(Unverifiable)` (Chrome 원격 디버깅 포트 미활성화). 로컬 미리보기 서버(`http://localhost:8765`) 기동 상태로 사용자 직접 확인 가능.


---

## 후속 작업: `프롬프트 패턴 연습` 섹션 허브 논문 소개 보강 및 3단계 패턴 지도 목록화
- **상태**: 완료
- **변경 내역**:
  - `pages/sections/prompt-patterns.md`: 기준 논문(White 외 2023) 배경 및 6개 분류 체계 설명 카드 추가, 미지원 마크다운 표(`|...|`) 및 이탤릭 기호(`*...*`) 제거 후 카드 구획(`---`) + 목록 구조로 입문·활용·심화 16개 패턴 지도 재구성.
- **검증 결과 (단일 세션 보상 검증 / Self Compensatory)**:
  - `python3 scripts/build.py`: 정상 완료 (`exit 0`, Pages: 96, Assets: 66, Routes: 96).
  - `python3 scripts/audit_prompts.py`: 96개 마크다운 페이지 및 56개 이미지 에셋 감사 통과 (`exit 0`).


---

## 후속 작업: `프롬프트 패턴 연습` 내 `공개`·`준비 중` 상태 표기 제거
- **상태**: 완료
- **변경 내역**:
  - `pages/sections/prompt-patterns.md`: 16개 패턴 지도 항목의 ` · 공개`, ` · 준비 중` 표기 삭제.
  - `pages/sections/prompt-patterns/question-refinement.md`: 6단계 `함께 쓰면 좋은 패턴`의 `(준비 중)` 표기 삭제.
- **검증 결과 (단일 세션 보상 검증 / Self Compensatory)**:
  - `python3 scripts/build.py` 및 `python3 scripts/audit_prompts.py` 통과 확인.


---

## 후속 작업: `프롬프트 패턴 연습` 배치 1 (입문 7개 완성 및 4대 상황 예제 보강)
- **상태**: 완료
- **변경 내역**:
  - `pages/sections/prompt-patterns/question-refinement.md`: 취업·이직·공부·업무 실전 예제 4종 카드 추가, 5단계 `실무 업무 처리` 옵션 추가, `Flipped Interaction` 상호 링크 연결.
  - 신규 입문 6종 작성 (`flipped-interaction.md`, `persona.md`, `template.md`, `fact-check-list.md`, `reflection.md`, `alternative-approaches.md`): 각 페이지 모두 6단계 공통 틀 + 취업·이직·공부·업무 실전 예제 4종 + 5단계 인라인 스마트 콤보박스 + `프롬프트 한 스푼` 연결 동선 적용 (`template.md`는 콤보박스 오파싱 방지를 위해 출력 틀 자리를 `<>`로 표기).
  - `pages/sections/prompt-patterns.md`: 입문 7개 항목 링크 전체 연결.
  - `data/navigation.json`, `data/page-registry.json`: 입문 6종 등록 (`order: 81~86`) 및 제목·설명문·경로 동기화.
- **검증 결과 (단일 세션 보상 검증 / Self Compensatory)**:
  - `python3 scripts/build.py`: 정상 완료 (`exit 0`, Pages: 102, Assets: 66, Routes: 102).
  - `python3 scripts/audit_prompts.py`: 102개 마크다운 페이지 및 56개 이미지 에셋 감사 통과 (`exit 0`).
  - `python3 -m unittest discover -s tests`: 89개 테스트 통과 (`OK (skipped=3)`, `exit 0`).


---

## 후속 작업: `프롬프트 패턴 연습` 배치 2 (활용 5개 완성)
- **상태**: 완료
- **변경 내역**:
  - 신규 활용 5종 작성 (`cognitive-verifier.md`, `recipe.md`, `context-manager.md`, `game-play.md`, `meta-language-creation.md`): 각 페이지 모두 6단계 공통 틀 + 취업·이직·공부·업무 실전 예제 4종 + 5단계 인라인 스마트 콤보박스 + `프롬프트 한 스푼` 연결 동선 적용.
  - `pages/sections/prompt-patterns.md`: 활용 5개 항목 링크 전체 연결.
  - `pages/sections/prompt-patterns/question-refinement.md`: 6단계 `Cognitive Verifier` 상호 링크 연결.
  - `data/navigation.json`, `data/page-registry.json`: `🧭 활용` 그룹 5종 등록 (`order: 87~91`) 및 제목·설명문·경로 동기화.
- **검증 결과 (단일 세션 보상 검증 / Self Compensatory)**:
  - `python3 scripts/build.py`: 정상 완료 (`exit 0`, Pages: 107, Assets: 66, Routes: 107).
  - `python3 scripts/audit_prompts.py`: 107개 마크다운 페이지 및 56개 이미지 에셋 감사 통과 (`exit 0`).
  - `python3 -m unittest discover -s tests`: 89개 테스트 통과 (`OK (skipped=3)`, `exit 0`).


---

## 후속 작업: `프롬프트 패턴 연습` 배치 3 (심화 4개 완성 · 전체 16개 패턴 구축 완료)
- **상태**: 완료
- **변경 내역**:
  - 신규 심화 4종 작성:
    - `output-automater.md` (`실행 자동화 만들기 · Output Automater`): 6단계 + 취업·이직·공부·업무 실전 예제 4종 + 실행 전 검토·백업 안전 안내.
    - `visualization-generator.md` (`도표·그림 입력 생성하기 · Visualization Generator`): 6단계 + Mermaid 코드 생성 체험 + 취업·이직·공부·업무 실전 예제 4종 + ChatGPT·Gemini/mermaid.live 확인 안내.
    - `infinite-generation.md` (`같은 형식 계속 생성하기 · Infinite Generation`): 6단계 + 배치·중단 규칙 체험 + 취업·이직·공부·업무 실전 예제 4종.
    - `refusal-breaker.md` (`거절된 질문 다시 묻기 · Refusal Breaker`): 계획서 안전 원칙에 따라 우회 체험 프롬프트 없이 개념·정당한 활용 상황 4종·안전/윤리 주의점·대체 패턴 연결 중심으로 구성.
  - `pages/sections/prompt-patterns.md`: 심화 4개 항목 링크 전체 연결 (16/16 패턴 링크 완료).
  - `data/navigation.json`, `data/page-registry.json`: `🚀 심화` 그룹 4종 등록 (`order: 92~95`) 및 제목·설명문·경로 동기화.
- **검증 결과 (단일 세션 보상 검증 / Self Compensatory)**:
  - `python3 scripts/build.py`: 정상 완료 (`exit 0`, Pages: 111, Assets: 66, Routes: 111).
  - `python3 scripts/audit_prompts.py`: 111개 마크다운 페이지 및 56개 이미지 에셋 감사 통과 (`exit 0`).
  - `python3 -m unittest discover -s tests`: 89개 테스트 통과 (`OK (skipped=3)`, `exit 0`).


---

## 후속 작업: 동료 리뷰 반영 1차 (허브·`persona`·`context-manager` 3개 파일 보완)
- **상태**: 완료
- **변경 내역**:
  - `pages/sections/prompt-patterns.md`: 섹션 소개 아래(논문 소개 위)에 상황별 바로가기 4개 카드 추가, arXiv 개정본 오기 제거 및 논문/사이트 역할 구분 문구 반영, 15개 비교 실습 + 1개 읽기 자료(`refusal-breaker`) 안내 및 전체 공개 상태 문구 일치화.
  - `pages/sections/prompt-patterns/context-manager.md`: 1·2단계에 동일 가상 학습 메모 및 동일 분량 조건(`3분 안에 읽을 분량`) 적용 후 2단계에만 포함·제외 맥락 1문장 추가, 새 대화 두 개 실행 안내 추가, 3단계 `[ ]` 제거 및 개방형 관찰 질문으로 교체.
  - `pages/sections/prompt-patterns/persona.md`: 1·2단계에 동일 자소서·동일 요청 적용 후 2단계에만 역할 1문장 추가, 새 대화 두 개 실행 안내 추가, 3단계 `[ ]` 제거 및 개방형 관찰 질문으로 교체.
- **검증 결과 (단일 세션 보상 검증 / Self Compensatory)**:
  - `python3 scripts/build.py`: 정상 완료 (`exit 0`, Pages: 111, Assets: 66, Routes: 111).
  - `python3 scripts/audit_prompts.py`: 111개 마크다운 페이지 및 56개 이미지 에셋 감사 통과 (`exit 0`).


---

## 후속 작업: 동료 리뷰 반영 2차 (나머지 13개 비교 실습 페이지 전체 통일)
- **상태**: 완료
- **변경 내역**:
  - 나머지 13개 비교 실습 페이지(`flipped-interaction.md`, `template.md`, `question-refinement.md`, `fact-check-list.md`, `reflection.md`, `alternative-approaches.md`, `cognitive-verifier.md`, `recipe.md`, `game-play.md`, `meta-language-creation.md`, `output-automater.md`, `visualization-generator.md`, `infinite-generation.md`) 일괄 수정:
    - 1단계 상단에 "같은 AI 모델의 새 대화 두 개에서 각각 실행" 안내 추가.
    - 3단계 제목을 `## 3단계. 두 답변 비교하기`로 통일, 클릭 불가 `[ ]` 기호 전부 제거, 개방형 관찰 질문 3개(`어떤 점이 달라졌나요? 차이가 거의 없다면 어떤 내용이 공통으로 나왔나요?` 포함)로 교체.
- **검증 결과 (단일 세션 보상 검증 / Self Compensatory)**:
  - `python3 scripts/build.py`: 정상 완료 (`exit 0`, Pages: 111, Assets: 66, Routes: 111).
  - `python3 scripts/audit_prompts.py`: 111개 마크다운 페이지 및 56개 이미지 에셋 감사 통과 (`exit 0`).
  - `python3 -m unittest discover -s tests`: 89개 테스트 통과 (`OK (skipped=3)`, `exit 0`).
  - `rg -n "\[ \]" pages/sections/prompt-patterns/`: 잔여 `[ ]` 0건 확인 (`exit 1`).


---

## 후속 작업: 최종 리뷰 미비점 4건 수정 (`meta-language-creation`·`prompt-patterns`·`template`)
- **상태**: 완료
- **변경 내역**:
  - `pages/sections/prompt-patterns/meta-language-creation.md`:
    - 5단계 `/` 콤보박스 오파싱 해결 (기본 단축어 `/쉽게`·`/점검`·`/간결` 일반 텍스트화, 자유 입력 칸 `"[내 단축어와 동작 입력]"`).
    - 1·2단계 조건 통일(`비전공자 눈높이 3줄 요약 + 일상 비유 1개`), `/요약 트랜잭션` → `/개념 트랜잭션` 통일, 2단계 하단에 새 주제(`데이터베이스 인덱스`) 후속 비교 안내 추가.
  - `pages/sections/prompt-patterns.md`, `data/navigation.json`, `data/page-registry.json`: 섹션 설명을 `15개 패턴은 같은 요청으로 비교해 보고, ‘거절된 질문 다시 묻기’는 사례로 살펴봅니다.`로 동기화(HTML 이스케이프 충돌 방지를 위해 둥근 작은따옴표 사용), `Refusal Breaker` 항목에 `읽기 자료` 표기 추가.
  - `pages/sections/prompt-patterns/template.md`: 2단계·4단계의 `대괄호 자리` → `꺾쇠(< >) 안` 표기 통일.
- **검증 결과 (단일 세션 보상 검증 / Self Compensatory)**:
  - `python3 scripts/build.py`: 정상 완료 (`exit 0`, Pages: 111, Assets: 66, Routes: 111).
  - `python3 scripts/audit_prompts.py`: 111개 마크다운 페이지 및 56개 이미지 에셋 감사 통과 (`exit 0`).
  - `python3 -m unittest discover -s tests`: 89개 테스트 통과 (`OK (skipped=3)`, `exit 0`).
  - `dist/prompt-patterns/meta-language-creation/index.html` 확인: 5단계 기본 단축어(`/쉽게`, `/점검`, `/간결`) 및 자유 입력 칩(`내 단축어와 동작 입력`) 정상 렌더링 확인.


---

## 후속 작업: `프롬프트 패턴 연습` 섹션 설명 문구 16개 기준으로 동기화
- **상태**: 완료
- **변경 내역**:
  - `pages/sections/prompt-patterns.md`, `data/navigation.json`, `data/page-registry.json`: 섹션 `description`을 `16개 프롬프트 패턴을 전후 비교 실습과 안전 사례로 익혀 보세요.`로 동기화.
- **검증 결과 (단일 세션 보상 검증 / Self Compensatory)**:
  - `python3 scripts/build.py` 및 `python3 scripts/audit_prompts.py` 통과 확인.
