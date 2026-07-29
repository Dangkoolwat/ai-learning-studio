# 진행 로그 (2026-07-29)

## 작업 내역
- **타이포그래피 프롬프트 페이지 추가**:
  - `pages/sections/image-ai/typography.md` 파일 생성
  - 사용자가 요청한 타이포그래피 생성 문구 및 조건 추가
  - 화면 비율, 배경색 항목을 인라인 태그 칩 옵션으로 처리 (예: `[ 16:9 가로형 / 1:1 정방형 / 9:16 세로형 ]`)
  - 자유 텍스트 입력 필드 `"[여기에 문구 입력]"`에 따옴표 적용 (파싱 오류 방지)
  - `ready-to-use-email` 페이지를 참고하여 `preview` 필드에 슬라이더용 예제 이미지 경로 추가 (`/assets/images/typography-example-1.png`, `/assets/images/typography-example-2.png`)
  ※ 빌드 시 슬라이더용 이미지가 최소 2개 이상 필요하여 임시로 2개의 경로를 입력함.

- **데이터 레지스트리 및 내비게이션 업데이트**:
  - `core/navigation.py`의 `EXPECTED_SECTIONS` 내 `image-ai` 섹션에 `image-ai-typography` 추가
  - `data/page-registry.json`에 `image-ai-typography` 데이터 등록
  - `data/navigation.json`에 `image-ai-typography` 메뉴 등록
- **이미지 리소스 관리 가이드라인 업데이트**:
  - `docs/content-guidelines.md` 파일에 이미지 에셋 저장 경로 규칙 추가 (`assets/images/<상위메뉴이름>/<페이지이름>/`)
  - 신규 생성한 `typography.md` 파일의 `preview` 경로를 새 가이드라인에 맞게 `/assets/images/image-ai/typography/...`로 수정 적용
- **이미지 파일 이동 및 미리보기 개선**:
  - 첨부해주신 이미지(`Downloads/seeyouagain.png`)를 가이드라인에 따라 `assets/images/image-ai/typography/typography-example-1.png`로 복사했습니다.
  - 미리보기 이미지가 1장일 때에도 에러가 발생하지 않고, 슬라이더 네비게이션(화살표 및 점)이 자동으로 숨겨지도록 컴포넌트 유효성 검사 및 렌더링 로직(`core/component_validation.py`, `core/renderers/static_prompt.py`)을 개선했습니다.
  - 이에 따라 `typography.md`의 `preview` 항목을 1장의 이미지로 다시 수정 반영했습니다.
- **프롬프트 텍스트 수정**:
  - `typography.md`에서 배경색 옵션 중 불필요한 `사용자 지정` 텍스트를 제거했습니다. (직접 타이핑 기능을 사용하면 되기 때문)
- **메뉴명 및 설명 업데이트**:
  - 사용자 친화적인 메뉴명(`손글씨 타이포그래피 만들기`)과 자세한 설명(`원하는 문구를 입력해 마커로 그린 듯한 삐뚤빼뚤하고 귀여운 레터링 이미지를 만들어 보세요.`)을 적용했습니다.
  - 관련 파일(`typography.md`, `core/navigation.py`, `core/page_registry.py`, `data/navigation.json`, `data/page-registry.json`)의 내용을 일괄 변경했습니다.
- **공통 컴포넌트 스타일 수정 (사용자 승인 완료)**:
  - `assets/css/site.css` 파일에서 이미지 슬라이더 프레임(`.image-slider__frame`)의 기본 파란색 배경(`background: #dce6f3;`)을 투명(`transparent`)으로 수정하여, 비율이 맞지 않는 이미지를 넣었을 때 빈 공간에 파란색 레터박스가 보이지 않도록 깔끔하게 개선했습니다.
  - 미리보기 이미지(`.image-slider__image`) 자체에도 모서리 둥글기(`border-radius`) 속성을 추가하여 프레임 배경이 없어도 이미지가 부드러운 라운딩 처리를 갖도록 수정했습니다.

