/* ===========================
   LOGIN / REGISTER MODAL
   =========================== */
const modal = document.getElementById("auth-modal");
const form = document.getElementById("auth-form");
const modalTitle = document.getElementById("modal-title");
const submitBtn = document.getElementById("auth-submit-btn");
const firstNameField = document.getElementById("first-name-field");
const lastNameField = document.getElementById("last-name-field");
const toggleAuthMode = document.getElementById("toggle-auth-mode");
const toggleText = document.getElementById("toggle-text");

// New authentication elements
const resendVerificationDiv = document.getElementById("resend-verification");
const resendVerificationBtn = document.getElementById("resend-verification-btn");
const resendStatus = document.getElementById("resend-status");
const forgotPasswordLink = document.getElementById("forgot-password-link");
const resetPasswordDiv = document.getElementById("reset-password");
const resetEmail = document.getElementById("reset-email");
const sendResetBtn = document.getElementById("send-reset-btn");
const cancelResetBtn = document.getElementById("cancel-reset-btn");
const resetStatus = document.getElementById("reset-status");

// Track current email for resend verification
let currentEmail = '';

// Open Login
document.getElementById("open-login")?.addEventListener("click", () => {
    modal.style.display = "flex";
    setLoginMode();
});

// Open Register
document.getElementById("open-register")?.addEventListener("click", () => {
    modal.style.display = "flex";
    setRegisterMode();
});

// Close modal
document.getElementById("close-auth")?.addEventListener("click", () => {
    modal.style.display = "none";
    resetModalState();
});

// Close modal when clicking outside
modal?.addEventListener("click", (e) => {
    if (e.target === modal) {
        modal.style.display = "none";
        resetModalState();
    }
});

// Toggle Login <-> Register inside modal
toggleAuthMode?.addEventListener("click", () => {
    if (submitBtn.innerText === "Login") setRegisterMode();
    else setLoginMode();
});

// Resend verification email
resendVerificationBtn?.addEventListener("click", async () => {
    if (!currentEmail) return;

    resendStatus.textContent = "Sending...";
    resendStatus.style.color = "#666";
    resendVerificationBtn.disabled = true;

    try {
        const formData = new FormData();
        formData.append('email', currentEmail);

        const res = await fetch("/auth/resend_verification", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (data.success) {
            resendStatus.textContent = "✅ Verification email sent!";
            resendStatus.style.color = "green";
        } else {
            resendStatus.textContent = "❌ Failed to send email";
            resendStatus.style.color = "red";
        }
    } catch (error) {
        resendStatus.textContent = "❌ Error sending email";
        resendStatus.style.color = "red";
    }

    setTimeout(() => {
        resendStatus.textContent = "";
        resendVerificationBtn.disabled = false;
    }, 5000);
});

// Forgot password link
forgotPasswordLink?.addEventListener("click", (e) => {
    e.preventDefault();
    resetPasswordDiv.style.display = "block";
    forgotPasswordLink.style.display = "none";
});

// Send reset password email
sendResetBtn?.addEventListener("click", async () => {
    const email = resetEmail.value.trim();

    if (!email) {
        resetStatus.textContent = "Please enter your email";
        resetStatus.style.color = "red";
        return;
    }

    if (!email.includes('@')) {
        resetStatus.textContent = "Please enter a valid email";
        resetStatus.style.color = "red";
        return;
    }

    resetStatus.textContent = "Sending reset link...";
    resetStatus.style.color = "#666";
    sendResetBtn.disabled = true;

    try {
        const res = await fetch("/auth/forgot_password", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email })
        });

        const data = await res.json();

        if (data.success) {
            resetStatus.textContent = "✅ Password reset link sent to your email!";
            resetStatus.style.color = "green";
            resetEmail.value = "";

            // Hide reset form after success
            setTimeout(() => {
                resetPasswordDiv.style.display = "none";
                forgotPasswordLink.style.display = "block";
                resetStatus.textContent = "";
            }, 3000);
        } else {
            resetStatus.textContent = data.error || "❌ Failed to send reset link";
            resetStatus.style.color = "red";
        }
    } catch (error) {
        resetStatus.textContent = "❌ Error sending reset link";
        resetStatus.style.color = "red";
    }

    sendResetBtn.disabled = false;
});

// Cancel reset password
cancelResetBtn?.addEventListener("click", () => {
    resetPasswordDiv.style.display = "none";
    forgotPasswordLink.style.display = "block";
    resetStatus.textContent = "";
    resetEmail.value = "";
});

function setLoginMode() {
    modalTitle.innerText = "Login";
    submitBtn.innerText = "Login";
    form.dataset.mode = "login";
    form.action = "/auth/login_form";
    firstNameField.style.display = "none";
    lastNameField.style.display = "none";
    toggleText.innerText = "Don't have an account?";
    toggleAuthMode.innerText = "Register";
    forgotPasswordLink.style.display = "block";
    resetPasswordDiv.style.display = "none";
    resendVerificationDiv.style.display = "none";
}

function setRegisterMode() {
    modalTitle.innerText = "Register";
    submitBtn.innerText = "Register";
    form.dataset.mode = "register";
    form.action = "/auth/register_form";
    firstNameField.style.display = "block";
    lastNameField.style.display = "block";
    toggleText.innerText = "Already have an account?";
    toggleAuthMode.innerText = "Login";
    forgotPasswordLink.style.display = "none";
    resetPasswordDiv.style.display = "none";
    resendVerificationDiv.style.display = "none";
}

function resetModalState() {
    currentEmail = '';
    resendVerificationDiv.style.display = "none";
    resetPasswordDiv.style.display = "none";
    if (forgotPasswordLink) {
        forgotPasswordLink.style.display = "block";
    }
    resetStatus.textContent = "";
    resendStatus.textContent = "";
    if (resetEmail) {
        resetEmail.value = "";
    }
}

/* ===========================
   AJAX FORM SUBMIT (Login / Register)
   =========================== */
form?.addEventListener("submit", async (e) => {
    e.preventDefault(); // prevent full page POST refresh

    const formData = new FormData(form);
    const mode = form.dataset.mode; // "login" or "register"
    const url = mode === "login" ? "/auth/login_form" : "/auth/register_form";

    // Store email for potential resend verification
    currentEmail = formData.get('email');

    // Show loading state
    const originalText = submitBtn.innerText;
    submitBtn.innerText = "Loading...";
    submitBtn.disabled = true;

    try {
        const res = await fetch(url, {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (!data.success) {
            // Show resend verification option if email not verified
            if (data.error && data.error.includes('verify your email')) {
                resendVerificationDiv.style.display = "block";
            }
            alert(data.error || "Something went wrong");
            return;
        }

        // ✅ Close modal and refresh UI
        modal.style.display = "none";
        location.reload();

    } catch (error) {
        alert("Network error. Please try again.");
    } finally {
        submitBtn.innerText = originalText;
        submitBtn.disabled = false;
    }
});