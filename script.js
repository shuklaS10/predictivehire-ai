document.addEventListener("DOMContentLoaded", function () {
    const resumeInput = document.getElementById("resume");
    const fileName = document.getElementById("file-name");
    const form = document.querySelector(".form-card");
    const submitButton = document.querySelector("button[type='submit']");

    if (resumeInput && fileName) {
        resumeInput.addEventListener("change", function () {
            if (resumeInput.files.length > 0) {
                fileName.textContent = resumeInput.files[0].name;
            } else {
                fileName.textContent = "Choose a resume file";
            }
        });
    }

    if (form && submitButton) {
        form.addEventListener("submit", function () {
            submitButton.textContent = "Analyzing Resume...";
            submitButton.disabled = true;
        });
    }
});
