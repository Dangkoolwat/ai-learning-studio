# AI 코딩 에이전트 작업 안내

이 문서는 **AI Learning Studio** 저장소에서 작업하는 모든 코딩 에이전트가 따라야 할 최상위 작업 규칙입니다. Codex, ChatGPT, Claude Code, Cursor, Windsurf, GitHub Copilot 등 어떤 도구를 사용하더라도 같은 기준을 적용합니다.

이 프로젝트는 기존 사이트를 수정하는 작업이 아니라, 지금까지 확정한 교육 목적·정보 구조·페이지 유형·디자인 원칙을 바탕으로 **새롭게 구축하는 정적 웹사이트 프로젝트**입니다. 이전 코드, 이전 라우팅, 이전 SPA 구조, 이전 디자인은 자동으로 계승하지 않습니다. 기존 자료는 사용자가 확정한 원칙과 재사용 가능한 콘텐츠를 확인할 때만 참고합니다.

---

## 1. 작업 우선순위

지시나 문서가 충돌하면 아래 순서로 판단합니다.

1. 현재 사용자 요청
2. 사용자가 가장 최근에 확정한 프로젝트 결정
3. 이 `AGENTS.md`
4. 현재 작업과 직접 관련된 가이드라인 문서
5. `PROJECT.md`
6. `README.md`
7. 기존 구현 관례

사용자가 확정한 구조를 일반적인 개발 관례나 에이전트의 선호로 바꾸지 않습니다. 구조, 기술 스택, IA, 페이지 유형, 배포 방식에 영향을 주는 충돌은 임의로 결정하지 말고 사용자에게 알립니다.

---

## 2. 프로젝트 목표

AI Learning Studio는 AI 입문자와 기초 활용자를 위한 한국어 AI 교육 웹사이트입니다.

사용자가 다음 행동으로 이어갈 수 있게 돕습니다.

- AI 활용 사례를 이해한다.
- 바로 쓸 수 있는 프롬프트를 복사한다.
- 입력값을 바탕으로 자기 상황에 맞는 프롬프트를 만든다.
- 단계형 실습을 따라가며 결과물을 완성한다.
- ChatGPT나 Gemini 같은 외부 AI 서비스에서 실제로 사용한다.
- 결과는 사람이 검토하고 수정해야 한다는 원칙을 배운다.

AI가 강사를 대신하지 않습니다. 사이트는 강사의 교육 철학, 설명 방식, 실습 흐름을 보조합니다.

---

## 3. 확정 기술 스택

사용 기술:

- HTML5
- CSS3
- Vanilla JavaScript
- JavaScript ES Modules
- JSON
- Markdown
- Python
- GitHub
- Vercel

사용하지 않는 기술:

- React
- Next.js
- Vue
- Angular
- Svelte
- TypeScript
- SPA 프레임워크
- 사용자 승인 없는 백엔드·데이터베이스·인증
- 사용자 승인 없는 외부 AI API

프레임워크 도입은 로그인, 데이터베이스, 서버 API, 사용자 계정, 대규모 동적 데이터 등 명확한 요구가 생겼을 때만 별도 검토합니다.

---

## 4. 확정 아키텍처

Python이 경로별 정적 HTML을 생성하고, JavaScript는 화면 상호작용만 담당합니다.

```text
JSON·Markdown·템플릿
        ↓
Python 빌드
        ↓
경로별 정적 HTML 생성
        ↓
dist/
        ↓
Vercel 정적 배포
```

핵심 규칙:

- 검색 노출에 필요한 본문은 초기 HTML에 있어야 합니다.
- 페이지 내용을 JavaScript 실행 뒤 처음 생성하는 구조를 사용하지 않습니다.
- 모든 경로를 하나의 `index.html`로 보내는 SPA fallback을 사용하지 않습니다.
- JavaScript는 프롬프트 생성, 복사, 메뉴 열기·닫기, 테마 변경 같은 상호작용만 처리합니다.
- 페이지 데이터와 화면 표현을 분리합니다.
- 경로별 HTML, metadata, canonical, breadcrumb, JSON-LD를 Python 빌드에서 생성합니다.

---

## 5. GitHub + Vercel 운영 구조

```text
GitHub 저장소
├─ 소스·데이터·문서 관리
├─ 작업 브랜치
├─ Pull Request
└─ GitHub Actions 검증
        ↓
Vercel Preview Deployment
        ↓
사용자 검수
        ↓
main 병합
        ↓
Vercel Production Deployment
```

