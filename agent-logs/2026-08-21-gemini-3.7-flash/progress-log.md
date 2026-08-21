# 2026-08-21 신규 페이지 추가 작업 로그

## 작업 개요
- **콘텐츠명**: `경험을 나만의 자산으로 바꾸기`
- **목적**: Naval Ravikant의 Specific Knowledge / Leverage 개념을 기반으로, 개인의 경험과 노하우를 휘발되지 않는 고유 자산(콘텐츠, 템플릿, 가이드, 도구 등)으로 축적하는 6단계 '프롬프트 한 스푼' 신규 페이지 신설.
- **수행 모델**: Gemini 3.7 Flash

---

## 변경 내역
1. **신규 마크다운 페이지 생성 및 기획 배경/철학 보강**
   - `pages/sections/prompt-snippets/experience-to-asset.md`
   - 제목에 추천 별표(`⭐`) 추가 반영 (`경험을 나만의 자산으로 바꾸기 ⭐`)
   - Naval Ravikant 4대 개념 및 프롬프트 한 스푼 지향점 서두 단락 반영
   - 대표 프롬프트 (`내 경험 속 숨은 강점 찾기`) 및 심층 진단 1종 + 추가 프롬프트 5종 구성
   - 출처 및 참고 문헌 명시 (`X @TheWhizzAI WEALTH PROTOCOL / Naval Ravikant`)
2. **4각 메타데이터 동기화 완료 (`⭐` 반영)**
   - `data/page-registry.json`
   - `data/navigation.json`
   - `core/page_registry.py`
   - `core/navigation.py`

---

## 빌드 및 검증 결과
- 빌드 명령어: `python3 scripts/build.py` (Exit code 0, 58개 페이지 정상 생성)

---

# 2026-08-21 이미지 프롬프트 신규 페이지 추가 작업 로그

## 작업 개요
- **콘텐츠명**: `사진 속 인물만 손그림 스티커로 바꾸기` (`image-ai-sketch-sticker`)
- **목적**: 배경 사진은 원본 그대로 유지하고, 사진 속 인물만 흰색 테두리가 있는 흑백 손그림 스티커 일러스트로 자연스럽게 합성하는 이미지 프롬프트 페이지 신설 및 명칭 정돈.
- **수행 모델**: Gemini 3.7 Flash

---

## 변경 내역
1. **예시 이미지 자산 배치**
   - `assets/images/image-ai/sketch-sticker/sketch-sticker1.jpg` (계단 뒷모습 예시)
   - `assets/images/image-ai/sketch-sticker/sketch-sticker2.jpg` (펜스 앞 앞모습 예시)
2. **신규 마크다운 페이지 생성 및 기본값/프롬프트 정돈**
   - `pages/sections/image-ai/sketch-sticker.md`
   - 페이지 및 프롬프트 제목: `사진 속 인물만 손그림 스티커로 바꾸기`
   - 출처 메타데이터 보존: `source: Threads (@nature.soul2025)`
   - 사용자 기본값 최적화 반영:
     - 손그림 스타일: `만화 선화` (1순위 기본값)
     - 선 느낌: `굵고 또렷하게` (1순위 기본값)
   - 스티커 톤앤매너 최적화 지침 보강:
     - 표현 단순화(얼굴/의상 특징 위주 간결한 선화), 선화 강조(미세 주름/피부 질감 최소화), 과도한 사실적 크로스해칭 방지 지침 추가 반영
3. **4각 메타데이터 동기화 완료**
   - `data/page-registry.json`
   - `data/navigation.json`
   - `core/page_registry.py`
   - `core/navigation.py`

---

## 빌드 및 검증 결과
- **빌드 테스트**: `python3 scripts/build.py` (Exit code 0, 총 59개 페이지 정상 생성)
- **결과물 검증**: `dist/image-ai/sketch-sticker/index.html` 내 인라인 콤보박스 기본값(`만화 선화`, `굵고 또렷하게`) 및 세부 지시문 정상 반영 확인
