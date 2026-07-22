# AI Learning Studio

> AI를 설명하는 데서 끝나지 않고, 사용자가 직접 해보고 결과물을 만들도록 돕는 한국어 AI 학습 웹사이트

AI Learning Studio는 AI 입문자와 기초 활용자를 위한 교육형 웹 프로젝트입니다.  
완성된 프롬프트를 복사해 사용하는 단계부터, 자기 상황에 맞게 프롬프트를 만들고 단계형 실습으로 결과물을 완성하는 과정까지 연결합니다.

현재는 **프로젝트 기반과 정적 사이트 생성 구조를 구축하는 초기 단계**입니다.

---

## 프로젝트가 지향하는 것

AI Learning Studio는 기능을 많이 보여주는 사이트보다, 학습자가 다음 행동을 쉽게 시작할 수 있는 사이트를 지향합니다.

- AI 활용 사례를 이해한다.
- 완성된 프롬프트를 바로 사용한다.
- 입력값을 바탕으로 자기 목적에 맞는 프롬프트를 만든다.
- 단계별 실습을 따라 실제 결과물을 완성한다.
- AI의 답변을 그대로 믿지 않고 검토하고 수정한다.

강사를 대신하는 서비스가 아니라, 강사의 교육 철학과 설명 흐름을 보조하는 학습 도구로 설계합니다.

---

## 주요 학습 영역

| 영역 | 설명 |
|---|---|
| 🧪 AI 체험 실습 | AI와 대화하고 결과를 수정하는 과정을 단계별로 경험합니다. |
| ⚡ 바로 사용하기 | 목적에 맞는 완성형 프롬프트를 복사해 바로 사용합니다. |
| 🤖 AI 도우미 | 사용자의 입력을 바탕으로 작업용 프롬프트를 구성합니다. |
| 🎨 이미지 AI | 이미지 생성과 시각 콘텐츠 제작에 필요한 실습을 제공합니다. |

메뉴 깊이는 최대 2단계로 제한하고, 데스크톱에서는 왼쪽 내비게이션과 오른쪽 작업 영역을 사용합니다.

---

## 페이지 유형

프로젝트의 프롬프트 페이지는 세 가지 유형으로 운영합니다.

### `static-prompt`

완성된 프롬프트를 읽고 복사하는 페이지입니다.

### `prompt-builder`

사용자가 입력한 조건을 조합해 브라우저에서 프롬프트를 만드는 페이지입니다.  
기본 구조에서는 AI API를 호출하지 않습니다.

### `practice-timeline`

모든 실습 단계를 한 화면에 세로로 보여주는 단계형 페이지입니다.

새로운 페이지 유형은 필요성과 교육적 효과를 먼저 검토한 뒤 추가합니다.

---

## 기술 구조

```text
JSON · Markdown · HTML Templates
                ↓
              Python
                ↓
        Static HTML Generation
                ↓
              dist/
                ↓
              Vercel
```

### 사용 기술

- HTML5
- CSS3
- Vanilla JavaScript
- JavaScript ES Modules
- JSON
- Markdown
- Python
- GitHub
- Vercel

### 사용하지 않는 기술

- React
- Next.js
- Vue
- TypeScript
- SPA 프레임워크
- 승인되지 않은 백엔드, 데이터베이스, 인증, AI API

이 프로젝트는 하나의 `index.html`에서 모든 경로를 처리하는 SPA가 아닙니다.  
각 공개 페이지는 독립된 정적 HTML과 고유 URL을 가집니다.

---

## 설계 원칙

- **Component First** — 반복되는 UI와 동작은 공통 컴포넌트로 관리합니다.
- **Data First** — 메뉴, 페이지, 콘텐츠, 테마 정보를 데이터로 분리합니다.
- **Theme First** — 테마는 구조와 기능을 바꾸지 않고 외형만 변경합니다.
- **SEO First** — 검색에 필요한 핵심 내용은 초기 HTML에 포함합니다.
- **Accessibility First** — 키보드, 포커스, 시맨틱 구조, 반응형 화면을 기본 조건으로 봅니다.
- **Lazy by Default** — 초기 화면에 필요하지 않은 자원은 필요한 시점에 불러옵니다.
- **Minimal Change** — 확정된 구조와 관련 없는 변경을 최소화합니다.

