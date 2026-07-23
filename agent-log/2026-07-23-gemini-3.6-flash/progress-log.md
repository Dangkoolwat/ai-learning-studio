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

