# AI Learning Studio 프로젝트 기준서

이 문서는 AI Learning Studio의 목적, 정보 구조, 기술 구조, 페이지 계약, 데이터 구조, 테마 시스템, 배포 구조를 정의합니다.

구현 과정에서 세부 선택이 필요할 때는 이 문서와 `AGENTS.md`를 기준으로 판단합니다. 사용자가 더 최근에 확정한 내용이 있다면 그 결정을 우선합니다.

---

## 1. 프로젝트 개요

AI Learning Studio는 AI 입문자와 기초 활용자를 위한 한국어 AI 교육 웹사이트입니다.

사용자가 AI 개념을 읽는 데서 끝나지 않고 다음 행동까지 이어지게 하는 것을 목표로 합니다.

- AI 활용 사례 이해
- 완성된 프롬프트 복사
- 자기 상황에 맞는 프롬프트 생성
- 단계형 실습 진행
- ChatGPT 또는 Gemini에서 실제 사용
- 결과 검토와 수정

사이트는 강사를 대신하지 않습니다. 강사의 교육 철학과 설명 흐름을 보조하고, 학습자가 직접 결과물을 만드는 데 집중합니다.

---

## 2. 구축 원칙

이 프로젝트는 이전 웹사이트의 코드와 구조를 이어 붙이는 작업이 아닙니다.

다음 원칙만 계승합니다.

- Component First
- Data First
- Theme First
- SEO First
- Accessibility First
- Lazy by Default
- Minimal Change

이전 사이트의 SPA 구조, 라우팅, 디자인, 폴더 구조, 구현 관례는 자동으로 계승하지 않습니다.

---

## 3. 기술 스택

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
- 사용자 승인 없는 백엔드
- 사용자 승인 없는 데이터베이스
- 사용자 승인 없는 인증
- 사용자 승인 없는 AI API

---

## 4. 시스템 아키텍처

```text
JSON·Markdown·HTML 템플릿
        ↓
Python 정적 빌드
        ↓
경로별 HTML·metadata·SEO 파일 생성
        ↓
dist/
        ↓
Vercel 정적 배포
```

### 핵심 계약

- 검색 노출에 필요한 핵심 콘텐츠는 초기 HTML에 포함합니다.
- JavaScript는 상호작용을 담당합니다.
- 모든 페이지를 하나의 `index.html`로 보내지 않습니다.
- 페이지마다 독립된 정적 URL과 HTML을 생성합니다.
- 경로별 title, description, canonical, breadcrumb, JSON-LD를 생성합니다.
- Python 빌드 실패 시 배포를 중단합니다.

---

## 5. 정보 구조

상위 영역은 다음 네 가지로 고정합니다.

1. 🧪 AI 체험 실습 - 하나의 주제를 제로샷에서 시작해 프롬프트를 단계적으로 보강하며 최종본을 완성하는 체험형 메뉴
2. ⚡ 바로 사용하기 - 바로 복사해서 쓸 수 있는 완성형 프롬프트 제공 메뉴
3. 🤖 AI 도우미 - Project나 GEM 전용 지침서 프롬프트를 범용 템플릿 형태로 제공하는 메뉴
4. 🎨 이미지 AI - 이미지 생성용 프롬프트 허브, 상위에서는 개념과 차이를 설명하고 하위에서 세부 유형으로 확장

### 데스크톱

- 왼쪽: 목적 기반 내비게이션
- 오른쪽: 작업 페이지
- 메뉴 깊이: 최대 2단계
- 테마 선택기: 왼쪽 아래

### 모바일

- 내비게이션 drawer 또는 panel
- 데스크톱과 동일한 메뉴 데이터
- 테마 선택기: 설정 패널

상위 영역과 메뉴 깊이는 사용자 승인 없이 변경하지 않습니다.
상위 영역은 서로 다른 사용 목적을 분명히 구분합니다.

---

## 6. 페이지 유형

프롬프트 페이지 유형은 세 가지입니다.

### 6.1 `static-prompt`

완성된 프롬프트를 제공하는 페이지입니다.

- 입력 없음
- 생성 버튼 없음
- 프롬프트 표시
- 복사 기능
- 필요한 경우 외부 AI 열기

### 6.2 `prompt-builder`

