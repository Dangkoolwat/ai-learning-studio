# 사고 보고서: 프롬프트 섹션 헤더의 독립 카드 고립 및 시각적 분리 결함

## 1. 사고 개요
- **일시**: 2026-09-02
- **발생 위치**: `static-prompt` 유형 전체 페이지 (예: `prompt-snippets/refine-text`, `prompt-snippets/change-level` 등)
- **증상**: `## 추가 프롬프트`, `## 대표 프롬프트 ⭐` 등의 섹션 헤딩이 본문 프롬프트 카드와 묶이지 않고, 상하 36px 패딩과 배경색을 가진 독립된 거대 카드 박스(`.practice-step-card`)에 제목 한 줄만 갇힌 채 출력되어 부자연스러운 여백과 박스 중첩 발생.

---

## 2. 근본 원인 분석 (Root Cause Analysis)

### ① 8월 31일 커밋(`ee67379`)의 부분 수정 및 사이드 이펙트 간과
- **원인 배경**: 이전에는 `.practice-step-card` 안에 `prompt-item`이 중첩되어 테두리가 2겹으로 겹치는 이중 박스(Nested Box) 문제가 있었음.
- **불완전한 패치**: `static_prompt.py`에서 플레이스홀더 치환 시 `</div>\n{prompt_block}\n<div class="practice-step-card">`로 강제 분할을 적용함.
- **발생한 사이드 이펙트**: 마크다운 파서가 `## 추가 프롬프트`를 읽어 `<h3>추가 프롬프트</h3>`를 생성한 뒤, 바로 뒤에서 카드가 닫히면서 **헤더 텍스트 한 줄만 든 텅 빈 `.practice-step-card`가 생성**됨.

### ② 사이드 이펙트 사전 교차 검증(Visual Regression Check) 미흡
- `build.py` 빌드 스크립트(Exit Code 0) 및 HTML 태그 문법 검증에만 의존함.
- 빌드 통과 후 **실제 렌더링된 화면의 시각적 완성도(브라우저 스크린샷 교차 검증)를 수행하지 않아** 레이아웃 깨짐 현상을 조기에 감지하지 못함.

---

## 3. 재발 방지 대책 (Preventative Actions)

1. **렌더러 아키텍처 정규화**:
   - `static-prompt` 렌더러에서 프롬프트 블록 직전의 헤딩(`## 대표 프롬프트`, `## 추가 프롬프트`, `## 짧은 프롬프트` 등)을 무거운 실습 카드(`.practice-step-card`)에 가두지 않고, 전용 섹션 헤더(`.prompt-section-header`)로 변환 분리.
2. **시각적 사이드 이펙트 교차 검증 필수화 (AGENTS.md §6 준수)**:
   - 렌더러 및 CSS 수정 시 `browser_subagent`를 통해 `prompt-snippets`, `image-ai`, `ready-to-use` 등 유형별 대표 페이지의 브라우저 렌더링을 직접 촬영하고 교차 검증 후 사용자에게 보고.
3. **이중 박스 및 고립 박스 방지 자동 검사 추가**:
   - `scripts/audit_prompts.py`에 헤딩만 포함된 단독 `.practice-step-card` 존재 여부를 검사하는 린트 규칙 추가 검토.
