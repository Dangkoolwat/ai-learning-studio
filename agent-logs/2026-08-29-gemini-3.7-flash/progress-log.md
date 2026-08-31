# 2026-08-29 작업 로그 (Gemini 3.7 Flash)

## 1. 작업 개요
- 피드백 기반 Phase A~C 미달 항목 및 배포 위험(CSP) 정밀 정리 완료:
  1. 배포 위험 CSP 원천 제거 (`vercel.json` 롤백)
  2. Phase A 문서 잔여 모순 완전 해소 (`prompt-page-guidelines.md`, `PROJECT.md`, `AGENTS.md`)
  3. Phase B `scripts/audit_prompts.py` 코어 모듈 재사용, 섹션 헤더 오경고 해소, 실패 경로 단위 테스트(`tests/test_audit_prompts.py`) 구축 및 `--strict` 완전 통과
  4. Phase C 도구 목록 및 CI 정돈 (`README.md`, `.github/workflows/quality-check.yml`, 불필요한 테스트 정리)

## 2. 세부 변경 내역
- **배포 안전성 확보 (CSP 롤백)**:
  - `vercel.json`: 인라인 테마/복원 스크립트 및 Google Fonts 차단 위험이 있는 `Content-Security-Policy` 헤더 완전 제거
- **데이터 및 템플릿/UI 개선**:
  - `core/navigation.py`: `NavigationSubItem`에 `featured: bool = False` 속성 및 유효성 검사 추가
  - `core/template_engine.py`: `sub.featured` 활성화 시 `<span class="sub-nav-badge--featured">추천</span>` 렌더링 지원
  - `assets/css/site.css`: `.sub-nav-badge--featured` 추천 배지 스타일 추가
  - `data/navigation.json`: 5대 메인 메뉴(상위 섹션) 전반에 걸쳐 핵심 대표 프롬프트에 `featured: true` 추천 플래그 확대 반영
  - `vercel.json`: HTML 즉시 갱신을 위한 `Cache-Control: public, max-age=0, must-revalidate` 헤더 추가 (CDN/브라우저 캐시 잔류 방지 자동화)
  - `templates/partials/head.html`, `assets/js/navigation.js`: 상단 홈 링크 클릭 시 이전 경로로 강제 리디렉션되던 버그 해소 (마지막 방문 경로 가로채기 스크립트 제거)
  - `data/navigation.json`: `silly-doodle`, `sketch-sticker` 추천 뱃지 추가 반영
  - `data/navigation.json`, `data/page-registry.json`, `summer-vacation-basic.md`: '여름휴가 계획 세우기 (기초편)'으로 라벨/제목 3자 동기화 단축 반영
  - `pages/index.md`, `pages/sections/image-ai/recipe-infographic.md`: 레지스트리와 불일치하던 description 동기화
  - `pages/sections/image-ai/food-poster.md`, `pages/sections/ready-to-use/uijeongbu-route-finder.md`, `pages/sections/ai-practice/uijeongbu-oneday-tour.md`, `pages/sections/ready-to-use/event-budget-calculator.md`: 드롭다운 내 중복 '직접 입력' 옵션 제거 및 텍스트 플레이스홀더 정리
- **문서 및 기준서 잔여 모순 해소**:
  - `docs/prompt-page-guidelines.md`: 1행 3종 잔여 문구를 "5가지 공식 승인 페이지 유형"으로 수정, `landing` 설명을 "홈 랜딩"으로 정정
  - `PROJECT.md`: `page-registry.json` 스키마 키 설명을 `entries`에서 실제 JSON 스키마인 `pages`로 정정, `prompt-builder` 계약 명세 복원
  - `AGENTS.md`: `python3 scripts/audit_prompts.py` 명확한 실행 명령어 명시
  - `README.md`: 단위 테스트 및 빌드 검증 섹션에 `python3 scripts/audit_prompts.py --strict` 추가
- **프롬프트 감사 스크립트 및 테스트 스위트 강화**:
  - `scripts/audit_prompts.py`: `core.data_consistency`, `core.page_registry`, `core.navigation` 재사용 및 `_is_section_header` 로직을 활용하여 정상 섹션 헤더에 대한 오경고를 원천 제거하고, 드롭다운 옵션 내 금지 키워드 및 대용량 자산 정밀 검출
  - `tests/test_audit_prompts.py`: 실제 저장소 검증뿐만 아니라 빈 preview, 누락 이미지, 빈 source, 대용량 이미지, 드롭다운 금지 키워드 시 exit 1 실패 경로 증명 테스트 구현 (7개 테스트 케이스)
- **CI 워크플로우 정돈**:
  - `.github/workflows/quality-check.yml`: Node.js 스텝 제거 및 `python3 scripts/audit_prompts.py --strict` 연동으로 순수 Python 빌드/검증 파이프라인으로 단정화
  - `tests/test_prompt_copy.mjs`: 정리 완료

## 3. 최종 검증 결과
- `ruff check core scripts tests`: 통과 (All checks passed)
- `python3 -m unittest discover -s tests`: 71개 테스트 전원 통과 (Ran 71 tests in 1.662s, OK)
- `python3 scripts/audit_prompts.py --strict`: 71개 페이지 및 37개 이미지 자산 엄격 감사 통과 (0 errors, 0 warnings)
- `python3 scripts/build.py`: 71개 정적 페이지 정상 빌드 및 dist 발행 완료
- `python3 scripts/build.py --check`: 빌드 무결성 검증 통과

---

## 4. `palette-knife-impasto.md` 출처 메타데이터 변경 및 배포 (22:38)
- **변경 사항**:
  - `pages/sections/image-ai/palette-knife-impasto.md`: `source: Threads (@jelly.ppori)` -> `source: Threads (@foodibear_)`
- **검증 결과**:
  - `python3 scripts/build.py`: 71개 페이지 정상 빌드 완료
  - `python3 scripts/audit_prompts.py`: 전수 감사 정상 통과
- **배포 및 Git 동기화**:
  - Commit: `ab4eb6e` (`docs(prompt): palette-knife-impasto 출처 정보 변경 (@foodibear_)`)
  - Push: `origin/main` 푸시 완료 (`55dc742..ab4eb6e`)

