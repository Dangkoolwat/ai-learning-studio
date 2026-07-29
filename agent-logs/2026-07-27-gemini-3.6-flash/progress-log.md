# Progress Log (2026-07-27)

## 작업 개요
1. `ai-practice.md` 및 `static-prompt` 유형 페이지에서 프롬프트 블럭(```prompt)이 포함되지 않더라도 빌드가 정상 완료되도록 조건 완화 및 검증 로직 수정
2. `pages/sections/ai-practice/summer-vacation-basic.md` 실습 페이지 정제 및 파이프라인 레지스트리/네비게이션 등록
3. 완성된 프롬프트 실시간 미리보기 카드(`prompt-item--preview`) 텍스트 누락 및 다중 카드 매핑 오류 버그 수정
4. 마크다운 본문의 강조 표현(`**text**`)을 HTML의 `<strong>text</strong>` 볼드 태그로 파싱하는 마크다운 파서 연동
5. 인라인 태그 칩 옵션 변경 시 칩 표기 텍스트 및 미리보기 카드 실시간 반영 버그 전면 보정
6. 미리보기 프롬프트 다중 행 렌더링 시 HTML 포맷터 들여쓰기 오염 제거 및 정렬 정상화
7. DOM attribute 동기화(`setAttribute("data-value")`) 및 버블링 차단(`e.stopPropagation()`)으로 옵션 선택 즉시 미리보기 동기화 보장

## 변경 파일
1. [static_prompt.py](file:///Users/sanghyoukjin/DongguramiProjects/AI%20Learning%20Studio/core/renderers/static_prompt.py)
   - `prompt_blocks` 0개일 때 `BuildError` 발생 로직 제거
   - `prompt_blocks` 존재 여부에 따른 `prompt-collection` 컴포넌트 조건부 렌더링
   - `_build_initial_clean_prompt_text` 구현으로 `<code class="prompt-item__preview-code">` 내 정적 기본 완성본 텍스트 렌더링
2. [build_pipeline.py](file:///Users/sanghyoukjin/DongguramiProjects/AI%20Learning%20Studio/core/build_pipeline.py)
   - Stage 11 (Parse renderer-specific control blocks) `static-prompt` 파싱에서 `prompt` 블럭 최소 1개 필수 제약 제거
   - `validate_renderer_component_usage`에서 `prompt_count > 0`일 때만 `prompt-collection` 컴포넌트 검증 포함
   - `render_markdown` 내 `**text**` -> `<strong>text</strong>` 인라인 볼드 변환 추가
3. [summer-vacation-basic.md](file:///Users/sanghyoukjin/DongguramiProjects/AI%20Learning%20Studio/pages/sections/ai-practice/summer-vacation-basic.md)
   - `ai_target: ChatGPT, Gemini` 명시 (ChatGPT 및 Gemini 원클릭 바로가기 및 전용 태그 지원)
   - 1~10단계 및 최종 프롬프트 블럭 정식 파티션(`title`, `description`, `---`) 및 인라인 스마트 콤보태그(`[ ... ]`) 구문 변환
4. [page-registry.json](file:///Users/sanghyoukjin/DongguramiProjects/AI%20Learning%20Studio/data/page-registry.json)
   - `ai-practice-summer-vacation-basic` 등록 및 순서(order) 조정
5. [navigation.json](file:///Users/sanghyoukjin/DongguramiProjects/AI%20Learning%20Studio/data/navigation.json)
   - `ai-practice` 섹션 하위 항목에 `여름휴가 계획 세우기 (기초편)` 연동
6. [navigation.py](file:///Users/sanghyoukjin/DongguramiProjects/AI%20Learning%20Studio/core/navigation.py)
   - `EXPECTED_SECTIONS` 상수에 `ai-practice-summer-vacation-basic` 등록
7. [page_registry.py](file:///Users/sanghyoukjin/DongguramiProjects/AI%20Learning%20Studio/core/page_registry.py)
   - `EXPECTED_PAGES` 상수에 `ai-practice-summer-vacation-basic` 등록 및 순서 연동
8. [prompt-copy.js](file:///Users/sanghyoukjin/DongguramiProjects/AI%20Learning%20Studio/assets/js/prompt-copy.js)
   - `applyValue` 시 `chip.dataset.value`와 `chip.setAttribute("data-value")`를 동시 동기화
   - `getPromptText`에서 `getAttribute("data-value")` 1순위 탐색 보장
   - 옵션 버튼 클릭 시 `e.stopPropagation()`을 적용하여 클릭 이벤트 버블링 차단 및 `updatePreview` 확정 실행
9. [base.py](file:///Users/sanghyoukjin/DongguramiProjects/AI%20Learning%20Studio/core/renderers/base.py)
   - `INLINE_BOLD_RE` 정규식 및 `_render_bold_and_escape` 함수 구현
   - `indent_preserving_pre` 포맷터 감지 조건에 `prompt-item__preview-code` 추가하여 원본 줄바꿈 들여쓰기 100% 보존

## 빌드 검증 결과
- `python3 scripts/build.py` 실행 결과 exit code 0 및 16단계 성공 (Pages: 13, Assets: 10, Routes: 13)
- `dist/assets/js/prompt-copy.js` 자산 배포 및 동기화 완료
