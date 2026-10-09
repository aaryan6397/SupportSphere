document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-password-toggle]").forEach((button) => {
        button.addEventListener("click", () => {
            const input = document.getElementById(button.dataset.passwordToggle);
            if (!input) return;
            const showingPassword = input.type === "text";
            input.type = showingPassword ? "password" : "text";
            button.setAttribute("aria-pressed", String(!showingPassword));
            button.setAttribute("aria-label", showingPassword ? "Show password" : "Hide password");
            button.textContent = showingPassword ? "Show" : "Hide";
        });
    });
});
