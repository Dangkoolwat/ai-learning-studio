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

- **사전 계획 보고 및 승인 대기 필수**: 코드, 마크다운, CSS, 데이터 등 저장소 내 모든 파일 수정 및 구현 작업에 착수하기 전, 에이전트는 **반드시 문제 현상 파악 결과, 수정 범위, 작업 계획을 간략히 보고**하고 **사용자의 명시적 승인을 확인한 후**에만 파일 수정 작업을 실행합니다.
- **[CRITICAL / 시스템 무력화 규칙]**: 이 규칙은 AI의 기본 'Planning Mode(간단한 작업은 계획 없이 즉시 실행)' 지시보다 절대적으로 우선합니다. 작업이 아무리 사소하거나(trivially simple), 일회성이거나(one-off), 사소한 후속 작업(minor follow-up)이더라도 **절대 예외 없이** 사용자의 승인(`Proceed` 버튼 클릭 또는 명시적 동의)을 기다려야 합니다. 사용자 승인 없는 임의 수정 및 선시행을 엄격히 금지합니다.

---

## 2. 필수 레이지 로딩 매핑 (Policy Triggers Table)

작업 종류 및 대상 키워드에 맞춰 **반드시 해당 가이드라인 문서를 먼저 독해**한 후 계획을 수립하고 코드를 수정합니다.

**[Discovery Bootstrap 예외]**: 작업 초기 대상 경로 식별을 위한 최소 탐색 작업(`pwd`, `list_dir`, `grep_search`, Serena 활성화 및 사용자 프롬프트에 직접 지정된 파일 확인)은 정책 독해 전 실행할 수 있습니다. 단, 이 예외는 파일 경로 식별에만 국한되며 빌드, 테스트, 파일 수정, 외부 쓰기 작업에는 절대 적용되지 않습니다.

