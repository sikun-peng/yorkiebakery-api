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
const authError = document.getElementById("auth-error");
const passwordInput = form?.querySelector('input[name="password"]');
const emailInput = form?.querySelector('input[name="email"]');
const registerStartedAt = document.getElementById("auth-register-started-at");

const showAuthMessage = (msg, isError = true) => {
    if (!authError) {
        alert(msg);
        return;
    }
    authError.textContent = msg || "";
    authError.style.display = msg ? "block" : "none";
    authError.style.color = isError ? "red" : "#1b5e20";
    authError.style.fontWeight = isError ? "normal" : "600";
};

// Backward compatibility for existing calls
const showAuthError = (msg) => {
    showAuthMessage(msg, true);
};

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
    if (registerStartedAt) {
        registerStartedAt.value = Date.now() / 1000;
    }
});

// Open Register
document.getElementById("open-register")?.addEventListener("click", () => {
    modal.style.display = "flex";
    setRegisterMode();
    if (registerStartedAt) {
        registerStartedAt.value = Date.now() / 1000;
    }
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
    showAuthMessage("");
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
    showAuthMessage("");
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
    showAuthMessage("");
    if (registerStartedAt) {
        registerStartedAt.value = Date.now() / 1000;
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

    // Client-side validation for password length in register mode
    if (mode === "register") {
        const pwd = (passwordInput?.value || "").trim();
        if (pwd.length < 6 || pwd.length > 32) {
            showAuthMessage("Password must be 6-32 characters.", true);
            return;
        }
    }

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
            showAuthMessage(data.error || "Something went wrong", true);
            return;
        }

        // ✅ Success handling
        if (mode === "register") {
            const successMsg = data.message || "Success! Check your email to verify your account.";
            showAuthMessage(successMsg, false);
            submitBtn.innerText = originalText;
            submitBtn.disabled = false;
            // Keep modal open so user sees the message
            return;
        } else {
            modal.style.display = "none";
            if (data.redirect) {
                window.location.href = data.redirect;
            } else {
                location.reload();
            }
        }

    } catch (error) {
        showAuthMessage("Network error. Please try again.", true);
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

/* ===========================
   FLOATING MUSIC PLAYER (single instance)
   =========================== */
document.addEventListener("DOMContentLoaded", () => {
    const player = document.getElementById("floating-player");
    const audio = document.getElementById("global-audio");
    const playControl = document.getElementById("fp-play");
    const nextBtn = document.getElementById("fp-next");
    const prevBtn = document.getElementById("fp-prev");
    const shuffleBtn = document.getElementById("fp-shuffle");
    const repeatBtn = document.getElementById("fp-repeat");
    const coverImg = document.getElementById("fp-cover-img");
    const titleEl = document.getElementById("fp-title");
    const subtitleEl = document.getElementById("fp-subtitle");
    const currentTimeEl = document.getElementById("fp-current-time");
    const durationEl = document.getElementById("fp-duration");
    const seekInput = document.getElementById("fp-seek");
    const volumeInput = document.getElementById("fp-volume");
    const muteBtn = document.getElementById("fp-mute");
    const trackButtons = Array.from(document.querySelectorAll(".play-track-btn"));

    if (!player || !audio || !trackButtons.length || !seekInput || !volumeInput || !muteBtn) return;

    let shuffle = false;
    let repeatMode = "off"; // off | all | one
    let currentIndex = null;

    const formatTime = (secs) => {
        if (!Number.isFinite(secs)) return "0:00";
        const m = Math.floor(secs / 60);
        const s = Math.floor(secs % 60).toString().padStart(2, "0");
        return `${m}:${s}`;
    };

    const playlist = trackButtons.map((btn, index) => ({
        id: btn.dataset.trackId,
        title: btn.dataset.title || "Untitled",
        composer: btn.dataset.composer || "",
        performer: btn.dataset.performer || "",
        file: btn.dataset.file,
        cover: btn.dataset.cover || "/static/images/default_music_cover.jpg",
        button: btn,
        card: btn.closest(".music-track-card"),
        index
    })).filter((t) => t.file);

    if (!playlist.length) {
        player.style.display = "none";
        return;
    }

    const updateShuffleLabel = () => {
        shuffleBtn.classList.toggle("is-active", shuffle);
        shuffleBtn.setAttribute("aria-pressed", String(shuffle));
    };

    const updateRepeatLabel = () => {
        repeatBtn.classList.toggle("is-active", repeatMode !== "off");
        repeatBtn.classList.toggle("repeat-one", repeatMode === "one");
        repeatBtn.setAttribute("aria-pressed", repeatMode !== "off");
        const label = repeatMode === "one" ? "Repeat one" : repeatMode === "all" ? "Repeat all" : "Repeat off";
        repeatBtn.setAttribute("aria-label", label);
    };

    const setMeta = (track) => {
        if (coverImg) coverImg.src = track.cover;
        if (titleEl) titleEl.textContent = track.title || "Untitled";
        if (subtitleEl) {
            const parts = [track.composer, track.performer].filter(Boolean);
            subtitleEl.textContent = parts.join(" — ") || "";
        }
    };

    const updatePlayUI = () => {
        const isPlaying = !audio.paused;
        playControl.textContent = "";
        playControl.classList.toggle("is-playing", isPlaying);
        playControl.setAttribute("aria-label", isPlaying ? "Pause" : "Play");
        playlist.forEach(({ button, index, card }) => {
            if (!button) return;
            if (index === currentIndex) {
                button.textContent = isPlaying ? "⏸" : "▶";
                card?.classList.toggle("is-playing", isPlaying);
            } else {
                button.textContent = "▶";
                card?.classList.remove("is-playing");
            }
        });
    };

    const loadTrack = (index, autoplay = false) => {
        const track = playlist[index];
        if (!track) return;
        currentIndex = index;
        audio.src = track.file;
        audio.loop = repeatMode === "one";
        if (seekInput) seekInput.value = "0";
        if (currentTimeEl) currentTimeEl.textContent = "0:00";
        if (durationEl) durationEl.textContent = formatTime(audio.duration || 0);
        setMeta(track);
        updatePlayUI();
        if (autoplay) audio.play().catch(() => {});
    };

    const getNextIndex = (forward = true) => {
        if (shuffle) {
            if (playlist.length === 1) return currentIndex;
            let next = currentIndex;
            while (next === currentIndex) {
                next = Math.floor(Math.random() * playlist.length);
            }
            return next;
        }
        const delta = forward ? 1 : -1;
        let next = currentIndex !== null ? currentIndex + delta : 0;
        if (next >= playlist.length) return repeatMode === "all" ? 0 : null;
        if (next < 0) return repeatMode === "all" ? playlist.length - 1 : null;
        return next;
    };

    const handleEnded = () => {
        if (repeatMode === "one") {
            audio.currentTime = 0;
            audio.play().catch(() => {});
            return;
        }
        const next = getNextIndex(true);
        if (next === null || next === undefined) {
            updatePlayUI();
            return;
        }
        loadTrack(next, true);
    };

    trackButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            const idx = playlist.findIndex((t) => t.id === btn.dataset.trackId);
            if (idx === -1) return;

            if (currentIndex === idx) {
                if (audio.paused) audio.play().catch(() => {});
                else audio.pause();
            } else {
                loadTrack(idx, true);
            }
        });
    });

    playControl.addEventListener("click", () => {
        if (currentIndex === null) {
            loadTrack(0, true);
            return;
        }
        if (audio.paused) audio.play().catch(() => {});
        else audio.pause();
    });

    nextBtn.addEventListener("click", () => {
        const next = getNextIndex(true);
        if (next === null || next === undefined) return;
        loadTrack(next, true);
    });

    prevBtn.addEventListener("click", () => {
        const prev = getNextIndex(false);
        if (prev === null || prev === undefined) return;
        loadTrack(prev, true);
    });

    shuffleBtn.addEventListener("click", () => {
        shuffle = !shuffle;
        updateShuffleLabel();
    });

    repeatBtn.addEventListener("click", () => {
        repeatMode = repeatMode === "off" ? "all" : repeatMode === "all" ? "one" : "off";
        audio.loop = repeatMode === "one";
        updateRepeatLabel();
    });

    audio.addEventListener("ended", handleEnded);
    audio.addEventListener("play", updatePlayUI);
    audio.addEventListener("pause", updatePlayUI);
    audio.addEventListener("timeupdate", () => {
        if (!audio.duration || !seekInput) return;
        const pct = (audio.currentTime / audio.duration) * 100;
        seekInput.value = String(pct);
        if (currentTimeEl) currentTimeEl.textContent = formatTime(audio.currentTime);
        if (durationEl) durationEl.textContent = formatTime(audio.duration);
    });

    audio.addEventListener("loadedmetadata", () => {
        if (durationEl) durationEl.textContent = formatTime(audio.duration || 0);
    });

    seekInput.addEventListener("input", () => {
        if (!audio.duration) return;
        const pct = Number(seekInput.value) / 100;
        audio.currentTime = audio.duration * pct;
    });

    // Volume
    volumeInput.addEventListener("input", () => {
        const vol = Math.min(100, Math.max(0, Number(volumeInput.value || 0)));
        audio.volume = vol / 100;
        muteBtn.classList.toggle("is-muted", audio.volume === 0);
        muteBtn.setAttribute("aria-pressed", audio.volume === 0);
    });
    volumeInput.value = String(Math.round(audio.volume * 100));

    muteBtn.addEventListener("click", () => {
        const isMuted = muteBtn.classList.toggle("is-muted");
        audio.muted = isMuted;
        muteBtn.setAttribute("aria-pressed", isMuted);
        if (!isMuted && audio.volume === 0) {
            audio.volume = 0.5;
            volumeInput.value = "50";
        }
        if (isMuted) {
            volumeInput.value = "0";
        } else {
            volumeInput.value = String(Math.round(audio.volume * 100));
        }
    });

    updateShuffleLabel();
    updateRepeatLabel();
    playControl.setAttribute("aria-label", "Play");

    // Preload the first track into the player (paused) for a populated UI
    if (playlist.length > 0) {
        loadTrack(0, false);
    }
});