---

## 저장소 구조

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

주요 문서:

- [`AGENTS.md`](./AGENTS.md) — 코딩 에이전트 작업 규칙
- [`PROJECT.md`](./PROJECT.md) — 프로젝트 아키텍처와 기술 계약
- [`docs/deployment-guidelines.md`](./docs/deployment-guidelines.md) — GitHub·Vercel 배포 기준

---

## 로컬 실행

### 저장소 복제

```bash
git clone https://github.com/Dangkoolwat/ai-learning-studio.git
cd ai-learning-studio
```

### 정적 사이트 빌드

```bash
python3 scripts/build.py
```

빌드 결과는 `dist/`에 생성됩니다.

### 로컬 서버 실행

```bash
python3 -m http.server 8000 --directory dist
```

브라우저에서 다음 주소를 엽니다.

```text
http://localhost:8000/
```

ES Module과 경로 처리를 위해 HTML 파일을 직접 더블클릭하기보다 로컬 서버 사용을 권장합니다.

---

## 배포 방식

이 저장소는 개인 프로젝트이므로 기본적으로 `main` 브랜치에 직접 커밋하고 푸시합니다.

```text
Local Work
    ↓
Build and Validate
    ↓
Commit
    ↓
Push to main
    ↓
Vercel Production
```

Vercel 권장 설정:

- Framework Preset: `Other`
- Build Command: `python3 scripts/build.py`
- Output Directory: `dist`
- Trailing Slash: enabled

GitHub Actions는 배포가 아니라 빌드와 데이터 검증을 담당합니다.

---

## 현재 상태

현재 단계에서는 다음 기반을 먼저 확정하고 있습니다.

- [x] 프로젝트 목표와 원칙
- [x] 정보 구조
- [x] 페이지 유형
- [x] 정적 사이트 생성 방향
- [x] GitHub·Vercel 운영 기준
- [ ] 프로젝트 기본 폴더와 빌드 스크립트
- [ ] 데이터 스키마
- [ ] 테마 생성기
- [ ] 공통 템플릿과 컴포넌트
- [ ] 첫 번째 학습 페이지
- [ ] SEO·접근성 자동 검증

구현되지 않은 기능을 완료된 것처럼 소개하지 않습니다. 진행 상황은 실제 저장소 상태에 맞춰 갱신합니다.

---

## 로드맵

### 1. Project Bootstrap

프로젝트 폴더, 최소 Python 빌드, Vercel 설정, GitHub Actions를 구성합니다.

### 2. Build Pipeline

데이터 검증, HTML 생성, 자산 복사, 사이트맵과 404 생성을 구현합니다.

### 3. Theme System

`design.md`를 기준으로 테마 토큰과 CSS를 생성합니다.

### 4. Page Renderers

세 가지 페이지 유형의 공통 렌더러를 구현합니다.

### 5. First Learning Experience

실제 강의 흐름과 연결되는 첫 학습 페이지를 완성합니다.

### 6. Quality and Release

접근성, SEO, 반응형 화면, 직접 URL, 배포 결과를 검증합니다.

---

## 콘텐츠와 품질 기준

- 쉬운 설명을 먼저 제공하고 정확한 용어를 연결합니다.
- AI를 사람처럼 기억하거나 이해한다고 단정하지 않습니다.
- 학습 데이터, 현재 대화 맥락, 메모리, 웹 검색, 외부 도구를 구분합니다.
- 실습은 기능 체험보다 결과물 완성을 중심으로 설계합니다.
- 최신 정보가 필요한 내용은 공식 자료를 확인합니다.
- 생성된 프롬프트와 AI 답변은 사용자가 최종 검토합니다.

---

## 기여와 제안

현재는 개인 프로젝트로 운영하고 있습니다.

오류 제보나 개선 의견은 GitHub Issues로 남길 수 있습니다.  
프로젝트 방향과 맞지 않는 대규모 구조 변경은 바로 반영하지 않을 수 있습니다.

---

## 라이선스

라이선스는 추후 확정합니다.  
라이선스가 명시되기 전까지 저장소의 코드와 문서를 임의로 복제하거나 재배포하지 마세요.
