# SEO (검색엔진 최적화) 가이드라인

이 문서는 **AI Learning Studio** 프로젝트의 모든 정적 HTML 페이지가 준수해야 하는 SEO 규칙과 계약을 다룹니다.

---

## 1. 정적 HTML & 초기 본문 보존 (SEO First)

- **초기 HTML 렌더링**: 검색엔진 크롤러가 클라이언트 JS 실행 없이 본문을 읽을 수 있도록 핵심 콘텐츠가 초기 HTML 파일에 포함되어야 합니다.
- **SPA Fallback 금지**: 모든 URL 요청을 하나의 `index.html`로 밀어넣는 SPA catch-all rewrite 방식을 절대 금지합니다.

---

## 2. 필수 페이지 메타데이터 요소

모든 공개 정적 페이지는 Python 빌드 단계에서 다음 요소를 올바르게 생성해야 합니다.

1. **고유 Title 및 Description**: 페이지별로 중복되지 않는 명확한 title 및 meta description.
2. **Canonical URL**: 정식 운영 도메인 기준의 표준 URL (Vercel Preview URL을 canonical로 설정 금지).
3. **Open Graph & Twitter Card**: 소셜 공유용 메타태그 (og:title, og:description, og:image 등).
4. **JSON-LD 구조화 데이터**: 페이지 성격에 부합하는 Schema.org JSON-LD 스크립트.
5. **Heading 계층구조**: 페이지당 단 하나의 `<h1>` 요소 사용 및 논리적 `<h2>`, `<h3>` 순서 준수.
6. **Breadcrumb**: 홈 이외의 모든 하위 경로에 Breadcrumb 마크업 및 JSON-LD 제공.
7. **사이트맵 및 크롤링 정책**: `sitemap.xml` 및 `robots.txt`에 정식 등록.