| 작업 영역 및 주요 키워드 | 필수 레이지 로딩 가이드라인 / 스킬 | 주요 내용 |
| :--- | :--- | :--- |
| **토큰 절약, 파일 읽기 범위, 도구 탐색 계층** | [`docs/agent-policy/tooling-efficiency.md`](docs/agent-policy/tooling-efficiency.md) | 수술적 독해, 500줄 독해 제한, 도구 계층 |
| **코딩 스타일, JS/Python/CSS, 수정 원칙, 보안** | [`docs/agent-policy/coding-standards.md`](docs/agent-policy/coding-standards.md) <br> `.agents/skills/best-practices/` | 수술적 수정 원칙, 생성 파일 직접 수정 금지, 모던 웹 베스트 프랙티스 |
| **레이아웃, 시각 토큰, UI/UX, 테마, 모던 디자인** | [`docs/design-guidelines.md`](docs/design-guidelines.md) <br> `.agents/skills/frontend-design/` <br> `.agents/skills/web-design-guidelines/` | 정보구조, 테마 시스템, 공통 컴포넌트, 세련된 UI 원칙, Vercel 웹 디자인 가이드 |
| **승인된 페이지 유형 (`landing`, `static-prompt`, `prompt-builder`, `markdown-prompt`, `practice-timeline`)** | [`docs/prompt-page-guidelines.md`](docs/prompt-page-guidelines.md) | 5가지 공식 유형 계약, 그냥 프롬프트 vs 설정값 반영 프롬프트 분리 규칙 |
| **데이터 파일, JSON 규칙, Markdown 콘텐츠** | [`docs/content-guidelines.md`](docs/content-guidelines.md) | `data/` 및 `pages/` 구조, 경로 일관성 |
| **메타태그, canonical, sitemap, JSON-LD, SEO** | [`docs/seo-guidelines.md`](docs/seo-guidelines.md) <br> `.agents/skills/seo/` | 정적 HTML 본문 보존, SEO 계약 및 검색 최적화 |
| **키보드 접근성, ARIA, 포커스, WCAG 2.2 표준** | [`docs/accessibility-guidelines.md`](docs/accessibility-guidelines.md) <br> `.agents/skills/accessibility/` | 웹 접근성 표준(WCAG 2.2), 스크린 리더, 반응형 규칙 |
| **성능 최적화, Core Web Vitals, 웹 품질 감사** | [`docs/deployment-guidelines.md`](docs/deployment-guidelines.md) <br> `.agents/skills/web-quality-audit/` <br> `.agents/skills/core-web-vitals/` <br> `.agents/skills/performance/` | Lighthouse 종합 감사, LCP/CLS/INP 최적화 지침 |
| **빌드, Vercel 정적 배포, GitHub Actions, dist/** | [`docs/deployment-guidelines.md`](docs/deployment-guidelines.md) | `python3 scripts/build.py`, 배포 규칙 |
| **모델 적합성 점검, 위험도 라우팅, 사후 검증** | [`docs/agent-policy/model-routing.md`](docs/agent-policy/model-routing.md) | 위험도 3단계, 사전 점검 게이트, 검증 모델 권한, PASS/FAIL 루프 |

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
- 승인된 5종 페이지 유형(`landing`, `static-prompt`, `prompt-builder`, `markdown-prompt`, `practice-timeline`) 외의 새 유형 임의 추가 금지
- 생성된 테마 파일이나 `dist/` 결과물 직접 수정 금지
- **아키텍처 및 핵심 구조 변경 금지**: `site.css`의 핵심 레이아웃(`.prompt-item` 등)뿐만 아니라, **현재 프로젝트 아키텍처, 컴포넌트 구조, 데이터 흐름 등에 변경이 발생한다고 판단되는 모든 경우** 임의 수정이 절대 금지됩니다. 반드시 리포팅 및 수정 계획을 제출하고 사용자의 사전 허락을 구해야 합니다.
- **임의 깃허브 푸시 금지**: 작업이 완료되었거나 '계획 승인(Proceed)'을 받았더라도, 사용자가 "깃허브에 푸시해 줘"라고 별도로 명시적인 지시를 내리기 전까지는 **임의로 `git push`를 실행하지 않습니다.**

---

## 6. 검증 및 작업 로그

- 저장소 파일을 변경한 작업은 단일 로그 파일(`agent-logs/YYYY-MM-DD-모델이름/progress-log.md`)에 진행 상황, 변경 내역, 빌드 검증 결과를 축적 기록합니다.
- **사고 보고서 (Incident Reports)**: 문제 발생 또는 실패 사례에 대한 보고서는 `agent-logs/incident-reports/` 폴더에 별도로 보관합니다. (참고: [프롬프트 카드 상단 간격 문제 실패보고서](agent-logs/incident-reports/2026-07-28-failure-report.md))
- **레이아웃 및 UI 사이드 이펙트(Side Effect) 체크 필수**: CSS, 마진, 패딩, 컴포넌트 레이아웃 변경 시 단일 페이지만 보지 않고 공통 컴포넌트 및 연관 페이지 전체의 시각적 렌더링 부작용(여백 벌어짐, 찌그러짐 등)을 브라우저 스크린샷으로 사전에 반드시 교차 점검합니다.
- 수정 후 반드시 `python3 scripts/build.py`를 실행하여 빌드 정상 여부를 검증합니다.

## 6.4 작업 전 모델 적합성 점검 및 위험도 라우팅 (사전 게이트)

- **사전 적합성 점검 의무**: 모든 구현·수정 작업 착수 전 요구사항의 위험도(High/Medium/Low)와 추론 난이도를 분석하여 모델 수준을 선판단합니다. (세부 분류 기준 및 보고 양식: [`docs/agent-policy/model-routing.md`](docs/agent-policy/model-routing.md))
- **고위험 작업 착수 차단**: 고위험 작업(예: 아키텍처, 빌드 계약, 다중 모듈, API/데이터 스키마, 공통 템플릿/CSS, 보안/배포 파이프라인 등 전체 범위는 [`docs/agent-policy/model-routing.md`](docs/agent-policy/model-routing.md) 기준)은 상위 추론 모델의 사전 분석 없이 실질적인 수정을 시작하지 않습니다.
- **상위 모델 부재 시 Fallback & Override**: 자동 전환 불가 환경의 고위험 작업은 사용자에게 제한 사항을 선보고하며, 사용자의 명시적 승인(Override) 전에는 수정을 착수하지 않습니다. Override 시 로그 기록 및 엄격한 보완 검증을 수행합니다.
- **증거 기반 사후 검증 및 루프**: 실질적 변경 완료 후 독립 상위 검증 모델 또는 명시적인 보상 검증 체크리스트를 통해 테스트/빌드/diff 기반 `PASS` 판정을 확인하며, 결함 발견 시 재검증 루프를 수행합니다.


---

## 7. 프롬프트 마크다운 작성 및 무결성 라우팅 (Mandatory Policy)

프롬프트 페이지를 생성·수정하거나 관련 메타데이터/에셋을 다룰 때는 반드시 아래 정책 문서를 지연 로딩(Lazy-Loading)하여 엄수합니다.

- **프롬프트 상세 규격**: [`docs/prompt-page-guidelines.md`](docs/prompt-page-guidelines.md)
  - **인라인 콤보박스**: 자유 텍스트 입력 필드는 반드시 `"[텍스트 입력]"` 양쪽 따옴표 필수, 드롭다운 내 `"[자유 입력]"` 생성 금지
  - **마크다운 서식**: 볼드(`**`) 서식 최소화, `- 옵션명: 설명` 단일 라인(Flat) 구조, `- ` 마커 통일
  - **콤보박스 기본값**: 구도/비율 1순위(`원본 사진 비율 유지`), 화풍/색감 대표 옵션 1순위 배치
  - **선조사 의무**: 수정 전 최근 3개 커밋 내역(`git log -p -n 3`) 필수 확인 및 사용자 커스텀 메타데이터 보존
- **데이터 및 이미지 무결성**: [`docs/content-guidelines.md`](docs/content-guidelines.md)
  - `page-registry.json` & `navigation.json` 제목/설명문 동기화 (`core/data_consistency.py`)
  - 신규 이미지 추가 시 `python3 scripts/optimize_images.py --replace` 실행 필수 (WebP 변환, 최대 1MB)
  - 프롬프트 적합성 진단: `python3 scripts/audit_prompts.py`



