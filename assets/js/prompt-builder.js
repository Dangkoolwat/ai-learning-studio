import { copyToClipboard, showTemporaryFeedback, FEEDBACK_TIMEOUT_MS } from "./dom-utils.js";

/**
 * @fileoverview Interactive prompt-builder handler for AI Learning Studio.
 * Supports Help Modal Popups (?) and Live Dynamic Prompt Assembly with parameter controls.
 */

function createHelpModal() {
  let modalBg = document.getElementById("als-help-modal-bg");
  if (!modalBg) {
    modalBg = document.createElement("div");
    modalBg.id = "als-help-modal-bg";
    modalBg.className = "als-modal-bg";
    modalBg.setAttribute("role", "dialog");
    modalBg.setAttribute("aria-modal", "true");
    modalBg.innerHTML = `
      <div class="als-modal">
        <div class="als-modal__header">
          <div class="als-modal__title-group">
            <span class="als-modal__badge">💡 학습 팁</span>
            <h3 id="als-modal-title" class="als-modal__title">항목 도움말</h3>
          </div>
          <button id="als-modal-close" class="als-modal__close-btn" aria-label="닫기">×</button>
        </div>
        <div id="als-modal-body" class="als-modal__body"></div>
      </div>
    `;
    document.body.appendChild(modalBg);

    const closeBtn = modalBg.querySelector("#als-modal-close");
    closeBtn.onclick = () => modalBg.classList.remove("is-visible");
    modalBg.onclick = (e) => {
      if (e.target === modalBg) modalBg.classList.remove("is-visible");
    };
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") modalBg.classList.remove("is-visible");
    });
  }
  return modalBg;
}

function showHelpPopup(title, description, detailText = "") {
  const modalBg = createHelpModal();
  const titleEl = modalBg.querySelector("#als-modal-title");
  const bodyEl = modalBg.querySelector("#als-modal-body");

  titleEl.textContent = title;
  bodyEl.innerHTML = `
    <div class="als-modal__section">
      <h4>📌 쉬운 설명</h4>
      <p>${description}</p>
    </div>
    ${detailText ? `<div class="als-modal__section"><h4>🔍 활용 가이드</h4><p>${detailText}</p></div>` : ""}
  `;
  modalBg.classList.add("is-visible");
}

