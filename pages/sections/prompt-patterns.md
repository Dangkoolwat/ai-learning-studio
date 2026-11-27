---
registry_id: prompt-patterns
title: 프롬프트 패턴 연습
description: 16개 프롬프트 패턴을 전후 비교 실습과 안전 사례로 익혀 보세요.
source: 논문 원전 · Jules White 외 8명, "A Prompt Pattern Catalog to Enhance Prompt Engineering with ChatGPT" (밴더빌트대학교, 2023-02-21 제출, arXiv:2302.11382 v1). 해설과 실습 예시는 AI Learning Studio 작성.
---

# 프롬프트 패턴 연습

같은 요청이라도 어떤 패턴을 한 줄 더하느냐에 따라 AI의 답변 수준이 크게 달라집니다.

이곳에서는 White 외(2023) 논문에 정리된 16가지 프롬프트 패턴 중 15개 패턴은 같은 요청으로 전후를 비교해 보고, '거절된 질문 다시 묻기'는 안전과 정당한 활용 사례로 살펴봅니다.

## 기존 메뉴와 무엇이 다른가요?

- 프롬프트 단계별 체험하기: 한 가지 주제를 여러 기법으로 쌓아 최종 프롬프트를 완성하는 연습
- 프롬프트 패턴 연습: 패턴 하나를 깊게 떼어내 전후 차이를 비교하며 원리를 익히는 연습
- 프롬프트 한 스푼: 원리를 익힌 뒤 실무에서 바로 복사해 쓰는 한 줄 프롬프트 모음

---

## 지금 이런 고민이라면 여기서 시작해 보세요

패턴 이름을 몰라도 괜찮습니다. 지금 가장 자주 겪는 막막함 하나를 골라 바로 비교 실습을 시작해 보세요.

- 무엇부터 말해야 할지 막막할 때: [역질문 유도하기 · Flipped Interaction](/prompt-patterns/flipped-interaction/)
- 답변이 너무 뻔하고 추상적일 때: [역할 부여하기 · Persona](/prompt-patterns/persona/)
- 결과가 매번 제멋대로인 형식으로 나올 때: [출력 틀 지정하기 · Template](/prompt-patterns/template/)
- 수치나 제도 설명이 맞는지 불안할 때: [사실 확인 목록 뽑기 · Fact Check List](/prompt-patterns/fact-check-list/)

---

## 기준 논문 소개

이 섹션은 White 외(2023)의 ChatGPT 연구를 바탕으로 했으며, 실습 예시는 AI Learning Studio가 ChatGPT와 Gemini에서 시도해 볼 수 있도록 작성했습니다.

미국 밴더빌트대학교 연구진(Jules White 외 8명)이 2023년 2월 21일 공개한 논문 "A Prompt Pattern Catalog to Enhance Prompt Engineering with ChatGPT" (arXiv:2302.11382 v1)은 소프트웨어 공학의 '디자인 패턴(Design Patterns)' 개념을 생성형 AI 프롬프트에 적용해 16가지 프롬프트 패턴을 하나의 카탈로그로 처음 체계화했습니다.

논문 분류표는 16개 패턴을 아래 6가지 영역으로 나눕니다.

- Input Semantics (입력 의미 정의): AI가 내 입력을 해석하는 규칙이나 나만의 단축어를 정하는 패턴
- Output Customization (출력 맞춤화): AI의 역할, 형식, 단계, 자동화 방식 등 결과물 형태를 제어하는 패턴
- Error Identification (오류 식별): AI가 스스로 답변을 점검하거나 확인해야 할 사실 목록을 뽑게 하는 패턴
- Prompt Improvement (프롬프트 개선): 질문을 더 구체적으로 다듬거나 대안을 비교해 더 나은 요청을 만드는 패턴
- Interaction (상호작용): AI가 먼저 질문하게 하거나 게임·반복 생성처럼 대화 흐름을 설계하는 패턴
- Context Control (맥락 제어): 긴 대화에서 계속 유지할 기준과 제외할 맥락을 지정하는 패턴

참고 안내:

- 기준 버전: 2023-02-21 공개본(arXiv:2302.11382 v1) 기준이며 원문은 ChatGPT를 중심으로 패턴을 설명합니다.
- 분류 개수 주석: 논문 본문에는 "five categories"라고 적혀 있으나 논문 분류표에는 위 6개 분류가 수록되어 있습니다. 이 섹션은 논문 분류표의 6개 분류를 따릅니다.

---

## 패턴 페이지 구성 안내

