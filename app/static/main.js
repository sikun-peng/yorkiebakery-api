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

        // ✅ Close modal and refresh UI/redirect
        modal.style.display = "none";
        if (data.redirect) {
            window.location.href = data.redirect;
        } else {
            location.reload();
        }

    } catch (error) {
        alert("Network error. Please try again.");
    } finally {
        submitBtn.innerText = originalText;
        submitBtn.disabled = false;
    }
});

/* ===========================
   AI Demo Link Environment Switch
   =========================== */
document.addEventListener("DOMContentLoaded", () => {
    const link = document.getElementById("ai-demo-link");
    console.log("AI Demo link element:", link);

    if (!link) return;

    const hostname = window.location.hostname;
    console.log("Hostname detected:", hostname);

    // Local development
    if (hostname === "localhost" || hostname === "127.0.0.1") {
        link.href = "http://localhost:5173/";
        link.target = "_blank";
        console.log("AI Demo link set to localhost:5173");
    }

    else {
        link.href = "/ai-demo/";
        console.log("AI Demo fallback: /ai-demo");
    }
});

/* ===========================
   AI Demo Button (if using <button>)
   =========================== */
document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("ai-demo-btn");
    if (!btn) return;

    const hostname = window.location.hostname;

    btn.addEventListener("click", () => {
        if (hostname === "localhost" || hostname === "127.0.0.1") {
            window.open("http://localhost:5173/", "_blank");
        } else {
            window.location.href = "/ai-demo/";
        }
    });
});

/* ===========================
   CART: AJAX add/remove on menu cards
   =========================== */
document.addEventListener("DOMContentLoaded", () => {
    const badge = document.getElementById("global-cart-count");

    async function updateCart(action, itemId, form) {
        const endpoint = action === "add" ? "/cart/add" : "/cart/remove";
        const payload = { menu_item_id: itemId };
        try {
            const res = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            if (!res.ok) throw new Error("Request failed");
            const data = await res.json();
            if (!data.ok) throw new Error("Bad response");

            // Update badge
            if (badge) {
                const count = data.cart_count || 0;
                badge.textContent = count;
                badge.style.display = count > 0 ? "inline-flex" : "none";
            }

            // Update qty display inside the same card
            const card = form.closest(".menu-card") || form.closest(".item-main");
            const itemCount = data.item_count || 0;

            if (card) {
                const qtyDisplay = card.querySelector(".qty-display");
                const qtyBadge = card.querySelector(".item-qty-badge");
                const addForm = card.querySelector('.cart-form[data-cart-action="add"]');
                const minusForm = card.querySelector('.cart-form[data-cart-action="remove"]');
                const addButton = addForm?.querySelector("button");
                const minusButton = minusForm?.querySelector("button");
                const hadQtyDisplay = Boolean(qtyDisplay);

                // If we were in "Add to Cart" state (no qty display) and we just added, reload to show controls
                if (!hadQtyDisplay && action === "add" && itemCount > 0) {
                    window.location.reload();
                    return;
                }

                if (qtyDisplay) {
                    qtyDisplay.textContent = itemCount;
                }
                if (qtyBadge) {
                    qtyBadge.textContent = itemCount;
                    qtyBadge.style.display = itemCount > 0 ? "inline-flex" : "none";
                }

                // Toggle disabled state when zero
                if (addButton) addButton.disabled = false;
                if (minusButton) minusButton.disabled = itemCount <= 0;

                // If we had controls and count dropped to zero, reload to restore single add button
                if (hadQtyDisplay && itemCount <= 0) {
                    window.location.reload();
                }
            }
        } catch (err) {
            console.error("Cart update failed:", err);
            // Fallback to normal form submit
            form.submit();
        }
    }

    document.body.addEventListener("submit", (e) => {
        const form = e.target;
        if (!form.classList.contains("cart-form")) return;
        e.preventDefault();
        const action = form.dataset.cartAction;
        const itemId = form.dataset.itemId;
        if (!action || !itemId) {
            form.submit();
            return;
        }
        updateCart(action, itemId, form);
    });
});

/* ===========================
   MENU CARD CLICK THRU
   =========================== */
document.addEventListener("DOMContentLoaded", () => {
    const cards = Array.from(document.querySelectorAll(".menu-card[data-item-link]"));
    if (!cards.length) return;

    const isInteractive = (el) => {
        const tag = el.tagName?.toLowerCase();
        if (!tag) return false;
        return ["a", "button", "input", "select", "textarea", "label"].includes(tag) || el.closest("form");
    };

    cards.forEach((card) => {
        const href = card.dataset.itemLink;
        if (!href) return;

        card.addEventListener("click", (e) => {
            if (isInteractive(e.target)) return;
            window.location.href = href;
        });

        card.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !isInteractive(e.target)) {
                e.preventDefault();
                window.location.href = href;
            }
        });

        card.style.cursor = "pointer";
    });
});

/* ===========================
   NAV: MOBILE TOGGLE
   =========================== */
document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("nav-toggle");
    const links = document.getElementById("nav-links");
    if (!toggle || !links) return;

    toggle.addEventListener("click", () => {
        links.classList.toggle("nav-open");
    });

    // Close menu when a link is clicked (mobile)
    links.addEventListener("click", (e) => {
        const target = e.target;
        if (target && target.classList.contains("nav-link")) {
            links.classList.remove("nav-open");
        }
    });
});
