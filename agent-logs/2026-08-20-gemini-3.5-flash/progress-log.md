# 작업 진행 로그 - 2026-08-20 (Gemini 3.5 Flash)

## 작업 개요
- **작업명**: 사진을 어린이 손그림으로 바꾸기 프롬프트 페이지 추가 및 메뉴 등록
- **대상**: ChatGPT Images 2 및 Gemini(바나나2) 이미지 생성 모델 최적화 프롬프트
- **참고 출처**: Threads (`https://www.threads.com/share/KJdOZ8CYh/`)

## 상세 작업 내역

1. **이미지 리소스 복사**
   - 사용자 업로드 이미지를 `assets/images/image-ai/child-doodle/preview.jpg` 로 복사 완료.

2. **신규 프롬프트 마크다운 생성**
   - `pages/sections/image-ai/child-doodle.md` 신규 생성.
   - 드롭다운 선택 칩 포맷 적용 및 네거티브 지침(13항) 등 구조화.

3. **데이터 및 설정 파일 갱신**
   - `data/page-registry.json`에 `image-ai-child-doodle` (order: 54) 추가 및 `ai-practice-fridge-recipe` (order: 55) 조정.
   - `data/navigation.json`에 `image-ai-child-doodle` 서브아이템 추가 완료.

4. **파이썬 유효성 매핑 코드 동기화**
   - `core/page_registry.py` 내 `EXPECTED_PAGES` 상수 갱신.
   - `core/navigation.py` 내 `EXPECTED_SECTIONS` 상수 갱신.

5. **출력 비율(Ratio) 옵션 추가**
   - `child-doodle.md`에 `출력 비율` 옵션(`[원본 사진 비율 유지 / 1:1 정사각형 / 4:5 세로형 / 9:16 세로형 / 16:9 가로형]`) 및 본문 `11. 출력 비율 적용` 조항 추가.
   - 기존의 11~14번 지침을 12~15번으로 순차 리벨런싱 완료.

6. **사용자 직접 수정 사항 반영**
   - 사용자가 `child-doodle.md` 메타데이터 내 `ai_target`을 `ChatGPT,Gemini` 로 쉼표(,) 구분식으로 갱신하고, `description`을 가독성 높게 수정함.
   - 이에 따른 렌더링 검증 완료.

7. **"인물을 엉뚱한 낙서 캐릭터로 바꾸기" 추가**
   - `silly-doodle.md` 신규 프롬프트 마크다운 추가.
   - 기본값 튜닝(보통, 흑백 중심, 흰 종이 여백, 원본 비율)을 콤보박스 첫 순위에 배치.
   - `page-registry.json`, `navigation.json` 및 관련 파이썬 유효성 매핑 코드에 정합성 맞춰 등록 완료.
   - `assets/images/image-ai/silly-doodle/preview.jpg` 플레이스홀더 이미지 리소스 배치 후 사용자 실제 예제 이미지로 최종 갱신 완료.
   - 가독성을 저해하는 콤보박스 지침부의 리스트 및 볼드 서식(`* **옵션명**`)을 한 줄 평탄화(`* 옵션명: 설명`)로 깔끔하게 정리 완료.
   - `child-doodle.md`와 레지스트리 및 네비게이션 JSON/Python 파일 간의 `description` 표기(옛 AI스러운 문구)를 신규 문구(`사진을 어린아이가 검은 펜과 색연필로 따라 그린 것처럼 바꿔보세요.`)로 완벽히 통일 및 원격 저장소 푸시 완료.
   - `silly-doodle.md` 내 프롬프트 문안에 대해 줄바꿈 간격을 통일하고 콤보박스 리스트 기호를 `-` 로 통합하는 등 AI 모델(Images 2 / Gemini)이 읽기에 정밀한 최적화 레이아웃으로 최종 정돈 및 깃허브 푸시 완료.
   - `child-doodle.md` 내 프롬프트 문안에 대해서도 동일하게 줄바꿈 간격을 일정하게 통일하고, 콤보박스 리스트 기호를 `-` 로 통합하는 등 AI 가독성 최적화 포맷팅 작업 적용 및 깃허브 푸시 완료.
   - 프롬프트 생성/설명문 관리 일관성을 극대화하기 위해 `AGENTS.md` 파일 최하단에 4각 동기화 규칙, AI 해석 최적화 마크다운 포맷팅 규칙, 콤보박스 기본값 설계 규칙을 Learned Rule로 명문화하여 등록 및 깃허브 푸시 완료.
   - **기존 10개 핵심 프롬프트의 description 4각 동기화 및 서식 정돈 완료**: `korean-editor.md`, `universal-handoff.md` 등 10개 핵심 프롬프트에 대해 의미 지시사항은 훼손 없이 서식만 정돈하고, description을 Frontmatter, registry JSON, navigation JSON, Python expected code 간 1:1로 완벽히 일치 및 원격 저장소 푸시 완료.
   - **미교정 12개 프롬프트 설명문 4각 정렬 및 포맷팅 평탄화 완료**: `ai-practice`, `image-ai` 등 7개 불일치 설명문을 md frontmatter를 기준으로 4각 동기화 완료하고, `reduce-hallucination.md` 등 5개 대상의 본문 지침부 중첩 볼드를 제거하고 평탄화하여 기계 가독성 확보 완료 (로컬 git 커밋 완료, push 대기).
   - **silly-doodle 메타데이터 복원 완료**: 이전 정리 도중 덮어써졌던 사용자의 preview(다중 이미지 `/preview.jpg, /preview2.png, /preview3.png`)와 source(`Threads (@ah_g_moo, @_0.beomi_)`) 메타데이터를 확인하고 원래대로 안전하게 복구 및 깃허브 푸시 완료.
   - **사고 보고서 생성**: 본 사고에 대해 원인 규명 및 재발 방지책을 명시한 `2026-08-20-silly-doodle-metadata-overwrite-report.md` 공식 사고 보고서를 작성하여 원격 깃허브 저장소 배포 완료.
   - **장문 프롬프트 3개 파일 과도한 줄바꿈 병합 정돈**: `silly-doodle.md`, `funeral-etiquette.md`, `korean-editor-guide.md` 등 장문 프롬프트 파일에 대해 한 줄 단위로 잘려있던 개행들을 긴밀한 단락(Paragraph) 형태로 묶어 정돈 및 깃허브 푸시 완료.

## 검증 결과
- **빌드 테스트**: `python3 scripts/build.py`
- **결과**: `Build complete. Pages: 57, Assets: 33` (성공, exit code 0)
