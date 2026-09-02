# 실패 보고서: 출처(Source) 박스 본문 카드 내부 갇힘 및 임의 비대화 문제

## 1. 사고 개요
- **일자**: 2026-09-02
- **대상**: 정적 프롬프트(`static-prompt`) 및 이미지 프롬프트(`image-ai/*`), 바로 써보기(`ready-to-use/*`)의 출처(Source) 박스 렌더링
- **핵심 문제**:
  1. `static_prompt.py` 렌더러에서 마크다운의 `<!-- RENDERER_CONTROL_BLOCK:prompt:0 -->` 치환 시 `PromptItemComponent`의 `prompt_source_html`을 카드 박스(`.practice-step-card`) 내부에 그대로 렌더링하여, `Source` 항목이 `[프롬프트 복사]` 버튼 아래에 함께 갇혀서 출력됨.
  2. 이를 수정하는 과정에서 `site.css`의 `.prompt-item__source`에 본문 카드 박스 수준의 과도한 패딩(`1.25rem 1.75rem`)과 배경색/그림자를 임의로 부여하여 거대 박스로 부풀리는 사이드 이펙트 발생.

---

## 2. 근본 원인 분석 (Root Cause)
1. **플레이스홀더 치환 위치 오판**:
   - 마크다운 파서(`base.py`)는 각 섹션을 `<div class="practice-step-card">`로 감싸서 출력함.
   - 프롬프트 블록이 치환될 때 `prompt-item`과 `source_html`이 모두 카드 내부로 들어가면서 카드가 닫히지 않고 함께 갇힘.
2. **독립 분리 계약 미준수**:
   - `Source`는 프롬프트 본문 카드에 속한 하위 요소가 아니라, 프롬프트 카드 바깥에 위치하는 별도의 콤팩트 라운딩 띠 박스여야 한다는 설계 원칙을 간과함.

---

## 3. 재발 방지 조치 및 영구 규칙 (Invariant)

1. **`core/renderers/static_prompt.py` (렌더러 계약)**:
   - `PromptItemComponent`의 `prompt_source_html`은 항상 `""`로 비우고,
   - 프롬프트 카드를 감싸는 `<div class="practice-step-card">`가 닫히는 `</div>` 바로 바깥 줄에 `source_html`을 주입하여 본문 카드와 100% 분리 보장.
2. **`assets/css/site.css` (시각 토큰 표준)**:
   - `.prompt-item__source`: `background: var(--site-surface-muted)`, `padding: var(--als-space-3) var(--als-space-4)`, `border-radius: var(--site-radius-md)`, `box-shadow: none`.
   - 절대 본문 카드 박스처럼 패딩이나 그림자를 키우지 말 것.
3. **규정 문서화**:
   - `AGENTS.md` (섹션 7): 출처(Source) 독립 분리 원칙 명문화.
   - `docs/prompt-page-guidelines.md` (제6장): 카드 박스 내부 갇힘 절대 금지 및 슬림 띠 박스 규격 명문화.