### GitHub 역할

- 소스 코드, JSON·Markdown 콘텐츠, 설계 문서 관리
- 작업 브랜치와 Pull Request 관리
- 변경 이력 관리
- GitHub Actions 검증

### Vercel 역할

- Pull Request와 브랜치의 Preview Deployment
- `main` 브랜치의 Production Deployment
- Python 빌드 실행
- `dist/` 정적 결과 배포

### GitHub Actions 역할

GitHub Actions는 직접 배포하지 않고 다음을 검증합니다.

- Python 빌드 성공 여부
- JSON 형식
- 페이지 등록
- 메뉴·페이지·canonical 경로 일치
- 내부 링크
- 테마 생성
- `dist/` 결과

실제 Preview·Production 배포는 Vercel Git 연동이 담당합니다.

---

## 6. GitHub 작업 규칙

- 사용자 요청 없이 `main`에 직접 커밋하거나 push하지 않습니다.
- 작업별 브랜치를 사용합니다.
- 브랜치 이름은 `agent/YYYY-MM-DD-작업이름` 형식을 기본으로 합니다.
- 하나의 Pull Request에는 하나의 주요 목적만 포함합니다.
- 코드 변경과 작업 로그를 같은 Pull Request에 포함합니다.
- Vercel Preview 검수 후 `main` 병합을 진행합니다.
- Preview에서 확인하지 못한 항목은 작업 로그에 적습니다.
- 기존 미완료 변경을 임의로 정리하거나 덮어쓰지 않습니다.

---

## 7. 빌드와 배포 규칙

모든 환경에서 빌드 진입점은 하나로 통일합니다.

```bash
python3 scripts/build.py
```

`build.py` 기본 순서:

1. Python 버전 확인
2. 원본 데이터와 설정 검증
3. 기존 `dist/` 정리
4. 테마 생성
5. 경로별 정적 HTML 생성
6. CSS·JavaScript·이미지 복사
7. `sitemap.xml` 생성
8. `robots.txt` 생성
9. `404.html` 생성
10. 최종 배포 결과 검증

오류가 발생하면 종료 코드 `1`로 빌드를 중단합니다.

### Vercel 계약

- Framework Preset: Other
- Build Command: `python3 scripts/build.py`
- Output Directory: `dist`
- trailing slash 사용
- SPA catch-all rewrite 금지
- 문서·로그만 바뀐 변경은 필요하면 `ignoreCommand`로 빌드 생략

### `dist/` 규칙

- Python이 생성하는 배포 결과입니다.
- 수동 편집하지 않습니다.
- 원본 데이터나 템플릿을 수정한 뒤 다시 생성합니다.
- 기본적으로 Git에서 제외합니다.
- Vercel은 `dist/`만 공개합니다.
- `docs/`, `agent-log/`, 원본 설계 파일을 배포 결과에 포함하지 않습니다.

---

## 8. 정보 구조

상위 영역은 다음 네 가지입니다.

1. 🧪 AI 체험 실습
2. ⚡ 바로 사용하기
3. 🤖 AI 도우미
4. 🎨 이미지 AI

데스크톱:

- 왼쪽 목적 기반 내비게이션
- 오른쪽 작업 페이지
- 메뉴 깊이는 최대 2단계

모바일:

- 내비게이션 패널 또는 drawer
- 데스크톱과 같은 메뉴 데이터 사용
- 별도의 모바일 메뉴 트리 금지

상위 영역과 메뉴 구조는 사용자 승인 없이 변경하지 않습니다.

---

## 9. 프롬프트 페이지 유형

다음 세 유형만 사용합니다.

1. `static-prompt`
2. `prompt-builder`
3. `practice-timeline`

새 유형은 사용자 승인 없이 추가하지 않습니다.

### `static-prompt`

- 완성된 프롬프트 표시
- 사용자 입력 없음
- 생성 버튼 없음
- 복사 버튼 제공
- 필요한 경우 외부 AI 열기 제공
- 프롬프트 본문은 초기 HTML에 포함

### `prompt-builder`

```text
입력·선택
→ 프롬프트 만들기
→ 결과 확인
→ 복사
→ ChatGPT 또는 Gemini 열기
```

규칙:

