# 디자인 및 컴포넌트 가이드라인

이 문서는 **AI Learning Studio** 프로젝트의 정보 구조, 테마 시스템, 시각 디자인 원칙 및 공통 컴포넌트 규칙을 다룹니다.

---

## 1. 정보 구조 (Information Architecture)

### 상위 영역 (Top-Level Domains)
1. 🧪 **AI 체험 실습** - 하나의 주제를 제로샷에서 시작해 프롬프트를 단계적으로 보강하며 최종본을 완성하는 체험형 메뉴
2. ⚡ **바로 사용하기** - 바로 복사해서 쓸 수 있는 완성형 프롬프트 제공 메뉴
3. 🤖 **AI 도우미** - Project나 GEM 전용 지침서 프롬프트를 범용 템플릿 형태로 제공하는 메뉴
4. 🎨 **이미지 AI** - 이미지 생성용 프롬프트 허브, 상위에서는 개념과 차이를 설명하고 하위에서 세부 유형으로 확장

> **주의**: 상위 영역과 메뉴 구조는 사용자 승인 없이 변경하지 않습니다.

### 내비게이션 레이아웃
- **데스크톱**: 왼쪽 목적 기반 내비게이션, 오른쪽 작업 페이지 (메뉴 깊이 최대 2단계)
- **모바일**: 내비게이션 패널/drawer, 데스크톱과 동일한 메뉴 데이터 사용 (별도 모바일 전용 메뉴 트리 금지)

---

## 2. 테마 시스템 (Theme System)

### 파일 및 관리 구조
- **원본 (사람 관리)**: `design/<theme-name>/design.md`
- **Python 빌드 결과물**:
  ```text
  design/<theme-name>/
  ├─ design.md
  ├─ tokens.json
  ├─ style.css
  └─ manifest.json
  ```
- **배포 경로**: `dist/assets/themes/<theme-name>/style.css`
- **사이트 테마 등록**: `data/themes.json`

### 테마 원칙
- `design.md`가 수정의 단일 원본(Single Source of Truth)입니다. 생성된 `tokens.json`, `style.css` 등을 직접 수정하지 않습니다.
- 테마는 **외형(CSS 시각 토큰)**만 변경하며, IA, 레이아웃 구조, 기능, 접근성을 변경해서는 안 됩니다.
- 테마 선택기는 데스크톱 왼쪽 아래, 모바일 설정 패널에 위치시킵니다.
- 지원 테마 스펙트럼: Studio Warm, Studio Neutral, Neutral Light/Dark (과도한 보라색 AI 그라데이션 금지).
- **모던 UI/UX 디자인 원칙 (`frontend-design`, `web-design-guidelines` 연계)**:
  - 뻔한 AI 템플릿 느낌을 지양하고, 절제된 타이포그래피(레터스페이싱, 폰트 두께 계층), 1px 미세 보더, 레이어드 섀도우를 적용합니다.
  - 마이크로 인터랙션(버튼 클릭/호버 시 스프링 피드백, 복사 상태 시각화)을 통해 인터페이스 반응성을 극대화합니다.
  - 다크 테마 적용 시 완전한 블랙 대신 징크/차콜 톤과 미세한 경계선을 사용하여 눈의 피로를 줄이고 프로페셔널한 느낌을 유지합니다.

---

## 3. 공통 컴포넌트 (Common Components)

### 페이지 렌더러
- `StaticPromptPage`
- `PromptBuilderPage`
- `PracticeTimelinePage`

### 공통 컴포넌트 목록
- `PromptDisplay`
- `CopyButton`
- `ExternalAiActions`
- `PromptField`
- `PromptResult`
- `PracticeStep`
- `EmptyResult`
- `ValidationMessage`

### 컴포넌트 개발 및 레이아웃 수정 규칙 (Side Effect Verification)
- 동일한 목적의 마크업과 동작을 페이지마다 중복 복제하지 않습니다.
- 새로 만들기 전에 기존 컴포넌트의 재사용 가능성을 확인합니다.
- 단순 wrapper 용도로 불필요한 컴포넌트를 만들지 않습니다.
- 컴포넌트는 명시적인 데이터를 입력받으며, 하드코딩하지 않습니다.
- 사용자 입력 및 편집 문구는 `textContent`를 우선 사용하여 XSS 방지 및 안전성을 확보합니다.
- **레이아웃 & 시각적 사이드 이펙트(Side Effect) 사전/사후 검증 필수**: CSS(마진, 패딩, gap, z-index 등) 및 레이아웃 구조를 변경할 때는 수정 대상 페이지 외에 다른 템플릿/페이지로 퍼질 수 있는 부작용(여백 벌어짐, 레이아웃 찌그러짐 등)을 브라우저 스크린샷 렌더링 검사로 반드시 사전/사후 교차 점검합니다.
