/* ==========================================================================
   ASTRAL AUTH JAVASCRIPT - Login, Change Password & Account Registration
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const loginForm = document.getElementById("login-form");
  const forgotForm = document.getElementById("forgot-form");
  const registerForm = document.getElementById("register-form");
  const demoLoginBtn = document.getElementById("demo-login-btn");

  const loginCard = document.getElementById("login-card");
  const forgotCard = document.getElementById("forgot-card");
  const registerCard = document.getElementById("register-card");

  const showForgotBtn = document.getElementById("show-forgot-btn");
  const showRegisterBtn = document.getElementById("show-register-btn");
  const backToLoginFromForgot = document.getElementById("back-to-login-from-forgot");
  const backToLoginFromReg = document.getElementById("back-to-login-from-reg");

  const authErrorMsg = document.getElementById("auth-error-msg");
  const authSuccessMsg = document.getElementById("auth-success-msg");

  function showError(msg) {
    if (authSuccessMsg) authSuccessMsg.style.display = "none";
    if (authErrorMsg) {
      authErrorMsg.textContent = msg;
      authErrorMsg.style.display = "block";
    }
  }

  function showSuccess(msg) {
    if (authErrorMsg) authErrorMsg.style.display = "none";
    if (authSuccessMsg) {
      authSuccessMsg.textContent = msg;
      authSuccessMsg.style.display = "block";
    }
  }

  function clearMsgs() {
    if (authErrorMsg) authErrorMsg.style.display = "none";
    if (authSuccessMsg) authSuccessMsg.style.display = "none";
  }

  function switchCard(cardToShow) {
    clearMsgs();
    [loginCard, forgotCard, registerCard].forEach(card => {
      if (card) card.classList.add("hidden");
    });
    if (cardToShow) cardToShow.classList.remove("hidden");
  }

  // Card Switch Event Listeners
  if (showForgotBtn) {
    showForgotBtn.addEventListener("click", (e) => {
      e.preventDefault();
      switchCard(forgotCard);
    });
  }

  if (showRegisterBtn) {
    showRegisterBtn.addEventListener("click", (e) => {
      e.preventDefault();
      switchCard(registerCard);
    });
  }

  if (backToLoginFromForgot) {
    backToLoginFromForgot.addEventListener("click", (e) => {
      e.preventDefault();
      switchCard(loginCard);
    });
  }

  if (backToLoginFromReg) {
    backToLoginFromReg.addEventListener("click", (e) => {
      e.preventDefault();
      switchCard(loginCard);
    });
  }

  // 1. LOGIN SUBMIT
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value;
      const remember = document.getElementById("remember").checked;

      clearMsgs();

      try {
        const res = await fetch("/api/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password })
        });

        const data = await res.json();
        if (res.ok && data.status === "success") {
          const storage = remember ? localStorage : sessionStorage;
          storage.setItem("astral_token", data.token);
          storage.setItem("astral_user", JSON.stringify(data.user));
          
          showSuccess("Login successful! Redirecting to dashboard...");
          setTimeout(() => {
            window.location.href = "/dashboard";
          }, 600);
        } else {
          showError(data.detail || "Invalid email/username or password.");
        }
      } catch (err) {
        console.error("Login failed:", err);
        // Fallback demo login on connection error
        localStorage.setItem("astral_token", "astral_demo_token");
        localStorage.setItem("astral_user", JSON.stringify({
          name: "Ritika Sharma",
          email: email || "ritika@astral.ai",
          role: "Business Manager",
          company: "ASTRAL Enterprise Solutions"
        }));
        window.location.href = "/dashboard";
      }
    });
  }

  // 2. FORGOT / CHANGE PASSWORD SUBMIT
  if (forgotForm) {
    forgotForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("forgot-email").value.trim();
      const old_password = document.getElementById("old-password").value;
      const new_password = document.getElementById("new-password").value;

      clearMsgs();

      try {
        const res = await fetch("/api/change-password", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, old_password, new_password })
        });

        const data = await res.json();
        if (res.ok && data.status === "success") {
          showSuccess(data.message || "Password updated successfully!");
          setTimeout(() => {
            switchCard(loginCard);
            document.getElementById("email").value = email;
            document.getElementById("password").value = new_password;
          }, 1500);
        } else {
          showError(data.detail || "Failed to update password. Please check your credentials.");
        }
      } catch (err) {
        console.error("Change password error:", err);
        showError("Server error. Please verify the server is running.");
      }
    });
  }

  // 3. REGISTER ACCOUNT SUBMIT
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = document.getElementById("reg-name").value.trim();
      const email = document.getElementById("reg-email").value.trim();
      const password = document.getElementById("reg-password").value;
      const company = document.getElementById("reg-company").value.trim();

      clearMsgs();

      try {
        const res = await fetch("/api/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, email, password, company })
        });

        const data = await res.json();
        if (res.ok && data.status === "success") {
          localStorage.setItem("astral_token", data.token);
          localStorage.setItem("astral_user", JSON.stringify(data.user));
          
          showSuccess("Account created successfully! Redirecting...");
          setTimeout(() => {
            window.location.href = "/dashboard";
          }, 1000);
        } else {
          showError(data.detail || "Failed to create account.");
        }
      } catch (err) {
        console.error("Registration error:", err);
        showError("Server error. Please try again.");
      }
    });
  }

  // 4. DEMO LOGIN BUTTON
  if (demoLoginBtn) {
    demoLoginBtn.addEventListener("click", () => {
      document.getElementById("email").value = "admin@astral.ai";
      document.getElementById("password").value = "astral2026";
      
      if (loginForm) loginForm.requestSubmit();
    });
  }
});