입력값을 바탕으로 브라우저에서 프롬프트를 조합합니다.

```text
입력·선택
→ 프롬프트 만들기
→ 결과 확인
→ 복사
→ 외부 AI 열기
```

계약:

- AI API 호출 없음
- 템플릿과 사용자 입력만 사용
- 빈 선택 입력 생략
- 입력하지 않은 사실 생성 금지
- 필수값 검증
- 사용자가 결과 수정 가능
- 자동 입력을 약속하지 않음

### 6.3 `practice-timeline`

단계형 실습을 세로로 보여줍니다.

- tab 금지
- wizard 금지
- slide 금지
- 모든 단계 동시 표시
- JSON 배열 기반
- 최종 프롬프트 별도 강조

새 페이지 유형은 사용자 승인 없이 추가하지 않습니다.

---

## 7. 공통 렌더러와 컴포넌트

### 공통 렌더러

- `StaticPromptPage`
- `PromptBuilderPage`
- `PracticeTimelinePage`

### 공통 컴포넌트

- `PromptDisplay`
- `CopyButton`
- `ExternalAiActions`
- `PromptField`
- `PromptResult`
- `PracticeStep`
- `EmptyResult`
- `ValidationMessage`

구현 이름은 실제 코드 스타일에 맞춰 kebab-case 파일명과 named export를 사용할 수 있습니다. 역할과 계약은 유지합니다.

---

## 8. 권장 저장소 구조

```text
/
├─ AGENTS.md
├─ PROJECT.md
├─ README.md
├─ vercel.json
├─ .gitignore
│
├─ .github/
│  ├─ workflows/
│  │  └─ quality-check.yml
│  └─ pull_request_template.md
│
├─ docs/
│  ├─ agent-policy/
│  │  ├─ tooling-efficiency.md
│  │  └─ coding-standards.md
│  ├─ design-guidelines.md
│  ├─ prompt-page-guidelines.md
│  ├─ content-guidelines.md
│  ├─ seo-guidelines.md
│  ├─ accessibility-guidelines.md
│  └─ deployment-guidelines.md
│
├─ assets/
│  ├─ css/
│  │  └─ site.css
│  ├─ js/
│  ├─ images/
│  ├─ icons/
│  └─ fonts/
│
├─ components/
├─ core/
├─ data/
├─ design/
├─ pages/
├─ templates/
├─ scripts/
├─ tests/
├─ agent-logs/
└─ dist/
```

### 경로 역할

- `assets/`: 정적 CSS, JS, 이미지, 아이콘, 폰트 자산 원본
- `components/`: 재사용 HTML 컴포넌트 조각
- `core/`: Python 정적 빌드 코어 엔진 (렌더러, 테마, 템플릿, 데이터 검증)
- `data/`: 내비게이션(`navigation.json`) 및 페이지 등록부(`page-registry.json`)
- `design/`: 테마 토큰 및 디자인 설계
- `pages/`: 페이지 콘텐츠(Markdown) 및 페이지별 자산
- `templates/`: 페이지 단위 정적 HTML 템플릿
- `scripts/`: 빌드(`build.py`), 이미지 최적화, 감사 스크립트
- `tests/`: 파이썬 단위 테스트 스위트
- `agent-logs/`: 일자별 에이전트 작업 기록
- `dist/`: Vercel 정적 배포 결과물

---

## 9. 데이터 계약

기본 데이터 파일:

```text
data/
├─ navigation.json
└─ page-registry.json
```

### `navigation.json`

- 사이트 메뉴 구조 및 상위 섹션/하위 메뉴 정의
- `version`: 내비게이션 스키마 버전 (현재: `1`)
- `sections`: 상위 메뉴 영역 배열 (`id`, `label`, `description`, `order`, `items`)
  - `items`: 하위 메뉴 배열 (`id`, `label`, `description`, `route`)

### `page-registry.json`

