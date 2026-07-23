/**
 * Interactive prompt-builder handler for AI Learning Studio (Option B: Live Auto-Assemble Builder).
 */

export function initPromptBuilder() {
  const builders = document.querySelectorAll(".prompt-builder");

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

      const recipient = values["recipient"] || "[팀장님 / 클라이언트 담당자 / 협력사 담당자]";
      const purpose = values["purpose"] || "[일정 변경 안내 / 프로젝트 진행 상황 보고 / 자료 요청]";
      const attachments = values["attachments"] || values["required-docs"] || "";
      const attachmentLine = (attachments && attachments !== "(선택 없음)") ? `- 필요 첨부 서류: ${attachments}\n` : "";
      const keyPoints = values["key-points"] || "1. [첫 번째 핵심 내용]\n  2. [두 번째 핵심 내용]";
      const tone = values["tone"] || "[정중하고 매끄러운 톤 / 간결하고 또렷한 톤]";

      const generatedPrompt = `당신은 베테랑 커뮤니케이션 전문가입니다.
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

      resultCode.textContent = generatedPrompt;
      resultBox.classList.remove("is-hidden");
      resultBox.style.display = "block";
    }

    // Attach real-time input listeners so B-option updates instantly on change
    const allControls = builder.querySelectorAll("select, input");
    allControls.forEach((control) => {
      control.addEventListener("input", updateLivePrompt);
      control.addEventListener("change", updateLivePrompt);
    });

    // Initial render for B-option
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
          await navigator.clipboard.writeText(text);
          copyBtn.textContent = "복사됨!";
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
