# 데이터 및 콘텐츠 가이드라인

이 문서는 **AI Learning Studio** 프로젝트의 데이터 구조, 파일 배치, 데이터 작성 원칙을 다룹니다.

---

## 1. 디렉토리 및 데이터 구조

```text
data/
├─ site.json       # 사이트 전깃 기본 메타정보
├─ menu.json       # 사이트 전체 내비게이션 메뉴 구조
├─ pages.json      # 정적 페이지 등록 레지스트리
└─ themes.json     # 테마 목록 등록 파일

pages/<slug>/
├─ page.json       # 해당 페이지 콘텐츠 데이터 (또는 <slug>.json)
├─ README.md       # 페이지 관련 작성자 문서
└─ assets/         # 페이지 전용 리소스

templates/
├─ base.html              # 기본 레이아웃 템플릿
├─ static-prompt.html     # static-prompt 페이지 템플릿
├─ prompt-builder.html    # prompt-builder 페이지 템플릿
└─ practice-timeline.html # practice-timeline 페이지 템플릿
```

---

## 2. 데이터 분리 및 무결성 원칙 (Data First)

- **책임 분리**: 사이트 메타데이터, 메뉴, 페이지 목록, 테마 데이터는 `data/` 하위 JSON으로 분리하고 Python 빌드 시 읽어서 정적 HTML로 합성합니다.
- **순수 데이터 유지**: JSON 내부에는 실행 가능한 JavaScript 함수, 이벤트 핸들러, HTML 마크업 문자열을 포함하지 않습니다.
- **경로 일관성 계약**:
  ```text
  menu path == page registry path == canonical path == sitemap URL
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

