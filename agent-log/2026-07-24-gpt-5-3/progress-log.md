# 작업 진행 및 검증 기록 (Progress Log)

- **작업 일시**: 2026-07-24
- **모델**: GPT-5
- **작업 내용**:
  1. `ai-practice`와 `ai-assistant` 하위 페이지 추가
  2. `data/navigation.json` 및 `data/page-registry.json`에 하위 메뉴 연결
  3. 상위 메뉴 정의와 실제 구조를 일치시킴

---

## 1. 추가한 페이지
- `pages/sections/ai-practice/zero-to-final.md`
- `pages/sections/ai-practice/prompt-techniques.md`
- `pages/sections/ai-assistant/project-guide.md`
- `pages/sections/ai-assistant/gem-guide.md`

## 2. 검증 계획
- `python3 scripts/build.py --check`
