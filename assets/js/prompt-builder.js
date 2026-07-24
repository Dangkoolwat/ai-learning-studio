/**
 * Interactive prompt-builder handler for AI Learning Studio.
 * Supports Help Modal Popups (?) and Live Prompt Assembly.
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
        const input = field.querySelector("input");

        let val = "";
        const checkboxes = field.querySelectorAll("input[type='checkbox']");
        if (checkboxes.length > 0) {
          const checked = Array.from(checkboxes).filter((cb) => cb.checked).map((cb) => cb.value.trim());
          val = checked.length > 0 ? checked.join(", ") : "";
        } else if (select) {
          val = select.value ? select.value.trim() : "";
        } else if (input) {
          val = input.value ? input.value.trim() : "";
        }

        if (val === "(선택 없음)") val = "";

        if (fieldId) {
          values[fieldId] = val;
        }
      });

      // Check if this is an image AI prompt builder page
      const isImageBuilder = values["ai_target"] || values["subject"] || values["background"] || values["style"];

      let generatedPrompt = "";

      if (isImageBuilder) {
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

        try {
          let copied = false;
          if (navigator.clipboard?.writeText) {
            try {
              await navigator.clipboard.writeText(text);
              copied = true;
            } catch (err) {
              console.warn("navigator.clipboard.writeText failed in builder, falling back to execCommand:", err);
            }
          }

          if (!copied) {
            const ta = document.createElement("textarea");
            ta.value = text;
            ta.style.cssText = "position:fixed;top:-9999px;left:-9999px;opacity:0";
            document.body.append(ta);
            ta.focus();
            ta.select();
            const ok = document.execCommand("copy");
            ta.remove();
            if (!ok) throw new Error("copy failed");
          }

          copyBtn.textContent = "복사되었습니다!";
          setTimeout(() => {
            copyBtn.textContent = "프롬프트 복사";
          }, 1800);
        } catch {
          alert("복사에 실패했습니다.");
        }
      };
    }
  });
}
