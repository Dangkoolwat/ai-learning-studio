# Progress Log: 2026-08-28

## 작업 내용: AGENTS.md 및 가이드라인에 볼드(`**`) 서식 최소화 규칙 영구 등록 완료

### 1. 작업 개요
* **목적**: 불필요한 `**` 볼드 기호 남발을 방지하고 단정한 플랫 텍스트 표준을 유지하도록 `AGENTS.md` 및 `docs/prompt-page-guidelines.md`에 영구 규칙 등록.
* **적용 파일**:
  1. `AGENTS.md` (제7조에 '볼드 마크다운 서식 최소화 및 평문화 규칙' 추가)
  2. `docs/prompt-page-guidelines.md` (제4조 '프롬프트 마크다운 작성 및 서식 규칙' 신설)

### 2. 검증 결과
* `python3 scripts/build.py`: 정상 완료 (70개 페이지 생성, Exit Code 0)
* `python3 -m unittest discover tests`: 전체 64개 단위 테스트 ALL PASS (Exit Code 0)

### 3. 상태
* **완료 (Ready for Deployment)**

---

## 작업 내용: '사진을 팔레트 나이프 임파스토 유화로 만들기' 신규 프롬프트 페이지 추가 및 등록

### 1. 작업 개요
* **목적**: Threads @jelly.ppori 출처의 '사진을 팔레트 나이프 임파스토 유화로 만들기' 프롬프트를 신규 `static-prompt` 페이지로 등록하고, 업로드된 4개의 샘플 이미지를 표준 컨벤션(`palette-knife-impasto1.webp` ~ `4.webp`)으로 리네임 후 `preview` 메타데이터에 등록.
* **적용 파일**:
  1. `pages/sections/image-ai/palette-knife-impasto.md` (신규 마크다운 페이지 및 preview 연동)
  2. `assets/images/image-ai/palette-knife-impasto/palette-knife-impasto[1-4].webp` (4개 샘플 이미지)
  3. `data/page-registry.json` (`image-ai-palette-knife-impasto` 등록, order: 60)
  4. `data/navigation.json` (`image-ai` 섹션에 신규 항목 추가)

### 2. 검증 결과
* `python3 scripts/build.py`: 정상 완료 (71개 페이지, 47개 에셋 생성, Exit Code 0)
* `python3 -m unittest discover -s tests`: 64개 단위 테스트 전체 통과 (Exit Code 0)

### 3. 상태
* **완료 (Ready for Deployment)**

---

## 작업 내용: 옵션 드롭다운 내 `"[자유 입력]"` 생성 금지 규칙 영구 제정 및 파일 정돈

### 1. 작업 개요
* **목적**: 프롬프트 선택 옵션(콤보박스) 작성 시 끝에 `"[자유 입력]"`, `"[직접 입력]"`을 관습적으로 추가하는 것을 금지하고, 검증된 구체적 프리셋 옵션으로만 구성하도록 규칙 제정 및 적용.
* **적용 파일**:
  1. `AGENTS.md` (제7조에 '옵션 드롭다운 내 `"[자유 입력]"` 생성 금지 규칙' 영구 등록)
  2. `docs/prompt-page-guidelines.md` (제4조 서식 규칙에 반영)
  3. `pages/sections/image-ai/palette-knife-impasto.md` (피사체 및 배경 옵션에서 `"[자유 입력]"` 제거)

### 2. 검증 결과
* `python3 scripts/build.py`: 정상 완료 (71개 페이지, 47개 에셋 생성, Exit Code 0)
* `python3 -m unittest discover -s tests`: 64개 단위 테스트 전체 통과 (Exit Code 0)

### 3. 상태
* **완료 (Ready for Deployment)**

---

## 작업 내용: '팔레트 나이프 임파스토 유화' 실전 활용 꿀팁(Quick Tips) 추가

### 1. 작업 개요
* **목적**: 배경 표현별 연출 가이드, 임파스토 강도 선택 기준, 사진 종류별 최적 추천 조합, 질감 보강 팁을 담은 실전 활용 꿀팁 섹션을 페이지 하단에 추가.
* **적용 파일**:
  1. `pages/sections/image-ai/palette-knife-impasto.md` (하단 `### 💡 실전 활용 꿀팁 (Quick Tips)` 섹션 추가)

### 2. 검증 결과
* `python3 scripts/build.py`: 정상 완료 (71개 페이지, 47개 에셋 생성, Exit Code 0)
* `python3 -m unittest discover -s tests`: 64개 단위 테스트 전체 통과 (Exit Code 0)

### 3. 상태
* **완료 (Ready for Deployment)**

---

## 작업 내용: '팔레트 나이프 임파스토 유화' 인물 정체성 보존 기준 정밀화

### 1. 작업 개요
* **목적**: 인물 변환 시 얼굴 뭉개짐 및 다른 인물로 변형되는 문제를 방지하기 위해 '인물 정체성 보존', '얼굴(섬세한 스트로크) vs 의상/헤어(과감한 임파스토) 분리', '얼굴 변형/미화 방지' 지침 반영.
* **적용 파일**:
  1. `pages/sections/image-ai/palette-knife-impasto.md` (`### 피사체 표현 기준` 내 인물 지침 정밀화)

### 2. 검증 결과
* `python3 scripts/build.py`: 정상 완료 (71개 페이지, 47개 에셋 생성, Exit Code 0)
* `python3 -m unittest discover -s tests`: 64개 단위 테스트 전체 통과 (Exit Code 0)

### 3. 상태
* **완료 (Ready for Deployment)**

