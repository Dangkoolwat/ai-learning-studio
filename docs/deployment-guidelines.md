# GitHub·Vercel 배포 가이드라인

이 문서는 AI Learning Studio의 GitHub 협업, 자동 검증, Vercel Preview, Production 배포 규칙을 정의합니다.

---

## 1. 기본 배포 흐름

```text
작업 브랜치
→ Pull Request
→ GitHub Actions 검증
→ Vercel Preview Deployment
→ 사용자 검수
→ main 병합
→ Vercel Production Deployment
```

GitHub Actions는 검증을 담당하고, Vercel Git 연동은 실제 배포를 담당합니다.

---

## 2. 브랜치 정책

### `main`

- Production 배포 기준 브랜치
- 사용자의 명시적 요청 없이 직접 작업하지 않음
- 검증과 Preview 확인이 끝난 변경만 병합

### 작업 브랜치

기본 형식:

```text
agent/YYYY-MM-DD-작업이름
```

예시:

```text
agent/2026-07-22-project-bootstrap
agent/2026-07-22-theme-pipeline
agent/2026-07-22-prompt-builder
```

원칙:

- 하나의 브랜치에는 하나의 주요 작업 목적
- 관련 없는 정리나 리팩터링 포함 금지
- 사용자 확정 범위를 넘는 변경 금지

---

## 3. Pull Request 규칙

Pull Request에는 다음 내용을 포함합니다.

- 작업 목적
- 주요 변경 파일
- 사용자 확정 내용과의 관계
- 실행한 빌드와 검증
- Vercel Preview 확인 결과
- 확인하지 못한 항목
- 관련 `agent-log/` 경로

병합 전 확인:

- GitHub Actions 통과
- Vercel Preview 생성
- 직접 URL 확인
- 모바일·데스크톱 확인
- SEO metadata 확인
- 주요 키보드 동작 확인

---

## 4. GitHub Actions 역할

GitHub Actions는 다음을 검증합니다.

- Python 빌드
- JSON 구문
- 필수 데이터 필드
- 메뉴 경로와 페이지 등록 경로
- canonical 경로
- 사이트맵
- 내부 링크
- 생성 결과 존재 여부

기본 워크플로 예시:

```yaml
name: Quality Check

on:
  pull_request:
  push:
    branches:
      - main

jobs:
  validate-and-build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Build and validate
        run: python3 scripts/build.py
```

실제 프로젝트가 지원하는 Python 버전이 확정되면 워크플로와 문서를 함께 수정합니다.

---

## 5. Vercel 프로젝트 설정

권장 설정:

- Framework Preset: `Other`
- Build Command: `python3 scripts/build.py`
- Output Directory: `dist`
- Production Branch: `main`

루트 `vercel.json` 예시:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": null,
  "installCommand": "",
  "buildCommand": "python3 scripts/build.py",
  "outputDirectory": "dist",
  "trailingSlash": true
}
```

문서나 로그만 바뀌었을 때 배포를 생략하려면 `ignoreCommand`를 별도로 추가할 수 있습니다. 실제 스크립트가 존재하기 전에는 설정만 먼저 넣지 않습니다.

---

## 6. 금지하는 Vercel 설정

다음 SPA rewrite를 사용하지 않습니다.

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

이 설정은 경로별 정적 HTML, 직접 URL, SEO 계약을 무효화합니다.

또한 다음을 금지합니다.

- Preview URL을 canonical로 생성
- `dist/` 밖의 원본 문서 공개
- 빌드 오류를 무시하고 배포 계속
- 사용자의 승인 없이 Production 환경 변수 추가
- 비밀정보를 저장소에 커밋

---

## 7. `dist/` 관리

- `dist/`는 Python 빌드 결과입니다.
- 수동 편집하지 않습니다.
- 기본적으로 Git에서 제외합니다.
- Vercel Output Directory로 사용합니다.
- 필요한 파일만 포함해야 합니다.

필수 결과 예시:

```text
dist/
├─ index.html
├─ 404.html
├─ robots.txt
├─ sitemap.xml
├─ assets/
└─ <page-path>/index.html
```

배포 전에 다음을 확인합니다.

- HTML 파일 존재
- CSS·JavaScript 경로 유효
- 이미지 경로 유효
- 내부 링크 유효
- canonical이 Production 도메인 사용
- 원본 문서와 로그 미포함

---

## 8. URL 규칙

- 소문자 kebab-case
- 디렉터리 기반 경로
- trailing slash 사용

예시:

```text
/practice/travel-planning/
```

생성 파일:

```text
dist/practice/travel-planning/index.html
```

다음 값은 같아야 합니다.

```text
menu path
=
page registry path
=
canonical path
=
sitemap URL
```

---

## 9. Preview 환경

Vercel Preview는 다음 검수에 사용합니다.

- 페이지 레이아웃
- 데스크톱·모바일
- 메뉴 동작
- 프롬프트 복사
- 프롬프트 생성
- 테마 변경
- 직접 URL
- 404
- metadata
- 내부 링크
- 긴 한국어 문장
- 키보드 포커스

Preview에서 확인하지 못한 항목은 `agent-log/.../validation.md`에 기록합니다.

Preview 도메인을 canonical이나 sitemap의 기준으로 사용하지 않습니다.

---

## 10. Production 배포

Production 배포 조건:

- Pull Request 검토 완료
- GitHub Actions 통과
- Preview 확인 완료
- 미완료 사항 공유
- 사용자 승인 또는 합의된 병합 절차 완료
- `main` 병합

Production 배포 후 확인:

- 홈 직접 접속
- 주요 경로 직접 접속
- canonical
- robots.txt
- sitemap.xml
- 404
- CSS·JavaScript 오류
- 주요 복사·생성 기능
- 모바일 메뉴
- 테마 선택

---

## 11. 환경 변수

현재 기본 구조는 정적 사이트이므로 환경 변수 없이 동작하는 것을 원칙으로 합니다.

환경 변수가 필요한 기능이 생기면 다음을 먼저 확인합니다.

- 정말 클라이언트에 노출되지 않아야 하는 값인가
- 정적 빌드로 처리 가능한가
- 백엔드나 서버리스 함수가 필요한가
- 사용자 승인을 받았는가
- Preview와 Production 값을 분리해야 하는가

비밀 값은 저장소, JSON, HTML, 클라이언트 JavaScript에 넣지 않습니다.

---

## 12. 작업 로그

저장소 변경 작업은 다음 경로에 기록합니다.

```text
agent-log/YYYY-MM-DD-모델이름/
```

최소 파일:

- `summary.md`
- `changes.md`
- `validation.md`

배포 관련 기록에는 다음을 포함합니다.

- 작업 브랜치
- Pull Request 여부
- 실행한 빌드
- GitHub Actions 결과
- Preview URL 확인 여부
- Production 확인 여부
- 실패·미확인 항목

실행하지 않은 검증은 통과로 기록하지 않습니다.