- 저장소 내 모든 정적 페이지의 단일 진실 등록부
- `version`: 페이지 레지스트리 스키마 버전 (현재: `1`)
- `entries`: 개별 페이지 메타데이터 객체 배열
  - `id`: 고유 페이지 식별자
  - `title`: 페이지 제목
  - `description`: 페이지 메타 설명문
  - `route`: 정적 생성 URL 경로 (`/` 및 trailing slash 규칙 준수)
  - `source`: 마크다운 원본 소스 경로 (`pages/...`)
  - `type`: 프롬프트 렌더러 유형 (`static-prompt`, `prompt-builder`, `practice-timeline`)
  - `section`: 소속 상위 메뉴 섹션 ID
  - `order`: 정렬 순서
  - `navigation`: 사이드바/내비게이션 노출 여부 (`true`/`false`)
  - `status`: 게시 상태 (`published`/`draft`)
  - `lang`: 기본 언어 (`ko`)

모든 leaf 메뉴 경로는 페이지 등록과 연결되어야 합니다.

```text
menu path
=
pages registry path
=
canonical path
=
sitemap URL
```

경로는 소문자 kebab-case로 작성하고 trailing slash를 사용합니다.

---

## 10. 테마 시스템

사람이 관리하는 테마 원본:

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

배포 복사본:

```text
dist/assets/themes/<theme-name>/style.css
```

원칙:

- `design.md`가 원본입니다.
- 생성 파일은 직접 수정하지 않습니다.
- 테마는 외형만 바꿉니다.
- IA, 레이아웃 구조, 기능, 접근성은 바꾸지 않습니다.
- 테마별 HTML이나 컴포넌트를 만들지 않습니다.

디자인 방향:

- Studio Warm
- Studio Neutral
- Neutral Light/Dark
- 과도한 보라색 AI 그라데이션 금지
- shadcn/ui는 시각 참고만 사용

---

## 11. Python 빌드 계약

단일 빌드 명령:

```bash
python3 scripts/build.py
```

빌드 순서:

1. Python 버전 확인
2. 원본 데이터 검증
3. 기존 `dist/` 정리
4. 테마 생성
5. 경로별 HTML 생성
6. 정적 자산 복사
7. `sitemap.xml` 생성
8. `robots.txt` 생성
9. `404.html` 생성
10. 최종 결과 검증

빌드 오류가 있으면 종료 코드 `1`을 반환합니다.

---

## 12. GitHub + Vercel 구조

```text
작업 브랜치
→ Pull Request
→ GitHub Actions 검증
→ Vercel Preview
→ 사용자 검수
→ main 병합
→ Vercel Production
```

### 브랜치

- `main`: 운영 배포 브랜치
- 작업 브랜치: `agent/YYYY-MM-DD-작업이름`

### 배포 역할

- GitHub Actions: 검증
- Vercel Git 연동: Preview와 Production 배포

### Vercel 계약

- Framework Preset: Other
- Build Command: `python3 scripts/build.py`
- Output Directory: `dist`
- trailing slash 사용
- SPA catch-all rewrite 금지

---

## 13. SEO 계약

모든 공개 페이지는 다음을 가집니다.

- 고유 URL
- 하나의 검색 의도
- 초기 HTML 핵심 본문
- 고유 title
- 고유 description
- canonical
- robots
- Open Graph
- Twitter metadata
- 실제 내용에 맞는 JSON-LD
- breadcrumb
- 하나의 `h1`
- 올바른 제목 단계
- 내부 링크

사이트 전체:

- `dist/sitemap.xml`
- `dist/robots.txt`
- `dist/404.html`

Preview URL은 canonical로 사용하지 않습니다.

---

## 14. 접근성 계약

- 키보드 사용 가능
- skip link 제공
- 시맨틱 landmark
- 명확한 포커스
- `aria-current`
- `aria-expanded`
- live region
- Escape 닫기
- 포커스 복원
- label과 대체 텍스트
- reduced motion 지원
- forced colors 고려
- 320px 화면 지원

---

## 15. 완료 기준

기능이나 페이지는 다음 조건을 충족해야 완료로 판단합니다.

- Python 빌드 성공
- 경로별 HTML 생성
- 직접 URL 접근 가능
- 메뉴·페이지·canonical·sitemap 경로 일치
- title과 description 확인
- 키보드 조작 확인
- 모바일·태블릿·데스크톱 확인
- 긴 프롬프트와 한국어 문장 확인
- Vercel Preview 확인
- 작업 로그 작성
- 미확인 항목 명시

실행하지 않은 검증은 통과로 기록하지 않습니다.
