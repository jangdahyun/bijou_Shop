document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("[data-signup-form]");
  if (!form) return;

  const completeButton = form.querySelector("[data-complete-button]");
  if (!completeButton) return;

  const setButtonState = () => {
    const isVerified = form.dataset.verified === "true";
    completeButton.disabled = !isVerified;
    completeButton.hidden = !isVerified;
  };

  setButtonState();

  // 보수적으로 폼 데이터가 변경되면 다시 비활성화
  form.addEventListener("input", (event) => {
    if (event.target.name === "action") return;
    if (form.dataset.verified !== "true") return;
    // 인증 완료 이후에 폼을 수정하면 다시 인증 필요
    form.dataset.verified = "false";
    setButtonState();
  });
});
