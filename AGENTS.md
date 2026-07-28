# AI 코딩 에이전트 작업 안내 (v5.0-Router)

이 문서는 **AI Learning Studio** 저장소에서 작업하는 모든 코딩 에이전트가 따라야 할 라우팅 중심의 최상위 작업 규칙입니다. 본 파일은 얇은 라우터(Router) 역할을 수행하며, 세부 정책은 트리거 발생 시 레이지 로드(Lazy-Loading)합니다.

---

## 1. 최상위 규칙 및 우선순위 (Source of Truth)

규칙이나 지시가 충돌할 경우 다음 순서로 절대 판단합니다.

1. **현재 사용자 요청**
2. **사용자가 가장 최근에 확정한 프로젝트 결정**
3. **이 `AGENTS.md` 라우터 문서**
4. **트리거로 로드된 `docs/` 세부 가이드라인 문서**
5. `PROJECT.md` & `README.md`
6. 기존 코드 및 구현 관례

---

## 1.5 작업 전 사전 보고 및 사용자 승인 필수 (Approval Gate)

- **사전 계획 보고 및 승인 대기 필수**: 코드, 마크다운, CSS, 데이터 등 저장소 내 모든 파일 수정 및 구현 작업에 착수하기 전, 에이전트는 **반드시 문제 현상 파악 결과, 수정 범위, 작업 계획을 간략히 보고**하고 **사용자의 명시적 승인을 확인한 후**에만 파일 수정 작업을 실행합니다. 사용자 승인 없는 임의 수정 및 선시행을 엄격히 금지합니다.

---

## 2. 필수 레이지 로딩 매핑 (Policy Triggers Table)

작업 종류 및 대상 키워드에 맞춰 **반드시 해당 가이드라인 문서를 먼저 독해**한 후 계획을 수립하고 코드를 수정합니다.

| 작업 영역 및 주요 키워드 | 필수 레이지 로딩 가이드라인 | 주요 내용 |
| :--- | :--- | :--- |
| **토큰 절약, 파일 읽기 범위, 도구 탐색 계층** | [`docs/agent-policy/tooling-efficiency.md`](docs/agent-policy/tooling-efficiency.md) | 수술적 독해, 500줄 독해 제한, 도구 계층 |
| **코딩 스타일, JS/Python/CSS, 수정 원칙** | [`docs/agent-policy/coding-standards.md`](docs/agent-policy/coding-standards.md) | 수술적 수정 원칙, 생성 파일 직접 수정 금지 |
| **레이아웃, 시각 토큰, UI 컴포넌트, 테마** | [`docs/design-guidelines.md`](docs/design-guidelines.md) | 정보구조, 테마 시스템, 공통 컴포넌트, 사이트 이펙트 검증 |
| **프롬프트 3개 유형 (`static`, `builder`, `timeline`)** | [`docs/prompt-page-guidelines.md`](docs/prompt-page-guidelines.md) | 3가지 정식 유형, 그냥 프롬프트 vs 설정값 반영 프롬프트 분리 규칙 |
| **데이터 파일, JSON 규칙, Markdown 콘텐츠** | [`docs/content-guidelines.md`](docs/content-guidelines.md) | `data/` 및 `pages/` 구조, 경로 일관성 |
| **메타태그, canonical, sitemap, JSON-LD** | [`docs/seo-guidelines.md`](docs/seo-guidelines.md) | 정적 HTML 본문 보존, SEO 계약 |
| **키보드 접근성, ARIA, 포커스, 320px 모바일** | [`docs/accessibility-guidelines.md`](docs/accessibility-guidelines.md) | 웹 접근성 표준, 반응형/성능 규칙 |
| **빌드, Vercel 정적 배포, GitHub Actions, dist/** | [`docs/deployment-guidelines.md`](docs/deployment-guidelines.md) | `python3 scripts/build.py`, 배포 규칙 |

---

## 3. 핵심 아키텍처 및 빌드 계약

Python이 경로별 정적 HTML을 생성하고, JavaScript는 화면 상호작용만 담당합니다.

```text
JSON · Markdown · Templates
            ↓
  python3 scripts/build.py
            ↓
  경로별 정적 HTML (dist/)
            ↓
    Vercel 정적 배포
```

- **단일 빌드 진입점**: 모든 환경에서 빌드는 `python3 scripts/build.py`로 실행합니다.
- **수동 수정 금지**: `dist/` 배포 결과물 및 Python 자동 생성 파일은 수동 편집하지 않습니다.

---

## 4. 토큰 절약 전략 (Context Economy)

- **수술적 독해 (Surgical Read)**: 파일 통독 대신 필요한 라인 범위만 조준 탐색 (500라인 이상 일괄 독해 금지).
- **최소 차분 수정 (Incremental Edit)**: 전체 코드를 재작성하지 않고 치환 도구를 통해 변경 부분만 수정.
- **로그 축소 요약 (Log Suppression)**: 빌드/테스트 성공 시 무분별한 덤프를 피하고 실패 및 스택 트레이스 핵심만 기록.

---

## 5. 절댓칙 (Core Prohibitions)

- Vanilla JS를 React/Next.js/Vue/Svelte 등 프레임워크로 교체 금지
- 사용자 승인 없는 백엔드, DB, 인증, 외부 AI API 도입 금지
- 모든 경로를 단일 `index.html`로 보내는 SPA Catch-all Rewrite 및 SPA Fallback 금지
- 페이지 핵심 본문을 클라이언트 JS가 뒤늦게 생성하는 구조 금지
- 세 가지 프롬프트 페이지 유형외의 새 유형 임의 추가 금지
- 생성된 테마 파일이나 `dist/` 결과물 직접 수정 금지
- `site.css` 내의 `.prompt-item` 및 `prompt-item__preview-section` 관련 핵심 레이아웃/구조 CSS 임의 수정 절대 금지 (사용자 승인 필수)

---

## 6. 검증 및 작업 로그

- 저장소 파일을 변경한 작업은 단일 로그 파일(`agent-log/YYYY-MM-DD-모델이름/progress-log.md`)에 진행 상황, 변경 내역, 빌드 검증 결과를 축적 기록합니다.
- **레이아웃 및 UI 사이드 이펙트(Side Effect) 체크 필수**: CSS, 마진, 패딩, 컴포넌트 레이아웃 변경 시 단일 페이지만 보지 않고 공통 컴포넌트 및 연관 페이지 전체의 시각적 렌더링 부작용(여백 벌어짐, 찌그러짐 등)을 브라우저 스크린샷으로 사전에 반드시 교차 점검합니다.
- 수정 후 반드시 `python3 scripts/build.py`를 실행하여 빌드 정상 여부를 검증합니다.

---

## 7. 프롬프트 마크다운 작성 규칙 (Learned Rule)
- 프롬프트 템플릿 작성 시, `[여기에 글 붙여넣기]` 같은 자유 텍스트 입력 옵션 칩이 단독으로 한 줄을 차지할 경우 파싱 엔진에 의해 '섹션 헤더'로 오인되어 무시됩니다. 
- 따라서 다음부터는 옵션이 정상적으로 나타나게 하려면 **반드시 `"[여기에 글 붙여넣기]"`와 같이 양쪽에 따옴표(`" "`)를 감싸서 옵션으로 제공**하는 것을 기본 규칙으로 합니다.
