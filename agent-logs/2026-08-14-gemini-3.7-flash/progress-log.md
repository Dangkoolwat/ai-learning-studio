# 작업 진행 로그 (2026-08-14)

## 1. 작업 개요
- **목적**: `나만의 AI 만들기` (`ai-assistant`) 섹션에 100% 독자 제작된 "Active Recall 메타인지 AI 튜터/시험관" 시스템 지침서 추가
- **저작권 지침**: 블로그(CC BY-NC-ND 4.0)의 텍스트 및 프롬프트 문구를 일절 사용하지 않고, 공인된 교육학 원리(Active Recall, Formative Assessment) 및 AI Learning Studio 표준 템플릿에 따라 독자 작성 (Clean-room Authoring)
- **주요 구성**: 
  - 학습과학 이론 및 서비스별(NotebookLM, Gemini GEMs, ChatGPT/Claude Projects) 설정 가이드
  - 7가지 맞춤형 조건 선택을 통한 동적 프롬프트 조립 (prompt-builder 방식)

## 2. 작업 계획
1. `data/page-registry.json` 및 `data/navigation.json`에 신규 페이지 `ai-assistant-active-recall-tutor` 등록
2. `pages/sections/ai-assistant/active-recall-tutor.md` 파일 독자 작성
## 3. 작업 결과 및 검증
- **생성된 페이지**: `/ai-assistant/active-recall-tutor/` (1:1 Active Recall 메타인지 학습 코치)
- **등록된 계약 파일**:
  - `data/page-registry.json`
  - `data/navigation.json`
  - `core/page_registry.py`
  - `core/navigation.py`
  - `pages/sections/ai-assistant/active-recall-tutor.md`
- **메뉴명 및 설명 업데이트**: 
  - 메뉴명: `1:1 Active Recall 학습 코치`
  - 설명: `질문과 피드백으로 내가 아는 것과 모르는 것을 직접 확인하는 맞춤형 학습 코치`
- **소개 및 핵심 원리 문구 다듬기**: 딱딱한 전문 심리학 용어를 지양하고 친절하고 가독성 높은 문구(`💡 왜 Active Recall 방식으로 공부할까요?`)로 본문 전면 개선 반영.
- **필드 설명 어휘 순화**: `진행 및 피드백 방식` 필드의 어렵고 다소 조잡했던 한자어 설명(`인출 몰입도와 오답 처리 방식`)을 쉬운 우리말(`질문을 한 문제씩 주고받는 대화 방식과 틀렸을 때 힌트를 줄지 정합니다.`)로 친절하게 개선.
- **학습 주제 범주 다변화 반영**: `학습 주제` 필드의 예시 및 설명을 초·중·고 교과목부터 대학·직장인 업무/전공, 성인·어르신의 인문 교양(`논어`, `사자성어`, `건강 상식` 등)까지 전 연령대를 포괄하도록 확장 업데이트.
- **정적 빌드 검증**: `python3 scripts/build.py` 실행 완료 (Exit Code: 0, 총 51개 페이지 빌드 완료)





- **HTML 렌더링 수정**: 마크다운 파서에서 LaTeX 문법으로 오인되어 `$ ightarrow >`로 깨져 출력되던 `$\rightarrow$` 문구를 표준 유니코드 화살표 `→`로 일괄 교정 및 검증 완료.
- **사용자 검수 4대 개선사항 반영 완료**:
  1. `메타인지를 극대화` → `메타인지를 돕는` 문구 다듬기
  2. `지식의 Edge 탐색` → `사용자가 정확히 이해하지 못한 경계 지점을 찾아 질문`으로 풀어 쓰기
  3. `10점 평가 기준 및 근거`: 정확성, 핵심 개념 이해, 명확성 기준 명시 및 이유 한 문장 설명 지침 추가
  4. `출처 구분 안전장치`: 업로드한 학습 자료와 외부 일반 지식 보완 내용의 출처 구분 및 차이점 명시 지침 수록
- **저작권 검증**: 타 블로그(CC BY-NC-ND 4.0)의 표상 및 구절 일절 사용 없음. 인출 연습(Active Recall), 바람직한 어려움(Desirable Difficulty), 핀포인트 형성평가 등 공인 교육학 원리를 기반으로 100% 독자적 재작성 완료 (Clean-room Authoring).