## 빌드 검증
- `python3 scripts/build.py` 실행 완료
- `navigation items count mismatch`, `page registry must define exactly...`, `preview front matter requires at least two image paths` 에러를 각각 확인하고 수정 조치함.
- 최종 빌드 성공 및 18개 페이지 정상 생성 확인 (`dist/` 디렉토리)

## 대기 및 이관 사항 (Handoff)
- 사용자가 첨부한 예제 이미지를 `assets/images/` 디렉토리에 `typography-example-1.png`, `typography-example-2.png` 이름으로 저장해야 UI 상에서 정상적으로 표시됨.

- **모던 레시피 인포그래픽 프롬프트 페이지 추가**:
  - `pages/sections/image-ai/recipe-infographic.md` 파일 생성 완료.
  - `prompt-builder` 규칙을 준수하여, `food-name`과 `aspect-ratio` 2개의 `prompt-field`를 추가함 (빌드 에러 방지 및 화면 비율 사용자화 제공).
  - `core/navigation.py` 및 `core/page_registry.py`의 `EXPECTED_SECTIONS` / `EXPECTED_PAGES` 계약(contract)에 `image-ai-recipe-infographic` 추가.
  - `data/navigation.json` 및 `data/page-registry.json` 업데이트 완료.
  - 빌드(python3 scripts/build.py) 성공 확인.
  - `preview` 필드 이미지(`pasta-example.png`)는 사용자가 이미지를 올바른 경로에 배치하면 정상 표출됨.

- **예제 이미지 등록**:
  - 사용자가 첨부한 시스템 임시 파일(`media__1785324908996.png`)을 `assets/images/image-ai/recipe-infographic/pasta-example.png`로 이동 및 저장 완료.
  - `python3 scripts/build.py` 실행하여 빌드 오류 없음 확인.

- **`prompt-builder` 페이지 렌더러 미리보기 이미지 출력 버그 수정**:
  - 원인: `core/renderers/prompt_builder.py`의 `render_prompt_builder_page` 내부에서 `preview` 메타데이터에 대한 슬라이더 렌더링 로직이 누락됨.
  - 수정: `static_prompt.py`의 이미지 슬라이더 파싱 및 렌더링 로직을 `prompt_builder.py`에 적용.
  - 빌드 파이프라인(`core/renderer_validation.py`, `core/build_pipeline.py`)에서 `prompt-builder` 유형일 때 미리보기(`image-slider`) 컴포넌트를 기대하도록 컴포넌트 검증 규칙 수정.
  - `python3 scripts/build.py` 실행 완료 및 사이트 빌드 정상 통과(총 19개 페이지 정상).

- **롤백 완료**:
  - 사용자의 "원복" 요청에 따라, CSS 스타일을 통합 박스 형태로 묶었던 이전 변경사항(`c26a129`)을 파기하고 `git reset --hard`를 이용해 작업 전 안전 상태(`b096bda`)로 즉각 롤백 및 재빌드 완료함.

- **드롭다운 옵션 파싱 로직 정식 수정 (Fast Track)**:
  - 현상: HTML 폼(`<select>`) 렌더링 시 사용되는 `core/component_engine.py`에서 무조건 슬래시(`/`) 단위로 옵션을 자르다 보니, 괄호 속의 슬래시까지 잘라버리는 문제 확인.
  - 조치: 마크다운 파일의 텍스트 원복 후, 파이썬 파서가 옵션을 자르는 기준 문자열을 `/`에서 양옆에 공백이 포함된 ` / `로 명확히 수정함.
  - 효과: 템플릿 마크다운 내에서 옵션 구분을 위해 띄어쓰기와 함께 작성한 ` / `만 정확하게 파싱되며, 괄호 등 기타 텍스트 내부의 붙여쓴 슬래시는 파싱 에러를 유발하지 않음.
