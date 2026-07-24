# 작업 진행 및 검증 기록 (Progress Log)

- **작업 일시**: 2026-07-24
- **모델**: GPT-5
- **작업 내용**:
  1. `ai-practice`와 `ai-assistant` 하위 페이지 생성
  2. `data/navigation.json`, `data/page-registry.json`, `core/navigation.py`, `core/page_registry.py`를 새 구조에 맞게 정렬
  3. 새 페이지들에 `prompt` 블록을 추가해 렌더러 계약 충족

---

## 1. 추가/수정 파일
- `pages/sections/ai-practice/zero-to-final.md`
- `pages/sections/ai-practice/prompt-techniques.md`
- `pages/sections/ai-assistant/project-guide.md`
- `pages/sections/ai-assistant/gem-guide.md`
- `data/navigation.json`
- `data/page-registry.json`
- `core/navigation.py`
- `core/page_registry.py`

## 2. 검증
- `python3 scripts/build.py --check` 통과
- 결과: Pages 11 / Assets 6 / Routes 11
