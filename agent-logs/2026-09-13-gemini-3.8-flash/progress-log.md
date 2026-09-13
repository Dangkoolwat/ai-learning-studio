# Progress Log - Vercel Web Analytics Integration

- **Date**: 2026-09-13
- **Model**: Gemini 3.8 Flash (High)
- **Task**: Vercel Web Analytics 가이드 검토 및 정적 아키텍처 호환 연동 (CSP 설정 및 인라인 스크립트 최적화)

---

## 1. 개요 및 요구사항 분석
- 사용자가 제공한 Vercel Web Analytics 설정 및 레퍼런스 구현 반영.
- Python 정적 사이트 빌더(`scripts/build.py`) 기반 순수 HTML/Vanilla JS 아키텍처에 맞추어 의존성 없이 구성.
- 프로젝트 빌드 제약(`len(executable_scripts) <= 2`)을 준수하기 위해 기존 `<head>` 인라인 스크립트 블록 내부에 `window.va` 및 DOM 스크립트 동적 주입 로직을 통합.
- Vercel Analytics 전용 CDN 및 수집 엔드포인트 차단 방지를 위해 `vercel.json`의 Content-Security-Policy(CSP) 정책 보강.

---

## 2. 변경 파일 및 상세 내역
- **[MODIFY] `templates/partials/head.html`**:
  - 기존 `<head>` 인라인 스크립트(`(function() { ... })();`) 블록 내부에 Vercel Web Analytics 로직 통합
  - 로컬 개발 환경(`localhost`, `127.0.0.1`, `file:`) 필터링을 통해 불필요한 404 콘솔 경고 방지
  - `window.va` 큐 함수 초기화 및 `/_vercel/insights/script.js` 상대 경로를 통해 동적 defer 주입
  - 추가 `<script>` 태그를 생성하지 않고 기존 인라인 블록 내부를 확장하여 빌드 파이프라인의 `executable_scripts` 개수 제약(정확히 2개) 완벽 충족
- **[MODIFY] `vercel.json`**:
  - `Content-Security-Policy` 헤더 업데이트
  - `script-src`에 `https://va.vercel-scripts.com` 추가
  - `connect-src`에 `https://va.vercel-analytics.com https://vitals.vercel-insights.com` 추가

---

## 3. 검증 결과
- **정적 빌드 검증**: `python3 scripts/build.py`
  - Exit code: `0`
  - 산출물: Pages: 77, Assets: 60, Routes: 77 정상 생성
  - 빌드 파이프라인(HTML 검증, 스크립트 개수 검증, 외부 URL 검사 등) 100% 통과
- **단위 테스트 검증**: `python3 -m unittest discover -s tests`
  - Exit code: `0`
  - Ran 89 tests in 2.396s -> OK (skipped=3) 전원 통과

---

## 4. 후속 배포 및 Vercel 활성화 안내
- Vercel 대시보드 프로젝트의 [Analytics] 탭에서 **Enable Web Analytics** 활성화
- Git 커밋 및 배포 후 브라우저 개발자 도구(Network 탭)에서 `/_vercel/insights/view` 요청 정상 전송 확인
