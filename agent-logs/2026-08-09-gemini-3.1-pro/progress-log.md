# AI 작업 로그 - 2026-08-09

## [Quick Plan] SNS 프로필 프롬프트 '추가 요청' 옵션 수정

### 1. 문제 현상 파악
`pages/sections/image-ai/sns-profile.md` 파일의 '7. 추가 요청' 항목에 사용자가 아무것도 요청하지 않을 경우 선택할 수 있는 '없음' 옵션이 누락되어 있습니다.

### 2. 수정 범위
- 대상 파일: `pages/sections/image-ai/sns-profile.md`
- 대상 라인: 60번째 줄

### 3. 작업 계획
`sns-profile.md`의 내용을 다음과 같이 수정합니다.

```diff
- "[자유롭게 추가 요청 사항을 입력하세요.]"
+ "[없음 / 자유롭게 추가 요청 사항을 입력하세요.]"
```

### 4. 검증 계획
- 파일 수정 후 `python3 scripts/build.py`를 실행하여 정상 빌드 여부 확인.
