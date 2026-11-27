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