- AI API를 호출하지 않습니다.
- 템플릿과 사용자 입력값만 조합합니다.
- 빈 선택 입력은 결과에서 생략합니다.
- 입력하지 않은 사실을 만들지 않습니다.
- 필수값을 검증합니다.
- 결과는 수정·복사할 수 있어야 합니다.
- 외부 AI를 열기 전에 복사 안내를 제공합니다.
- 프롬프트가 외부 AI에 자동 입력된다고 약속하지 않습니다.

### `practice-timeline`

- 세로형 페이지
- 모든 단계를 한 화면 흐름에서 확인
- wizard, tab, slide 금지
- JSON 배열 기반

각 단계는 필요한 범위에서 다음을 가집니다.

- 단계 제목
- 학습 포인트
- 프롬프트
- 복사 버튼
- 설명
- 무엇이 달라졌는지
- 예상 결과

마지막 최종 프롬프트는 별도로 강조합니다.

---

## 10. 공통 렌더러와 컴포넌트

페이지 렌더러:

- `StaticPromptPage`
- `PromptBuilderPage`
- `PracticeTimelinePage`

공통 컴포넌트:

- `PromptDisplay`
- `CopyButton`
- `ExternalAiActions`
- `PromptField`
- `PromptResult`
- `PracticeStep`
- `EmptyResult`
- `ValidationMessage`

규칙:

- 같은 목적의 마크업과 동작을 페이지마다 복제하지 않습니다.
- 새 컴포넌트 전에 기존 컴포넌트 재사용 가능성을 확인합니다.
- 단순 wrapper 하나를 위해 컴포넌트를 추가하지 않습니다.
- 컴포넌트는 명시적인 데이터를 입력받습니다.
- 콘텐츠, 경로, SEO 정보를 하드코딩하지 않습니다.
- 사용자 입력과 편집 문구는 `textContent`를 우선 사용합니다.
- 긴 한국어 문장과 긴 프롬프트를 견뎌야 합니다.

---

## 11. 데이터 규칙

권장 구조:

```text
data/
├─ site.json
├─ menu.json
├─ pages.json
└─ themes.json

pages/<slug>/
├─ page.json 또는 <slug>.json
├─ README.md
└─ 필요한 경우 전용 자산

templates/
├─ base.html
├─ static-prompt.html
├─ prompt-builder.html
└─ practice-timeline.html
```

원칙:

- 사이트 정보: `data/site.json`
- 메뉴: `data/menu.json`
- 페이지 등록: `data/pages.json`
- 교육 콘텐츠: 페이지 데이터 파일
- 테마 등록: `data/themes.json`
- JSON에 함수, 이벤트 handler, 실행식을 넣지 않습니다.
- JSON에 HTML 문자열을 넣는 방식은 별도 합의 없이 사용하지 않습니다.
- 편집 순서가 중요하면 배열을 사용합니다.
- 존재하지 않는 강좌, 통계, 후기, 기관, 작성자, 자격을 만들지 않습니다.

다음 경로는 항상 일치해야 합니다.

```text
menu path
=
page registry path
=
canonical path
=
sitemap URL
```

경로는 소문자 kebab-case와 trailing slash를 사용합니다.

---

## 12. 테마 시스템

사람이 관리하는 원본:

```text
design/<theme-name>/design.md
```

Python 생성 결과:

```text
design/<theme-name>/
├─ design.md
├─ tokens.json
├─ style.css
└─ manifest.json
```

사이트 테마 목록은 `data/themes.json`으로 관리하거나 생성합니다.

배포 복사본:

```text
dist/assets/themes/<theme-name>/style.css
```

규칙:

- `design.md`가 사람이 수정하는 원본입니다.
- 생성된 `tokens.json`, `style.css`, `manifest.json`, `themes.json`을 직접 수정하지 않습니다.
- 테마는 외형만 변경합니다.
- IA, 레이아웃 구조, 동작, 접근성을 바꾸지 않습니다.
- 테마별 HTML이나 컴포넌트를 만들지 않습니다.
- 테마 선택기는 데스크톱 왼쪽 아래, 모바일 설정 패널에 둡니다.
- 잘못된 테마 값은 기본 테마로 복구합니다.

디자인 방향:

- Studio Warm
- Studio Neutral
- Neutral Light/Dark
- 과도한 보라색 AI 그라데이션 금지
- shadcn/ui는 시각 참고만 가능하며 React 패키지로 사용하지 않음

---

## 13. 핵심 작업 원칙

