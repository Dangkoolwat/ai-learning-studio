# 작업 로그: 2026-08-22 (Gemini 3.7 Flash)

## 1. 개요 및 목적
- 프로젝트 코드 감사(Audit) 결과 제기된 핵심 기술 부채 3가지 개선 사항 검증 및 3번 과제(이미지 WebP 최적화 및 LCP 개선) 완수.

## 2. 세부 작업 내역

### 1) 4각 동기화 해소 및 SSOT 단일화 (이전 작업자 완료분 검증)
- `core/page_registry.py`, `core/navigation.py`의 하드코딩 상수(`EXPECTED_PAGES`, `EXPECTED_SECTIONS`) 제거.
- `core/data_consistency.py` 신설: 빌드 시 `navigation.json`과 `page-registry.json` 간 상호 정합성 자동 검증.
- `AGENTS.md` 규칙 갱신.

### 2) 단위/통합 테스트 스위트 구축 (이전 작업자 완료분 검증)
- Python stdlib `unittest` 기반 `tests/` 스위트 구축 (`test_build_smoke.py`, `test_data_consistency.py`, `test_navigation.py`, `test_page_registry.py`).

### 3) 이미지 WebP 변환 및 LCP 최적화 (3번 과제 수행)
- **변환 스크립트 작성**: `scripts/optimize_images.py` 추가 (Pillow 기반 WebP 품질 85, 최대 해상도 1600px 리사이즈).
- **이미지 에셋 일괄 최적화**: 24개 PNG/JPG 파일 전체를 WebP로 변환 교체.
  - 총 용량: **24.65MB → 3.14MB (87.3% 절감)**
  - 1MB 초과 파일: **12개 → 0개** (최대 크기 283KB)
- **마크다운 Frontmatter 및 본문 경로 동기화**:
  - `pages/sections/ai-practice/fridge-recipe.md` (3개 이미지)
  - `pages/sections/image-ai/*.md` 9개 파일 (`preview:` 메타데이터)
- **빌드 파이프라인 방어 로직 추가**:
  - `core/build_pipeline.py`: `MAX_IMAGE_ASSET_BYTES = 1024 * 1024` (1MB) 상수 정의 및 `validate_static_asset` 내 1MB 초과 바이너리 이미지 차단 로직 구현.
- **이미지 테스트 스위트 확장**:
  - `tests/test_image_assets.py` 신설 (1MB 이하 검증, preview/본문 디스크 실존 검증, 초과 시 BuildError 발생 검증).

## 3. 검증 결과
- **단위 테스트**: `python3 -m unittest discover -s tests -p "test_*.py" -v` -> **44/44 PASSED (1.08s)**
- **정적 빌드**: `python3 scripts/build.py` -> **59개 페이지, 35개 에셋 빌드 성공 (Exit Code 0)**
- **결과물 용량**: `dist/assets/images/` 전체 용량 3.2MB 확인.
