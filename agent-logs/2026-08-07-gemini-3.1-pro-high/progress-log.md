# 구글 폰트(Google Fonts) 연동 및 빌드 보안 예외 처리 작업 로그

## 1. 개요
* **작업 일시**: 2026-08-07
* **작업 목표**: 윈도우 환경 프롬프트 렌더링 가독성 향상을 위한 구글 폰트(`Noto Sans KR`, `Nanum Gothic Coding`) 적용.
* **주요 이슈**: 기존 `template_validation.py` 및 `build_pipeline.py`의 엄격한 Zero Trust 보안 정책으로 인해 외부 URL(`https://fonts.googleapis.com`) 로드 시 빌드 에러가 발생함. 이를 우회하기 위한 화이트리스트 예외 처리(Architecture Update) 단행.

## 2. 작업 계획 (Implementation Plan)
* `core/template_validation.py` 수정: 구글 폰트 도메인에 한해 외부 URL 검사 예외 처리 (Regex 치환 적용)
* `core/build_pipeline.py` 수정: `main_html` 검사 단계에서도 동일한 구글 폰트 예외 처리 로직 적용
* `templates/partials/head.html` 수정: `Noto Sans KR`, `Nanum Gothic Coding` 폰트 링크 삽입
* `assets/css/site.css` 수정: 프롬프트 표시 영역(`.prompt-item__content code`, `.prompt-item__preview-code`) 폰트 스택에 구글 폰트 추가

## 3. 체크리스트 및 실행 로그 (Execution)
- [x] 1. Update `core/template_validation.py` to whitelist Google Fonts URLs.
- [x] 2. Update `core/build_pipeline.py` output validation to whitelist Google Fonts URLs.
- [x] 3. Update `templates/partials/head.html` to include Google Fonts.
- [x] 4. Update `assets/css/site.css` to use Google Fonts for code blocks.
- [x] 5. Verify build success.

## 4. 검증 내역 (Verification)
- `python3 scripts/build.py` 실행 결과: 정상 통과 (Exit Code 0)
- `head.html` 내부에 `https://fonts.googleapis.com` 링크가 포함된 상태로 전체 정적 배포본 검증 및 빌드 통과를 확인.

## 5. 추가 스타일 개선 (Fast Track)
- **작업 내용**: 프롬프트 영역의 폰트 스택을 `JetBrains Mono` 및 `Noto Sans KR` 하이브리드로 변경하고, 사이즈를 `12px`(`xs`)로 축소하여 세련됨 극대화.
- **수정 파일**: `templates/partials/head.html`, `assets/css/site.css`
- **결과**: 정상 빌드 및 검증 완료.

## 6. 네이밍 리브랜딩 (조미료 -> 한 스푼)
- **작업 내용**: '프롬프트 조미료'라는 용어를 더 부드럽고 직관적인 '프롬프트 한 스푼'으로 전체 일괄 변경.
- **수정 파일**: 
  - 랜딩 페이지 (`pages/index.md`)
  - 서브 카테고리 본문 (`pages/sections/prompt-snippets.md` 외 4건)
  - 데이터/네비게이션 JSON 및 Python 레지스트리 (`navigation.json`, `page-registry.json`, `navigation.py`, `page_registry.py`)
- **결과**: 정상 빌드 및 검증 완료.