16개 패턴 중 15개는 체험을 먼저 하고 설명을 나중에 읽는 6단계 비교 실습으로 구성되며, 안전상 우회 체험을 제외한 1개 패턴([거절된 질문 다시 묻기 · Refusal Breaker](/prompt-patterns/refusal-breaker/))은 개념과 주의점을 다루는 읽기 자료로 제공합니다.

1. 패턴 없이 먼저 해보기: 짧은 요청으로 일반적인 답을 겪어 봅니다.
2. 패턴을 넣어 다시 해보기: 같은 요청에 패턴 문장만 더해 차이를 확인합니다.
3. 차이 비교 질문: 두 답변에서 무엇이 달라졌는지 직접 관찰하고 정리합니다.
4. 패턴 해설: 한 줄 정의, 언제 쓰는지, 핵심 문장 구조를 정리합니다.
5. 내 주제로 바꾸기: 스마트 콤보박스로 내 상황에 맞춰 조합하고 복사합니다.
6. 주의점과 조합: 한계와 함께 쓰면 좋은 패턴, 바로 쓰는 한 스푼 링크를 확인합니다.

---

## 16가지 프롬프트 패턴 지도

입문 7개, 활용 5개, 심화 4개로 총 16개 패턴을 정리했습니다.

### 🌱 입문 (7개) · 바로 써먹기 좋은 기본 패턴

- [역질문 유도하기 · Flipped Interaction](/prompt-patterns/flipped-interaction/) (Interaction): AI가 먼저 질문하게 하기
- [역할 부여하기 · Persona](/prompt-patterns/persona/) (Output Customization): AI에게 역할 부여하기
- [출력 틀 지정하기 · Template](/prompt-patterns/template/) (Output Customization): 출력 틀을 지정하기
- [질문 다듬기 · Question Refinement](/prompt-patterns/question-refinement/) (Prompt Improvement): 내 질문을 더 좋은 질문으로 고치게 하기
- [사실 확인 목록 뽑기 · Fact Check List](/prompt-patterns/fact-check-list/) (Error Identification): 확인해야 할 사실 목록 뽑게 하기
- [스스로 점검하게 하기 · Reflection](/prompt-patterns/reflection/) (Error Identification): 자기 답변을 스스로 점검하게 하기
- [다른 방법 비교하기 · Alternative Approaches](/prompt-patterns/alternative-approaches/) (Prompt Improvement): 같은 목표의 다른 방법을 비교하게 하기

### 🧭 활용 (5개) · 복잡한 목표와 긴 대화를 다루는 패턴

- [하위 질문으로 쪼개기 · Cognitive Verifier](/prompt-patterns/cognitive-verifier/) (Prompt Improvement): 큰 질문을 하위 질문으로 쪼개 답하게 하기
- [중간 단계 채우기 · Recipe](/prompt-patterns/recipe/) (Output Customization): 아는 시작과 끝 사이의 중간 단계 채우기
- [대화 맥락 지정하기 · Context Manager](/prompt-patterns/context-manager/) (Context Control): 대화에서 고려할 맥락과 뺄 맥락 지정하기
- [게임처럼 연습하기 · Game Play](/prompt-patterns/game-play/) (Interaction): 상황을 게임처럼 진행하며 연습하기
- [나만의 단축어 만들기 · Meta Language Creation](/prompt-patterns/meta-language-creation/) (Input Semantics): 나만의 단축어를 정의해 쓰기

### 🚀 심화 (4개) · 확장·자동화·안전 개념 패턴

- [실행 자동화 만들기 · Output Automater](/prompt-patterns/output-automater/) (Output Customization): 결과를 실행 가능한 자동화로 만들게 하기
- [도표·그림 입력 생성하기 · Visualization Generator](/prompt-patterns/visualization-generator/) (Output Customization): 그림·도표를 만들 입력을 생성하게 하기
- [같은 형식 계속 생성하기 · Infinite Generation](/prompt-patterns/infinite-generation/) (Interaction): 같은 형식의 결과를 계속 생성하게 하기
- [거절된 질문 다시 묻기 · Refusal Breaker](/prompt-patterns/refusal-breaker/) (Prompt Improvement · 읽기 자료): 거절된 질문을 다른 표현으로 다시 묻게 하기

---

## 이용 전 꼭 확인할 점

- AI가 만든 결과는 그대로 믿지 말고 반드시 직접 확인하세요.
- 예제에 실명, 연락처, 회사명 같은 개인정보나 민감한 정보를 넣지 마세요.
- 연봉, 정책, 법률, 채용 기준 같은 수치는 반드시 공식 사이트에서 다시 확인하세요.