/* ===========================
   Home page menu carousel
   =========================== */
document.addEventListener("DOMContentLoaded", () => {
    const track = document.getElementById("menu-track");
    const windowEl = document.getElementById("menu-window");
    const prev = document.getElementById("menu-prev");
    const next = document.getElementById("menu-next");
    if (!track || !windowEl || !prev || !next) return;
    initCarousel({
        windowEl,
        track,
        prev,
        next,
        cardSelector: ".menu-card-compact",
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const track = document.getElementById("music-track");
    const windowEl = document.getElementById("music-window");
    const prev = document.getElementById("music-prev");
    const next = document.getElementById("music-next");
    if (!track || !windowEl || !prev || !next) return;
    initCarousel({
        windowEl,
        track,
        prev,
        next,
        cardSelector: ".home-music-card",
    });
});

function initCarousel({ windowEl, track, prev, next, cardSelector }) {
    const cardWidth = () => {
        const first = track.querySelector(cardSelector);
        if (!first) return 300;
        const gap = parseFloat(getComputedStyle(track).columnGap || getComputedStyle(track).gap || "12") || 12;
        return first.getBoundingClientRect().width + gap;
    };

    const maxScroll = () => Math.max(0, track.scrollWidth - windowEl.clientWidth);

    const updateButtons = () => {
        prev.disabled = windowEl.scrollLeft <= 0;
        next.disabled = windowEl.scrollLeft >= maxScroll() - 4;
    };

    prev.addEventListener("click", () => {
        windowEl.scrollBy({ left: -cardWidth(), behavior: "smooth" });
        setTimeout(updateButtons, 250);
    });

    next.addEventListener("click", () => {
        windowEl.scrollBy({ left: cardWidth(), behavior: "smooth" });
        setTimeout(updateButtons, 250);
    });

    windowEl.addEventListener("scroll", updateButtons);
    updateButtons();
}

/* ===========================
   Missing track notice
   =========================== */
document.addEventListener("DOMContentLoaded", () => {
    document.body.addEventListener("click", (e) => {
        const btn = e.target.closest(".cover-missing-btn");
        if (!btn) return;
        const title = btn.dataset.title || "This track";
        alert(`${title} is unavailable right now.`);
    });
});
