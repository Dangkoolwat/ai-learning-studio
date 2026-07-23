# 작업 및 진행 기록 (Progress Log)

- **작성 일자**: 2026-07-23
- **작업 목적**: 상위 메뉴 라벨 개편 및 메뉴 서브 설명(description) 구조 반영
- **담당 모델**: Gemini 3.6 Flash

---

## 1. 작업 개요

왼쪽 내비게이션 메뉴 네이밍을 사용자 요청에 맞춰 직관적인 이름으로 변경하고, 메뉴 설명(서브 설명)을 데이터 계약 및 UI 렌더링에 추가함.

### 변경 메뉴 명세
1. **`ai-practice`**
   - 상위 메뉴명: `프롬프트 단계별 체험하기`
   - 서브 설명: `같은 주제에 여러 프롬프트 방식을 적용하고 결과 차이 비교하기`
2. **`ready-to-use`**
   - 상위 메뉴명: `바로 써보기`
   - 서브 설명: `필요한 조건만 선택해 프롬프트를 만들고 바로 사용하기`
3. **`ai-assistant`**
   - 상위 메뉴명: `나만의 AI 만들기`
   - 서브 설명: `Project·Gem 등에 사용할 맞춤형 역할과 지침 만들기`
4. **`image-ai`**
   - 상위 메뉴명: `이미지 만들기`
   - 서브 설명: `이미지 생성·편집에 사용할 프롬프트 만들기와 실습`

---

## 2. 주요 변경 내역 (Files Changed)

- `core/navigation.py`: `NavigationSection` 구조에 `description` 추가, `EXPECTED_SECTIONS` 검증 및 로더 확장
- `core/page_registry.py`: `EXPECTED_PAGES` 계약 튜플 내 타이틀 및 설명 반영
- `core/template_engine.py`: 내비게이션 HTML 생성 시 `<span class="nav-label">` 및 `<span class="nav-description">` 구조로 렌더링하도록 변경
- `core/build_pipeline.py`: 정규식 `NAVIGATION_LINK_RE` 및 출력 검증 로직에 `description` 일치 여부 추가 검증
- `data/navigation.json`: 섹션 데이터에 새 라벨 및 `description` 필드 추가
- `data/page-registry.json`: 등록된 페이지들의 타이틀 및 설명 업데이트
- `pages/sections/ai-practice.md`: H1 제목을 `# 프롬프트 단계별 체험하기`로 변경
- `pages/sections/ready-to-use.md`: H1 제목을 `# 바로 써보기`로 변경
- `pages/sections/ai-assistant.md`: H1 제목을 `# 나만의 AI 만들기`로 변경
- `pages/sections/image-ai.md`: H1 제목을 `# 이미지 만들기`로 변경
- `assets/css/site.css`: `.nav-label` 및 `.nav-description` CSS 클래스 스타일 정의 추가
- `scripts/serve.py`: 원터치 자동 빌드 + HTTP 서버 실행 + 브라우저 자동 오픈 개발 스크립트 작성
- `core/renderers/static_prompt.py`: 인라인 조절 태그/빌더 옵션이 있는 프롬프트에만 하단 `✨ 완성된 프롬프트 (실시간 미리보기)` 독립 카드를 렌더링하고, 설정이 없는 일반 정적 프롬프트는 미리보기 상자 없이 본문 카드 하단에 [프롬프트 복사] 버튼을 직접 렌더링하도록 수술 완료
- `components/prompt-item.html`: `prompt_actions_html` 및 `prompt_preview_html` 조건부 플레이스홀더 도입
- `core/component_models.py` & `core/component_registry.py`: `PromptItemComponent` 및 승인 규격에 조건부 파라미터 반영
- `pages/sections/ready-to-use/email.md`: A안 및 B안 완벽 체험 비교 구성
- `README.md`: 원터치 개발 서버 실행 명령어 구문 추가

---

## 3. 빌드 및 검증 결과