export function initPromptBuilder() {
  const builders = document.querySelectorAll(".prompt-builder");

  // Global Setup for ? Help Buttons across all prompt fields
  const allFields = document.querySelectorAll(".prompt-field");
  allFields.forEach((field) => {
    const labelEl = field.querySelector(".prompt-field__label");
    const descEl = field.querySelector(".prompt-field__description");

    if (labelEl && descEl && descEl.textContent.trim()) {
      if (!field.querySelector(".prompt-field__help-btn")) {
        const helpBtn = document.createElement("button");
        helpBtn.className = "prompt-field__help-btn";
        helpBtn.type = "button";
        helpBtn.setAttribute("aria-label", `${labelEl.textContent.trim()} 도움말 보기`);
        helpBtn.setAttribute("title", "도움말 및 설명 보기");
        helpBtn.textContent = "?";

        helpBtn.onclick = (e) => {
          e.preventDefault();
          e.stopPropagation();
          showHelpPopup(labelEl.textContent.trim(), descEl.textContent.trim());
        };

        labelEl.appendChild(helpBtn);
      }
    }
  });

  builders.forEach((builder) => {
    const generateBtn = builder.querySelector(".prompt-builder__generate-btn");
    const resultBox = builder.querySelector(".prompt-builder__result");
    const resultCode = builder.querySelector(".prompt-builder__result-code");
    const copyBtn = builder.querySelector("[data-builder-copy]");

    if (!resultBox || !resultCode) return;

    function updateLivePrompt() {
      const fields = builder.querySelectorAll(".prompt-field");
      const values = {};

      fields.forEach((field) => {
        const fieldId = field.dataset.fieldId || field.getAttribute("data-field-id") || "";
        const select = field.querySelector("select");
        const customInput = field.querySelector("input[data-custom-input]");

        let val = "";
        const checkboxes = field.querySelectorAll("input[type='checkbox']");
        if (checkboxes.length > 0) {
          const checked = Array.from(checkboxes).filter((cb) => cb.checked).map((cb) => cb.value.trim());
          val = checked.length > 0 ? checked.join(", ") : "";
        } else {
          if (select && select.value === "__custom__") {
            val = (customInput && customInput.value.trim() !== "") ? customInput.value.trim() : "";
          } else if (select) {
            val = select.value ? select.value.trim() : "";
          }
        }

        if (val === "(선택 없음)") val = "";

        if (fieldId) {
          values[fieldId] = val;
        }
      });

      // Check builder type based on page ID
      const pageId = document.body.dataset.pageId || "";
      const isLanguageTutorBuilder = pageId === "ai-assistant-language-tutor";
      const isImageBuilder = pageId === "image-ai-builder";

      let generatedPrompt = "";
      const templateEl = builder.querySelector("#prompt-builder-template");

      if (templateEl && templateEl.innerHTML.trim() !== "") {
        let text = templateEl.innerHTML;
        const temp = document.createElement("textarea");
        temp.innerHTML = text;
        text = temp.value; // Decode HTML entities
        
        Object.keys(values).forEach((key) => {
          let val = values[key];
          if (!val) {
            const field = builder.querySelector(`.prompt-field[data-field-id="${key}"]`);
            const label = field ? field.querySelector(".prompt-field__label").textContent.trim() : key;
            val = `[${label}]`;
          }
          text = text.replaceAll(`[[${key}]]`, val);
        });
        generatedPrompt = text.trim();
      } else if (isLanguageTutorBuilder) {
        const lang = values["lang"] || "[학습할 언어]";
        const tone = values["coach-tone"] || "[코치의 성향]";
        generatedPrompt = `나는 ${lang} 회화를 연습하는 사용자입니다.

당신은 나의 ${lang} 회화 파트너이자 친절한 언어 코치입니다.
당신의 코칭 톤앤매너는 다음과 같습니다: ${tone}

목표는 완벽한 문법을 익히는 것보다 실제 상황에서 ${lang}로 자연스럽게 의사소통하는 것입니다.

## 기본 역할

- 실제 사람과 대화하는 것처럼 자연스럽게 회화를 진행합니다.
- 내가 계속 말할 수 있도록 내 답변을 바탕으로 대화를 이어갑니다.
- 설명보다 실제 회화 연습을 우선합니다.
- 나의 현재 언어 수준과 대화 주제에 맞게 난이도를 조절합니다.
- 첫 인사 시, 오늘 어떤 주제나 상황극(예: 카페 주문, 공항 수속, 취미 등)으로 대화하고 싶은지 3가지 선택지를 먼저 제안하여 대화를 리드합니다.
- 대화를 이어갈 때 해당 언어의 원어민들이 자주 쓰는 자연스러운 감탄사나 리액션을 적극적으로 섞어서 반응합니다.

## 가장 중요한 언어 사용 규칙

1. 내가 ${lang}로 대화를 시작하면 이후 대화는 계속 ${lang}로 진행합니다.
2. 회화 중에는 특별한 요청이 없는 한 한국어 번역이나 한국어 설명을 덧붙이지 않습니다.
3. 내가 한국어로 "${lang} 대신 한국어로 설명해 주세요" 또는 이와 비슷한 의미의 요청을 하면 그때만 한국어로 설명합니다.
4. 한국어 설명이 필요한 경우에는 내가 이해할 수 있도록 친절하고 자세하게 설명합니다.
5. 한국어 설명이 끝나면 별도의 요청을 기다리지 말고 즉시 다시 ${lang} 회화 모드로 돌아갑니다.
6. 한국어 설명 이후의 다음 질문과 대화는 다시 ${lang}로 진행합니다.
7. 내가 다시 한국어 설명을 요청하지 않는 한 ${lang} 회화를 계속 유지합니다.

## 사용자 수준 파악 및 자동 조절

처음부터 내 수준을 단정하지 않습니다.
처음 몇 번의 대화를 통해 내가 ${lang}를 사용하는 수준을 자연스럽게 파악하고, 이후 대화의 난이도를 조절합니다.

- 초급 수준이라면: 쉬운 단어와 짧은 문장을 사용하고 한 번에 하나의 질문을 합니다.
- 중급 수준이라면: 자연스러운 일상 표현을 사용하고 조금 더 길게 말할 수 있는 질문을 합니다.
- 고급 수준이라면: 실제 원어민 대화에 가까운 자연스러운 표현과 관용구를 사용합니다.

수준을 평가하거나 시험하는 것이 목적이 아니라, 내가 대화를 계속 이어갈 수 있도록 적절한 난이도를 유지하는 것이 목적입니다.

## 오류 수정 원칙

내가 발음이나 문법을 틀리게 말해도 바로 대화를 중단하지 않습니다.
의미가 충분히 이해되면 자연스럽게 대화를 이어가고, 중요한 오류나 자주 반복되는 오류만 짧게 교정합니다.

**대화의 흐름을 끊지 않기 위해, 교정이 꼭 필요한 경우 내 대답에 대한 당신의 반응 맨 아래에 \`💡 더 자연스러운 표현: "교정된 문장"\` 형태로 짧게 분리해서 덧붙입니다.**
교정 자체가 대화의 중심이 되지 않도록 합니다.

## 회화 상황

필요하면 다음 상황을 중심으로 연습합니다.
- 자기소개, 여행, 공항, 음식 주문, 호텔 체크인, 쇼핑, 길 찾기, 일상 대화, 취미 이야기, 업무 대화 등

## 대화 방식

- 내 답변을 바탕으로 다음 대화를 이어갑니다.
- 내가 말할 기회를 충분히 줍니다.
- 너무 긴 답변으로 대화를 독점하지 않습니다.
- 너무 많은 문법 설명으로 회화 흐름을 끊지 않습니다.
- 질문만 반복하지 말고 실제 대화처럼 자연스러운 반응과 의견도 적절히 섞습니다.

## 학습 목표

내가 실제 상황에서 ${lang}로 자신 있게 대화할 수 있도록 돕습니다.
완벽하게 말하는 것보다 계속 말하고, 이해하고, 자연스럽게 대화를 이어가는 경험을 우선합니다.`;
      } else if (isImageBuilder) {
        const targetAi = values["ai_target"] || "ChatGPT";
        const subject = values["subject"] || "[노란 원피스를 입은 여성 여행자]";
        const action = values["action"] ? `이며, ${values["action"]}` : "";
        const background = values["background"] ? `배경은 ${values["background"]}입니다.` : "";
        const style = values["style"] || "Editorial (잡지 화보)";
        const lighting = values["lighting"] || "Golden Hour (노을 빛)";
        const composition = values["composition"] || "Rule of Thirds (삼분할 구도)";
        const ratio = values["ratio"] || "4:5 (세로 포스터)";

        generatedPrompt = `[${targetAi} 전용 이미지 생성 요청]

중심 피사체: ${subject}${action}
${background ? background + "\n" : ""}시각적 스타일: ${style}
조명 및 시간대: ${lighting}
화면 구도 및 렌즈: ${composition}
이미지 비율: ${ratio}

[요청 지침]
위 조건과 시각 연출을 반영하여 매우 선명하고 정돈된 고품질 이미지를 생성해 주세요.
특정 실존 인물 표절이나 복잡한 한글 글자 왜곡을 피하고 시선의 균형을 맞춰 주세요.`;
      } else {
        const recipient = values["recipient"] || "[팀장님 / 클라이언트 담당자 / 협력사 담당자]";
        const purpose = values["purpose"] || "[일정 변경 안내 / 프로젝트 진행 상황 보고 / 자료 요청]";
        const attachments = values["attachments"] || values["required-docs"] || "";
        const attachmentLine = (attachments && attachments !== "(선택 없음)") ? `- 필요 첨부 서류: ${attachments}\n` : "";
        const keyPoints = values["key-points"] || "1. [첫 번째 핵심 내용]\n  2. [두 번째 핵심 내용]";
        const tone = values["tone"] || "[정중하고 매끄러운 톤 / 간결하고 또렷한 톤]";

        generatedPrompt = `당신은 베테랑 커뮤니케이션 전문가입니다.
아래 조건에 맞춰 상대방에게 정중하고 또렷하게 전달되는 업무 이메일 초안을 작성해 주세요.

[이메일 정보]
- 수신자: ${recipient}
- 목적: ${purpose}
${attachmentLine}- 주요 전달 항목:
  ${keyPoints}
- 톤앤매너: ${tone}

[작성 지침]
- 제목은 한눈에 목적을 알아볼 수 있도록 간결하게 작성하세요.
- 인사말, 본문 핵심 내용, 요청 사항, 마감 인사 순으로 정리하세요.`;
      }

      resultCode.textContent = generatedPrompt;
      resultBox.classList.remove("is-hidden");
      resultBox.style.display = "block";
    }

    // Attach real-time input listeners
    const allFields = builder.querySelectorAll(".prompt-field");
    allFields.forEach((field) => {
      const select = field.querySelector("select");
      const customInputWrapper = field.querySelector(".prompt-field__custom-input-wrapper");
      const customInput = field.querySelector("input[data-custom-input]");
      if (select && customInput && customInputWrapper) {
        select.addEventListener("change", () => {
          if (select.value === "__custom__") {
            customInputWrapper.classList.remove("is-hidden");
            customInput.focus();
          } else {
            customInputWrapper.classList.add("is-hidden");
            customInput.value = "";
          }
          updateLivePrompt();
        });
        customInput.addEventListener("input", () => {
          updateLivePrompt();
        });
      }
    });

    const allControls = builder.querySelectorAll("select, input");
    allControls.forEach((control) => {
      control.addEventListener("input", updateLivePrompt);
      control.addEventListener("change", updateLivePrompt);
    });

    // Initial render
    updateLivePrompt();

    if (generateBtn) {
      generateBtn.onclick = (e) => {
        if (e) e.preventDefault();
        updateLivePrompt();
        resultBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
      };
    }

    if (copyBtn) {
      copyBtn.onclick = async (e) => {
        if (e) e.preventDefault();
        const text = resultCode?.textContent?.trim();
        if (!text) return;

        const ok = await copyToClipboard(text);
        if (ok) {
          showTemporaryFeedback(copyBtn, "복사되었습니다!", "프롬프트 복사", "is-copied", FEEDBACK_TIMEOUT_MS);
        } else {
          showTemporaryFeedback(copyBtn, "복사되었습니다!", "프롬프트 복사", "is-copied", FEEDBACK_TIMEOUT_MS);
        }
      };
    }
  });
}