1. **Component First** — 새 마크업 전에 기존 컴포넌트를 확인합니다.
2. **Data First** — 콘텐츠와 설정을 렌더링 코드 밖에 둡니다.
3. **Theme First** — 시각 변경은 토큰과 테마 CSS에서 처리합니다.
4. **SEO First** — 콘텐츠·경로 변경과 SEO 계약을 함께 관리합니다.
5. **Accessibility First** — 키보드와 보조기술 사용을 필수 조건으로 봅니다.
6. **Lazy by Default** — 현재 화면에 필요한 자산만 불러옵니다.
7. **Minimal Change** — 요청을 해결하는 최소 파일만 수정합니다.

---

## 14. SEO 규칙

모든 공개 페이지는 다음 조건을 충족해야 합니다.

- 고유 URL
- 페이지당 하나의 검색 의도
- 초기 HTML에 핵심 본문 포함
- 고유 title과 description
- canonical URL
- robots 정책
- Open Graph와 Twitter metadata
- 실제 내용에 맞는 JSON-LD
- 홈이 아닌 경로의 breadcrumb
- 하나의 `h1`
- 올바른 제목 단계
- 내부 링크
- `sitemap.xml`
- `robots.txt`

운영 도메인은 한 곳에서 관리합니다. Preview URL을 canonical로 사용하지 않습니다. 임시 페이지는 필요하면 `noindex`를 사용합니다.

---

## 15. 접근성 규칙

- 기본 HTML 컨트롤을 우선합니다.
- 본문 바로 가기 링크와 시맨틱 landmark를 제공합니다.
- 모든 상호작용 요소는 키보드로 사용할 수 있어야 합니다.
- 현재 위치는 `aria-current="page"`로 전달합니다.
- 펼침 상태는 `aria-expanded`로 전달합니다.
- 비동기 성공·실패 상태는 live region으로 알립니다.
- drawer나 dialog를 닫으면 이전 요소로 포커스를 돌립니다.
- Escape 닫기를 지원합니다.
- 포커스는 모든 테마에서 분명해야 합니다.
- `prefers-reduced-motion`과 강제 색상 모드를 존중합니다.
- 폼 요소에는 label을 제공합니다.
- 내용 이미지에는 의미 있는 대체 텍스트를 제공합니다.
- 장식 이미지는 빈 대체 텍스트를 사용합니다.
- 320px 화면에서도 조작 가능해야 합니다.

---

## 16. 성능 규칙

- 브라우저 기본 API를 우선합니다.
- 사용하지 않는 라이브러리를 추가하지 않습니다.
- 경로 전용 JavaScript와 자산은 해당 페이지에서만 불러옵니다.
- 첫 화면에 필요하지 않은 이미지는 lazy loading을 사용합니다.
- 이미지 크기를 지정해 layout shift를 줄입니다.
- 교육적 가치가 없는 대형 장식 이미지를 피합니다.
- 긴 프롬프트와 코드가 화면 밖으로 넘치지 않게 합니다.
- 실제 문제 측정 전 복잡한 최적화 계층을 추가하지 않습니다.
- 빌드 결과에 원본 문서, 로그, 비밀정보를 포함하지 않습니다.

---

## 17. 문서 구조와 지침 로딩

```text
/
├─ AGENTS.md
├─ PROJECT.md
├─ README.md
└─ docs/
   ├─ design-guidelines.md
   ├─ prompt-page-guidelines.md
   ├─ content-guidelines.md
   ├─ seo-guidelines.md
   ├─ accessibility-guidelines.md
   └─ deployment-guidelines.md
```

필요하면 다음 문서를 둡니다.

```text
components/<component-name>/README.md
pages/<page-slug>/README.md
```

작업별 확인 문서:

| 작업 | 먼저 확인할 문서 |
| --- | --- |
| 모든 저장소 변경 | `AGENTS.md` |
| 전체 구조·기술 계약 | `PROJECT.md` |
| 설치·실행 안내 | `README.md` |
| 레이아웃·스타일·테마 | `docs/design-guidelines.md` |
| 프롬프트 페이지 | `docs/prompt-page-guidelines.md` |
| 교육 콘텐츠 | `docs/content-guidelines.md` |
| metadata·canonical·sitemap | `docs/seo-guidelines.md` |
| 키보드·ARIA·포커스 | `docs/accessibility-guidelines.md` |
| GitHub·Vercel·배포 | `docs/deployment-guidelines.md` |

현재 작업과 직접 관련된 문서만 읽습니다.

필수 가이드라인이 없을 때:

