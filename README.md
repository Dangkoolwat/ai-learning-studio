# AI Learning Studio

AI Learning Studio는 AI 입문자와 기초 활용자가 프롬프트를 이해하고, 직접 만들고, 단계형 실습으로 결과물을 완성할 수 있도록 돕는 한국어 AI 교육 웹사이트입니다.

이 저장소는 HTML, CSS, Vanilla JavaScript, JSON, Markdown, Python을 사용해 경로별 정적 HTML을 생성하고 GitHub와 Vercel로 운영합니다.

---

## 프로젝트 상태

현재 프로젝트는 새롭게 구축하는 단계입니다.

이전 사이트의 SPA 구조나 구현을 이어 붙이지 않습니다. 현재 확정된 정보 구조, 페이지 유형, 디자인 원칙, GitHub·Vercel 운영 구조를 기준으로 단계별로 구현합니다.

---

## 주요 기능

- 완성된 프롬프트 복사
- 사용자 입력 기반 프롬프트 생성
- 단계형 AI 실습
- ChatGPT·Gemini 외부 연결
- 목적 기반 내비게이션
- 테마 변경
- 모바일 반응형 화면
- 경로별 정적 HTML과 SEO metadata

---

## 상위 영역

1. 🧪 AI 체험 실습
2. ⚡ 바로 사용하기
3. 🤖 AI 도우미
4. 🎨 이미지 AI

---

## 페이지 유형

- `static-prompt`: 완성된 프롬프트 제공
- `prompt-builder`: 입력값 기반 프롬프트 조합
- `practice-timeline`: 단계형 세로 실습

---

## 기술 구성

- HTML5
- CSS3
- Vanilla JavaScript ES Modules
- JSON
- Markdown
- Python
- GitHub
- Vercel

React, Next.js, TypeScript, SPA 프레임워크를 사용하지 않습니다.

---

## 로컬 실행

### 1. 저장소 복제

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. 정적 사이트 빌드

```bash
python3 scripts/build.py
```

빌드 결과는 `dist/`에 생성됩니다.

### 3. 로컬 서버 실행

Python 기본 서버를 사용할 수 있습니다.

```bash
python3 -m http.server 8000 --directory dist
```

브라우저에서 다음 주소를 엽니다.

```text
http://localhost:8000/
```

파일을 직접 더블클릭하는 방식은 ES Module, 경로, fetch 동작이 브라우저 제한을 받을 수 있으므로 권장하지 않습니다.

---

## 기본 저장소 구조

```text
/
├─ AGENTS.md
├─ PROJECT.md
├─ README.md
├─ vercel.json
├─ .github/
├─ docs/
├─ assets/
├─ components/
├─ core/
├─ css/
├─ data/
├─ design/
├─ pages/
├─ templates/
├─ scripts/
├─ agent-log/
└─ dist/
```

자세한 기술 계약은 `PROJECT.md`, 에이전트 작업 규칙은 `AGENTS.md`를 확인합니다.

---

## 배포

배포 흐름:

```text
작업 브랜치
→ Pull Request
→ GitHub Actions 검증
→ Vercel Preview
→ 검수
→ main 병합
→ Vercel Production
```

Vercel 설정:

- Framework Preset: Other
- Build Command: `python3 scripts/build.py`
- Output Directory: `dist`

자세한 내용은 `docs/deployment-guidelines.md`를 확인합니다.

---

## 문서

- `AGENTS.md`: 코딩 에이전트 작업 규칙
- `PROJECT.md`: 프로젝트 구조와 기술 계약
- `docs/design-guidelines.md`: 디자인 기준
- `docs/prompt-page-guidelines.md`: 프롬프트 페이지 기준
- `docs/content-guidelines.md`: 교육 콘텐츠 기준
- `docs/seo-guidelines.md`: SEO 기준
- `docs/accessibility-guidelines.md`: 접근성 기준
- `docs/deployment-guidelines.md`: GitHub·Vercel 운영 기준

초기 구축 단계에서는 가이드라인 문서를 먼저 확정한 뒤 구현합니다.

---

## 작업 원칙

- 사용자 확정 내용을 임의로 변경하지 않습니다.
- 관련 없는 리팩터링을 하지 않습니다.
- 생성 파일을 직접 수정하지 않습니다.
- 실제로 수행한 검증만 기록합니다.
- 작업 결과는 `agent-log/`에 남깁니다.
- Vercel Preview에서 확인한 뒤 운영에 반영합니다.

---

## 라이선스

라이선스는 프로젝트 운영자가 별도로 확정합니다. 확정 전에는 임의의 라이선스를 추가하지 않습니다.
