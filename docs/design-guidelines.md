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

### 컴포넌트 개발 규칙 (Component First)
- 동일한 목적의 마크업과 동작을 페이지마다 중복 복제하지 않습니다.
- 새로 만들기 전에 기존 컴포넌트의 재사용 가능성을 확인합니다.
- 단순 wrapper 용도로 불필요한 컴포넌트를 만들지 않습니다.
- 컴포넌트는 명시적인 데이터를 입력받으며, 하드코딩하지 않습니다.
- 사용자 입력 및 편집 문구는 `textContent`를 우선 사용하여 XSS 방지 및 안전성을 확보합니다.