- 초기 골격 단계라면 확정 설계를 기준으로 가이드라인 문서를 먼저 생성합니다.
- 초기 단계가 아니라면 누락 사실을 사용자에게 알리고 작업 로그에 기록합니다.
- 사용자 승인 없이 UI나 기능을 발명하지 않습니다.

---

## 18. 코딩 스타일

### JavaScript

- ES Module과 이름 있는 export를 사용합니다.
- 기본은 `const`, 필요할 때만 `let`을 사용합니다.
- 비동기는 `async`/`await`를 사용합니다.
- 긴 HTML 문자열보다 DOM API를 우선합니다.
- 콘텐츠 삽입은 `textContent`를 우선합니다.
- 함수는 작고 역할이 분명해야 합니다.
- 새 전역 변수를 만들지 않습니다.

### Python

- 빌드, 생성, 검증 책임을 분리합니다.
- 표준 라이브러리를 우선합니다.
- 외부 패키지는 이유를 문서화하고 승인받습니다.
- 경로 처리는 `pathlib`을 우선합니다.
- 같은 원본으로 같은 결과를 생성해야 합니다.
- 검증 실패를 종료 코드로 전달합니다.

### CSS

- 클래스 이름은 kebab-case를 사용합니다.
- 기존 토큰을 먼저 확인합니다.
- 구조 CSS, 페이지 전용 CSS, 테마 CSS의 책임을 섞지 않습니다.
- 대체 표현 없이 focus outline을 제거하지 않습니다.
- 320px, 태블릿, 데스크톱을 확인합니다.

### JSON과 Markdown

- UTF-8을 사용합니다.
- JSON은 2칸 들여쓰기를 사용합니다.
- 경로는 `/`로 시작하고 `/`로 끝나게 통일합니다.
- Markdown은 실제 구현과 일치해야 합니다.

---

## 19. 수정 원칙

- 편집 전에 관련 코드와 계약 문서를 읽습니다.
- 요청을 만족하는 최소 범위만 수정합니다.
- 사용자가 요청하지 않은 동작은 유지합니다.
- 콘텐츠 변경, 구조 변경, 디자인 변경, 기능 변경을 구분합니다.
- 관련 없는 파일을 다시 포맷하지 않습니다.
- 경로, ID, 폴더, 공개 입력 변경 시 모든 참조를 확인합니다.
- 생성 파일을 직접 고치지 않습니다.
- 사용자 승인 없이 구조를 다시 설계하지 않습니다.
- 좋은 아이디어가 있어도 확정 설계를 조용히 대체하지 않습니다.
- 대안을 제안할 때는 변경 대상, 이유, 기대 효과, 기존안과의 차이를 먼저 설명합니다.

---

## 20. 작업 결과 기록

저장소 파일을 변경한 작업은 `agent-log/`에 기록합니다.

```text
agent-log/YYYY-MM-DD-모델이름/
├─ summary.md
├─ changes.md
└─ validation.md
```

`summary.md`:

- 작업 목적
- 완료 내용
- 미완료 항목
- 사용자 확인 사항

`changes.md`:

- 수정·추가·삭제 파일
- 주요 변경
- 확정 설계와 달라진 점이 있다면 이유와 영향

`validation.md`:

- 실행한 빌드와 검증
- 직접 확인한 화면
- 통과·실패 항목
- 실행하지 못한 테스트
- Preview에서 확인하지 못한 항목

원칙:

- 실제로 수행한 작업만 기록합니다.
- 오류와 미완료를 숨기지 않습니다.
- 비밀번호, API 키, 개인정보를 기록하지 않습니다.
- 기존 로그를 덮어쓰지 않습니다.
- 단순 조회나 설명만 한 작업은 로그를 생략할 수 있습니다.
- 완료 응답에는 로그 경로를 함께 알립니다.

---

## 21. 편집 전 확인

- [ ] 현재 사용자 요청을 끝까지 읽었습니다.
- [ ] 가장 최근에 확정된 프로젝트 결정을 확인했습니다.
- [ ] `AGENTS.md`를 확인했습니다.
- [ ] 현재 작업에 필요한 가이드라인만 확인했습니다.
- [ ] 최소 변경 범위를 찾았습니다.
- [ ] 기존 컴포넌트와 데이터를 재사용할 수 있는지 확인했습니다.
- [ ] GitHub·Vercel·정적 빌드 영향 범위를 확인했습니다.
- [ ] SEO, 접근성, 테마, 경로 영향을 확인했습니다.
- [ ] 생성 파일과 원본 파일을 구분했습니다.
- [ ] 승인 없이 새 구조나 페이지 유형을 만들고 있지 않은지 확인했습니다.

