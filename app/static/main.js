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
});

// Toggle Login <-> Register inside modal
toggleAuthMode?.addEventListener("click", () => {
  if (submitBtn.innerText === "Login") setRegisterMode();
  else setLoginMode();
});

function setLoginMode() {
  modalTitle.innerText = "Login";
  submitBtn.innerText = "Login";
  form.action = "/auth/login_form";
  firstNameField.style.display = "none";
  lastNameField.style.display = "none";
  toggleText.innerText = "Don't have an account?";
  toggleAuthMode.innerText = "Register";
}

function setRegisterMode() {
  modalTitle.innerText = "Register";
  submitBtn.innerText = "Register";
  form.action = "/auth/register_form";
  firstNameField.style.display = "block";
  lastNameField.style.display = "block";
  toggleText.innerText = "Already have an account?";
  toggleAuthMode.innerText = "Login";
}