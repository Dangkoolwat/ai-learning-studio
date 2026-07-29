# 실패보고서: 프롬프트 미리보기 카드 상단 간격 문제

## 1. 작업 대상
- `ai-practice/summer-vacation-basic` 페이지의 `완성된 프롬프트 (실시간 미리보기)` 카드 상단 여백 문제를 줄이려는 수정 작업.

## 2. 기대 결과
- 미리보기 카드 제목이 카드 상단에 더 가깝게 붙고, 위쪽에 불필요한 빈 공간이 보이지 않아야 함.

## 3. 실제 결과
- 일부 여백은 줄었지만, 최종적으로 화면에서 미리보기 카드 제목이 여전히 아래로 떠 보였음.
- 사용자가 제공한 스크린샷 기준으로, preview 카드 상단이 일반 카드보다 훨씬 비어 보이는 상태가 남아 있었음.

## 4. 확인된 원인
- preview 카드가 일반 카드와 같은 `prompt-item__header` 구조를 공유함.
- 공통 헤더가 `display: flex` + `justify-content: space-between` + `flex-wrap: wrap` 기반이라, preview 전용으로 제목과 배지의 시각적 기준이 맞지 않았음.
- `h3` 제목의 공통 상단 마진과 preview 카드 상단 패딩이 함께 작용해 빈 공간이 더 커져 보였음.

## 5. 시도한 수정
- `assets/css/site.css`
  - `prompt-item.prompt-item--preview`의 `margin-top` 축소
  - preview 헤더의 `align-items: flex-start` 적용
  - preview 제목의 `margin: 0 !important` 적용
  - preview 카드 상단 `padding-top` 축소
- `core/renderers/static_prompt.py`
  - preview 카드 마크업은 유지한 채 스타일만 조정

## 6. 검증 결과
- `python3 scripts/build.py`는 성공적으로 통과함.
- 그러나 시각적으로는 preview 카드 헤더 구조 자체가 더 근본적으로 분리되지 않아, 최종 레이아웃 만족도는 부족했음.

## 7. 실패 판단
- 이번 작업은 “표면적인 여백 축소”에는 성공했지만, “preview 카드만 별도 헤더 레이아웃으로 분리”하는 수준까지 가지 못해 완전 해결로 보기 어려움.
- 따라서 이 작업은 부분 성공, 최종 UX 개선은 미완료로 판정함.

## 8. 다음 권장 조치
- `prompt-item--preview` 전용으로 헤더 마크업을 분리
- 제목 행과 배지 행을 별도 블록으로 재구성
- preview 카드에서만 적용되는 전용 spacing 규칙을 다시 정의