* **실행 명령어**: `python3 scripts/build.py`
* **검증 결과**:
  * 16/16 단계 검증 완벽 통과
  * 6개 정적 페이지 (`/`, `/ai-practice/`, `/ready-to-use/`, `/ready-to-use/email/`, `/ai-assistant/`, `/image-ai/`) 및 서브 내비게이션 UI 정상 렌더링 완료 (`dist/` 생성 성공).

---

## 4. 완성된 프롬프트 UI 수정 (2026-07-23)

### 요청 사항
1. 완성된 프롬프트 제목 앞 ✨ 아이콘 삭제
2. 완성된 프롬프트 제목 하단 구분선(라인) 삭제

### 작업 내용
- `core/renderers/static_prompt.py`: `<h3 class="prompt-item__preview-title">`에서 `✨ ` 아이콘 제거 (`완성된 프롬프트 (실시간 미리보기)`)
- `assets/css/site.css`: `.prompt-item__preview-title`의 `border-bottom: 1px solid #e2e8f0;` 및 `padding-bottom` 제거

### 검증
- `python3 scripts/build.py` 빌드 정상 완료 (16/16 단계 통과)

---

## 5. 멀티셀렉션(다중 선택) 2가지 방안 적용 (2026-07-23)

### 작업 내용
1. **A안 인라인 다중 선택 태그 (`static-prompt`)**:
   - `core/renderers/static_prompt.py`: `[+ 옵션1 / 옵션2 / 옵션3 ]` 마크다운 패턴을 `data-type="multi-combo"` 칩으로 파싱
   - `assets/js/prompt-copy.js`: `multi-combo` 칩 클릭 시 체크박스 드롭다운 목록 렌더링 및 복수 선택 값을 쉼표(`, `)로 결합하여 실시간 본문/복사 미리보기 반영
   - `assets/css/site.css`: `.itc-dropdown__checkbox-item` 체크박스 칩 전용 CSS 스타일링 추가
2. **B안 폼 기반 다중 선택 (`prompt-builder`)**:
   - `assets/js/prompt-builder.js`: 다중 선택 필드(`attachments` 등) 수집 및 템플릿 실시간 조립 연동
3. **업무 이메일 페이지 반영**:
   - `pages/sections/ready-to-use/email.md`: `필요 첨부 서류: [+ 사업자등록증 / 견적서 / 통장사본 / 대표자 신분증]` 다중 선택 테스트 케이스 적용

### 검증
- `python3 scripts/build.py` 빌드 16/16 단계 완벽 통과 및 `dist/` 렌더링 검증 완료

---

## 6. (선택 없음) 실시간 미리보기 텍스트 노출 버그 수정 (2026-07-23)

### 수정 사항
- 멀티셀렉션 및 인라인 칩에서 아무 항목도 선택하지 않아 칩에 `(선택 없음)` 상태일 때, 실시간 미리보기 카드 및 복사 텍스트에 `(선택 없음)` 텍스트가 노출되던 문제 정제 수술.
- `assets/js/prompt-copy.js`: `getPromptText()` 파서에서 `(선택 없음)` 값을 빈 문자열(`""`)로 대치하고, 값 없이 남아있는 항목 라인(`- 필요 첨부 서류:`)을 정적 미리보기/복사본에서 자동으로 제거하도록 보완.
- `assets/js/prompt-builder.js`: `(선택 없음)`일 때 `attachmentLine` 조립 생략 처리.

### 검증
- `python3 scripts/build.py` 실행 (16/16 단계 검증 통과)

---

## 7. (선택 없음) 결합 병목 버그 정제 (2026-07-23)

### 수정 원인 및 내용
- **원인**: `selectedSet` 초기화 및 체크박스 온체인지 시 기존 `(선택 없음)` 문자열 필터링 누락으로 인해 새 항목 선택 시 `(선택 없음), 사업자등록증`과 같이 텍스트가 중복 결합되는 현상 발생.
- **수정**: `prompt-copy.js`의 `multi-combo` 집합 생성 및 `selectedSet` 갱신 로직에 `(선택 없음)` 자동 제거(`selectedSet.delete("(선택 없음)")`) 필터링 추가.

### 검증
- `python3 scripts/build.py` 실행 (16/16 단계 성공)




