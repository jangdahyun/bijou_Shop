document.addEventListener("DOMContentLoaded", () => {
    const inputs = document.querySelectorAll(".auth-form__field input");

    inputs.forEach((input) => {
        input.addEventListener("focus", () => {
            input.parentElement.classList.add("is-focused");
        });
        input.addEventListener("blur", () => {
            if (!input.value.trim()) {
                input.parentElement.classList.remove("is-focused");
            }
        });
    });
});
