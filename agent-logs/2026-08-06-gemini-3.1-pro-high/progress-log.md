# 작업 로그: 마크다운 메일 링크 허용 및 수정 (2026-08-06)

## [Status / Files Changed / Verification / Handoff Status]
- **Status**: 완료
- **Files Changed**:
  - `pages/index.md`
  - `core/renderers/base.py`
- **Verification**: 빌드 성공 확인 (`python3 scripts/build.py` 실행 완료)
- **Handoff Status**: 작업 완료

## 1. 문제 현상 및 분석
- **현상**: `index.md` 내에 작성된 이메일 연락처(mailto:)가 링크로 렌더링되지 않음.
- **분석 1 (마크다운 문법)**: `chingoo2@naver.com(mailto:chingoo2@naver.com)` 형태로 작성되어 있어, 대괄호(`[]`)가 누락된 잘못된 마크다운 문법이었습니다.
- **분석 2 (빌드 실패)**: 마크다운 문법을 올바르게 수정(`[chingoo2@naver.com](mailto:chingoo2@naver.com)`) 후 빌드했으나, 렌더러가 내부 링크만 허용(`only internal links are allowed in markdown content`)하여 빌드가 실패했습니다.

## 2. 작업 내용
- `pages/index.md` 파일에서 이메일 링크 부분을 올바른 마크다운 문법으로 수정했습니다.
- `core/renderers/base.py` 파일의 `_is_safe_internal_href` 함수에 `mailto:` 프로토콜을 예외적으로 허용하도록 보안 정책을 수정했습니다.

## 3. 검증 결과
- 수정 후 `python3 scripts/build.py` 명령어를 통해 사이트 빌드를 다시 수행했으며, 성공적으로 HTML 변환이 완료됨을 확인했습니다.