---

## 22. 편집 후 확인

- [ ] `python3 scripts/build.py`를 실행했습니다.
- [ ] `dist/`가 정상 생성되었습니다.
- [ ] 변경 경로의 정적 HTML이 존재합니다.
- [ ] 메뉴·페이지 등록·canonical·sitemap 경로가 일치합니다.
- [ ] `h1`, 제목 단계, metadata, JSON-LD를 확인했습니다.
- [ ] 내부 링크, 직접 URL, 404를 확인했습니다.
- [ ] 키보드와 포커스 이동을 확인했습니다.
- [ ] 320px, 태블릿, 데스크톱을 확인했습니다.
- [ ] 적용 중인 모든 테마를 확인했습니다.
- [ ] 긴 프롬프트와 코드 overflow를 확인했습니다.
- [ ] 브라우저 콘솔 오류를 확인했습니다.
- [ ] Vercel Preview 확인 내용을 기록했습니다.
- [ ] 확인하지 못한 항목을 로그에 적었습니다.
- [ ] 관련 없는 수정과 중복 코드가 없는지 diff를 검토했습니다.

실제로 실행하지 않은 항목은 통과했다고 기록하지 않습니다.

---

## 23. 금지 사항

- Vanilla JavaScript를 React, Next.js, Vue, Angular, Svelte로 교체
- 사용자 승인 없이 TypeScript 도입
- 사용자 승인 없이 백엔드, 인증, 데이터베이스 추가
- 모든 경로를 하나의 `index.html`로 보내는 SPA rewrite 추가
- History API 기반 단일 SPA 구조로 변경
- 페이지 핵심 본문을 클라이언트 JavaScript가 처음 생성하게 만들기
- 페이지 콘텐츠를 JavaScript 렌더러에 하드코딩
- 메뉴를 HTML과 JavaScript에 중복 하드코딩
- 데스크톱과 모바일에 서로 다른 메뉴 데이터 사용
- 네 가지 상위 영역을 임의로 변경
- 세 가지 프롬프트 페이지 유형 외의 새 유형을 임의로 추가
- AI API를 몰래 추가
- 외부 AI에 프롬프트가 자동 입력된다고 안내
- 테마가 레이아웃, IA, 기능, 접근성을 바꾸게 만들기
- 생성된 테마 파일이나 `dist/`를 수동 수정
- 실제로 없는 콘텐츠, 통계, 후기, 출처, 작성자 생성
- 요청과 무관한 리팩터링과 이름 변경
- 사용자의 확정 내용을 일반 개발 관례로 대체
- 수행하지 않은 테스트를 통과했다고 기록
- 비밀정보, 캐시, 테스트 산출물 커밋

---

## 24. 초기 프로젝트 구축 순서

```text
1. 확정사항 정리
2. AGENTS.md 확정
3. PROJECT.md 작성
4. README.md 작성
5. docs 가이드라인 작성
6. 기본 폴더 구조 생성
7. Python 단일 빌드 골격 구현
8. Vercel 설정
9. GitHub Actions 검증 설정
10. 최소 정적 페이지 생성
11. Preview 배포 확인
12. 공통 컴포넌트 구현
13. 세 가지 프롬프트 페이지 유형 구현
14. 테마 생성 파이프라인 구현
15. 실제 콘텐츠 추가
```

기반 문서와 빌드가 검증되기 전에 전체 화면과 콘텐츠를 한꺼번에 만들지 않습니다.

---

## 25. 최종 판단 기준

- 현재 사용자 요청을 직접 해결했는가
- 최근 확정 내용을 유지했는가
- HTML·CSS·Vanilla JavaScript·Python 정적 생성 구조를 지켰는가
- GitHub + Vercel 운영 구조와 충돌하지 않는가
- 경로별 정적 HTML과 초기 SEO 본문을 보존했는가
- 네 가지 상위 영역과 세 가지 페이지 유형을 유지했는가
- 데이터·컴포넌트·테마 책임을 분리했는가
- 접근성과 모바일 사용성을 확인했는가
- 생성 파일과 원본 파일을 구분했는가
- 실제 검증 결과를 정직하게 기록했는가
- 관련 없는 변경을 만들지 않았는가

불확실한 내용은 추측으로 채우지 않고 확인이 필요한 상태로 남깁니다.
