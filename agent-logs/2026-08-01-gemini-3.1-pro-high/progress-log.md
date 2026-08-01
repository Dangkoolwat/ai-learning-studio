# 3D 직업 캐릭터 포스터 프롬프트 추가 작업 로그

## 1. 작업 개요
- **일시**: 2026-08-01
- **작업자**: Gemini 3.1 Pro (High)
- **목적**: `image-ai` 섹션에 "나만의 3D 직업 캐릭터 만들기" 프롬프트 신규 추가

## 2. 변경 내역
- `pages/sections/image-ai/3d-career-character.md` 파일 신규 생성 (프롬프트 본문 추가)
- `data/navigation.json`에 `image-ai-3d-career-character` 항목 추가
- `core/navigation.py`의 `EXPECTED_SECTIONS` 검증 리스트 업데이트
- `data/page-registry.json`에 `image-ai-3d-career-character` 페이지 등록
- `core/page_registry.py`의 `EXPECTED_PAGES` 검증 리스트 업데이트

## 3. 검증 결과
- `python3 scripts/build.py` 실행 완료
- 모든 페이지 및 네비게이션 데이터 검증 정상 통과

## 4. 추가 수정 내용 (코어 엔진 버그 패치)
- **이슈**: 드롭다운 칩에 따옴표(`"`)가 포함될 경우 `&quot;` 등 HTML 엔티티가 프론트엔드에 이중 이스케이프(Double Escaping)되어 그대로 출력되는 현상 발견.
- **해결**: `core/renderers/static_prompt.py`의 `render_inline_prompt_body_html` 정규식 파싱 방식을 리팩토링(`re.split` 기반 청크 처리).
- **효과**: 이중 변환 버그가 해결되었으며, 특수문자가 포함된 섹션 헤더(예: `[<역할>]`)를 인식하지 못하던 기존 버그도 함께 완벽하게 패치됨.

---

# AI 이력서·프로필 사진 생성 프롬프트 추가 작업 로그

## 1. 작업 개요
- **일시**: 2026-08-01
- **목적**: `image-ai` 섹션에 "AI 이력서·프로필 사진 생성" 범용 프롬프트 신규 추가

## 2. 변경 내역
- `pages/sections/image-ai/resume-profile.md` 파일 신규 생성
  - 사용자가 요청한 전체 원문 반영 및 UI 스마트 칩 렌더링을 위한 괄호 최적화(`"[여기에 문구 입력]"`) 적용
- `data/navigation.json`에 `image-ai-resume-profile` 항목 추가
- `core/navigation.py`의 `EXPECTED_SECTIONS` 검증 리스트 업데이트
- `data/page-registry.json`에 `image-ai-resume-profile` 페이지 등록
- `core/page_registry.py`의 `EXPECTED_PAGES` 검증 리스트 업데이트

## 3. 검증 결과
- `python3 scripts/build.py` 정상 실행
- 빌드 결과물(`dist/image-ai/resume-profile/index.html`) 이상 없음 및 에러 미검출 확인.
