# 데이터 및 콘텐츠 가이드라인

이 문서는 **AI Learning Studio** 프로젝트의 데이터 구조, 파일 배치, 데이터 작성 원칙을 다룹니다.

---

## 1. 디렉토리 및 데이터 구조

```text
data/
├─ navigation.json       # 사이트 전체 내비게이션 메뉴 및 계층 구조
└─ page-registry.json    # 정적 페이지 등록 레지스트리 및 메타데이터

pages/
├─ index.md              # 메인 랜딩 페이지 마크다운
└─ sections/             # 섹션 허브 및 카테고리별 강의/프롬프트 마크다운 (.md)
   ├─ ai-assistant.md    # AI 어시스턴트 섹션 허브
   ├─ ai-assistant/      # AI 어시스턴트 상세 페이지 디렉토리
   ├─ ai-practice.md     # AI 실전 연습 섹션 허브
   ├─ ai-practice/       # AI 실전 연습 상세 페이지 디렉토리
   ├─ image-ai.md        # 이미지 AI 섹션 허브
   ├─ image-ai/          # 이미지 AI 상세 페이지 디렉토리
   ├─ prompt-snippets.md # 프롬프트 모음 섹션 허브
   ├─ prompt-snippets/   # 프롬프트 모음 상세 페이지 디렉토리
   ├─ ready-to-use.md    # 바로 쓰는 실전 프롬프트 섹션 허브
   └─ ready-to-use/      # 바로 쓰는 실전 프롬프트 상세 페이지 디렉토리

templates/
├─ base.html             # 기본 레이아웃 템플릿
└─ partials/             # 공통 부분 템플릿
   ├─ head.html          # 메타태그, 폰트, 공통 에셋 링크
   ├─ site-header.html   # 상단 브랜드 로고, 테마 토글, 햄버거 메뉴
   ├─ navigation.html    # 사이드바 메뉴 및 실시간 검색 입력부
   └─ footer.html        # 하단 푸터

components/              # 렌더러용 재사용 가능 UI 컴포넌트 템플릿
├─ prompt-item.html      # 프롬프트 카드 템플릿
├─ prompt-builder.html   # 프롬프트 조립기 템플릿
├─ prompt-field.html     # 조립기 컨트롤 필드
├─ practice-timeline.html# 타임라인 컨테이너
├─ timeline-step.html    # 타임라인 단계 항목
├─ image-slider.html     # 전/후 이미지 비교 슬라이더
├─ prompt-collection.html# 프롬프트 모음 박스
├─ page-intro.html       # 페이지 소개부
└─ page-body.html        # 본문 영역

assets/
├─ css/site.css          # 공통 스타일시트
├─ js/                   # Vanilla ES 모듈 클라이언트 스크립트
│  ├─ site.js            # 진입점 스크립트
│  ├─ prompt-copy.js     # 프롬프트 복사 및 인라인 칩 제어
│  ├─ prompt-builder.js  # 프롬프트 조립기 제어
│  ├─ navigation.js      # 내비게이션 및 사이드바 제어
│  ├─ theme-toggle.js    # 테마 토글 제어
│  ├─ image-slider.js    # 이미지 비교 슬라이더
│  ├─ image-lightbox.js  # 이미지 라이트박스
│  └─ dom-utils.js       # 공통 DOM/클립보드 유틸리티
├─ images/               # 최적화된 WebP 이미지 리소스
└─ favicon.svg           # 사이트 파비콘
```

---

## 2. 데이터 분리 및 무결성 원칙 (Data First)

- **책임 분리**: 사이트 내비게이션 메뉴와 페이지 등록 정보는 `data/` 하위 JSON(`navigation.json`, `page-registry.json`)으로 관리하고, 본문 콘텐츠는 `pages/` 하위 마크다운(`.md`)으로 작성하여 Python 빌드 시 읽어서 정적 HTML로 합성합니다.
- **순수 데이터 유지**: JSON 내부에는 실행 가능한 JavaScript 함수, 이벤트 핸들러, HTML 마크업 문자열을 포함하지 않습니다.
- **경로 일관성 계약**:
  ```text
  navigation path == page registry path == canonical path == sitemap URL
  ```
  모든 경로는 **소문자 kebab-case**와 **trailing slash (`/`)** 형태를 유지해야 합니다.
- **사실에 기반한 콘텐츠**: 실제 존재하지 않는 무분별한 가짜 강좌, 후기, 작성자 경력, 통계 데이터를 허위 생성하지 않습니다.

---

## 3. 이미지 리소스 관리 규칙 (Image Assets)

- 페이지에서 사용되는 모든 예제 이미지와 리소스는 `assets/images/<상위메뉴이름>/<페이지이름>/` 디렉토리에 저장해야 합니다.
  - 예시: `assets/images/image-ai/typography/example-1.webp`
- 파일명은 소문자와 하이픈(`-`)만을 사용하여 페이지 맥락을 알 수 있도록 명확하게 지정합니다.
- **WebP 포맷 의무 및 최적화**: 웹 성능 및 LCP(Largest Contentful Paint) 최적화를 위해 이미지는 **반드시 WebP 포맷**을 사용해야 합니다.
  - 신규 PNG/JPG 이미지를 추가한 후에는 **`python3 scripts/optimize_images.py --replace`**를 실행하여 WebP 변환 및 대용량 원본 정리를 수행해야 합니다.
  - 모든 바이너리 이미지는 **파일당 최대 1MB 이하**여야 하며, 초과 시 빌드 파이프라인에서 자동으로 차단됩니다.

