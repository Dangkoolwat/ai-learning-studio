# AI Learning Studio

> AI를 설명하는 데서 끝나지 않고, 사용자가 직접 해보고 결과물을 만들도록 돕는 한국어 AI 학습 웹사이트

AI Learning Studio는 AI 입문자와 기초 활용자를 위한 교육형 웹 프로젝트입니다.

완성된 프롬프트를 그대로 사용하는 것에서 시작해, 자신의 상황에 맞게 프롬프트를 수정하고, AI와 여러 번 대화하며 실제 결과물을 만드는 과정을 단계적으로 학습할 수 있도록 설계했습니다.

이 프로젝트는 강사를 대신하는 서비스가 아니라, **강사의 교육 철학과 설명 흐름을 보조하는 학습 도구**를 목표로 합니다.

---

# 프로젝트가 지향하는 것

AI Learning Studio는 기능을 많이 보여주는 사이트보다, 학습자가 다음 행동을 쉽게 시작할 수 있는 사이트를 지향합니다.

- AI 활용 사례를 이해한다.
- 완성된 프롬프트를 바로 사용한다.
- 입력값을 바탕으로 자신의 목적에 맞는 프롬프트를 만든다.
- 단계별 실습을 따라 실제 결과물을 완성한다.
- AI의 답변을 그대로 믿지 않고 검토하고 수정한다.

---

# 주요 학습 영역

| 영역 | 설명 |
|------|------|
| 🧪 AI 체험 실습 | AI와 대화하고 결과를 수정하는 과정을 단계별로 경험합니다. |
| ⚡ 바로 사용하기 | 목적에 맞는 완성형 프롬프트를 복사해 바로 사용합니다. |
| 🤖 AI 도우미 | 사용자의 입력을 바탕으로 작업용 프롬프트를 구성합니다. |
| 🎨 이미지 AI | 이미지 생성과 시각 콘텐츠 제작에 필요한 실습을 제공합니다. |

- 메뉴 깊이는 최대 2단계로 제한합니다.
- 데스크톱에서는 왼쪽 내비게이션과 오른쪽 작업 영역을 사용합니다.
- 모바일에서도 동일한 학습 흐름을 유지하도록 설계합니다.

---

# 설계 원칙

- **Component First** — 반복되는 UI와 동작은 공통 컴포넌트로 관리합니다.
- **Data First** — 메뉴, 페이지, 콘텐츠, 테마 정보를 데이터로 분리합니다.
- **Theme First** — 테마는 구조와 기능을 바꾸지 않고 외형만 변경합니다.
- **SEO First** — 검색에 필요한 핵심 내용은 초기 HTML에 포함합니다.
- **Accessibility First** — 키보드, 포커스, 시맨틱 구조, 반응형 화면을 기본 조건으로 봅니다.
- **Lazy by Default** — 초기 화면에 필요하지 않은 자원은 필요한 시점에 불러옵니다.
- **Minimal Change** — 확정된 구조와 관련 없는 변경을 최소화합니다.

---

# 기술 스택

- HTML5
- CSS3
- Vanilla JavaScript (ES Modules)
- Python
- Markdown
- JSON
- GitHub
- Vercel

사용하지 않는 기술

- React
- Vue
- Next.js
- TypeScript
- Node.js
- Backend Framework
- Database

---

# 시스템 아키텍처

```text
Markdown / JSON
        │
        ▼
Python Build Pipeline
        │
        ▼
Page Registry
        │
        ▼
Renderer
        │
        ▼
Component Engine
        │
        ▼
Template Engine
        │
        ▼
Static HTML (dist/)
        │
        ▼
Vercel
```

Python이 모든 페이지를 정적 HTML로 생성하며, JavaScript는 사용자 인터랙션만 담당합니다.

---

# 프로젝트 구조

```text
.
├── assets/             CSS, JavaScript, 이미지
├── components/         공통 HTML 컴포넌트
├── core/               빌드 엔진
├── data/               페이지 레지스트리 및 JSON 데이터
├── design/             테마 원본
├── dist/               빌드 결과물
├── docs/               개발 및 설계 가이드라인
├── pages/              Markdown 콘텐츠
├── scripts/            빌드 스크립트
├── templates/          HTML 템플릿
├── AGENTS.md           AI 코딩 에이전트 라우터
└── README.md
```

---

# 시작하기

저장소를 복제합니다.

```bash
git clone https://github.com/Dangkoolwat/ai-learning-studio.git
cd ai-learning-studio
```

빌드를 실행합니다.

```bash
python3 scripts/build.py
```

빌드 후 자동으로 웹 서버를 실행하고 브라우저를 엽니다.

```bash
python3 scripts/serve.py
```

검증만 실행합니다.

```bash
python3 scripts/build.py --check
```

---

# AI 코딩 에이전트

이 저장소는 AI 코딩 에이전트(Codex, ChatGPT 등)와 협업할 수 있도록 설계되어 있습니다.

작업 순서는 다음과 같습니다.

1. `AGENTS.md`를 읽습니다.
2. 작업 종류에 맞는 `docs/` 가이드라인을 레이지 로딩합니다.
3. 필요한 범위만 수정합니다.
4. 빌드 및 검증을 수행합니다.

세부 규칙은 `AGENTS.md`와 `docs/`에서 관리합니다.

---

# 현재 구현 상태

| Phase | 상태 |
|-------|------|
| Phase 1 — Bootstrap | ✅ |
| Phase 2 — Build Pipeline | ✅ |
| Phase 3 — Page Registry | ✅ |
| Phase 4 — Theme Generator | ✅ |
| Phase 5 — Template Engine | ✅ |
| Phase 6 — Page Renderers | ✅ |
| Phase 7 — Common Components | ✅ |
| Phase 8 — First Learning Page | ✅ |
| Phase 9 — Core Learning Pages | ✅ |
| Phase 10 — Production Ready | ✅ |

---

# 빌드 및 검증

빌드

```bash
python3 scripts/build.py
```

검증

```bash
python3 scripts/build.py --check
```

빌드는 항상 Python을 통해 수행하며, 생성된 `dist/` 결과물은 직접 수정하지 않습니다.

---

# 배포

AI Learning Studio는 정적 사이트로 배포됩니다.

- Source Repository : GitHub
- Hosting : Vercel

---

# 라이선스

이 프로젝트의 교육 콘텐츠와 자료를 사용할 경우 출처를 표기해 주세요.

Copyright © 2026 진상혁. All rights reserved.