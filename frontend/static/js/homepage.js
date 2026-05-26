document.addEventListener("DOMContentLoaded", () => {
  const sentences = [
    "1. Your smart AI companion for campus queries!",
    "2. Empowering students through information.",
    "3. Your trusted guide to campus life and beyond."
  ];
  const banner = document.getElementById("hero-banner");

  sentences.forEach((text, index) => {
    const p = document.createElement("p");
    p.textContent = text;
    p.style.animationDelay = `${index * 2}s`;
    banner.appendChild(p);
  });

  document.getElementById("create-btn").onclick = () => openPopup("Create Account");
  document.getElementById("login-btn").onclick = () => openPopup("Login");
  document.getElementById("close-popup").onclick = () => document.getElementById("popup").style.display = "none";

  document.getElementById("submit-btn").onclick = handleLogin;
  document.getElementById("register-submit-btn").onclick = handleRegister;

  // Password toggles
  document.getElementById("show-login-password").addEventListener("change", (e) => {
    document.getElementById("password").type = e.target.checked ? "text" : "password";
  });

  document.getElementById("show-register-password").addEventListener("change", (e) => {
    document.getElementById("reg_password").type = e.target.checked ? "text" : "password";
  });
});

function openPopup(mode) {
  document.getElementById("popup").style.display = "flex";
  document.getElementById("popup-title").innerText = mode;

  document.getElementById("login-form").style.display = mode === "Login" ? "block" : "none";
  document.getElementById("register-form").style.display = mode === "Create Account" ? "block" : "none";

  document.getElementById("error-msg").innerText = "";
  document.getElementById("register-error-msg").innerText = "";
}

async function handleLogin(e) {
  e.preventDefault();

  const email = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const role = document.getElementById("role").value;
  const errorMsg = document.getElementById("error-msg");

  if (!email.endsWith("@college.com")) {
    errorMsg.innerText = "Email must end with @college.com";
    return;
  }

  const passwordRegex = /^(?=.*[A-Z])(?=.*[@$!%*?&]).{6,}$/;
  if (!passwordRegex.test(password)) {
    errorMsg.innerText = "Password must have 6+ characters, 1 capital letter & 1 special character.";
    return;
  }

  try {
    const res = await fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      credentials: "include",
      body: `email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}&role=${role}`
    });

    if (res.redirected) {
      window.location.href = res.url;
    } else {
      const msg = await res.text();
      errorMsg.innerText = msg;
    }
  } catch (err) {
    console.error("Error:", err);
    errorMsg.innerText = "Server error. Please try again.";
  }
}

async function handleRegister(e) {
  e.preventDefault();

  const name = document.getElementById("reg_name").value.trim();
  const contact = document.getElementById("reg_contact").value.trim();
  const dept = document.getElementById("reg_dept").value.trim();
  const email = document.getElementById("reg_email").value.trim();
  const password = document.getElementById("reg_password").value.trim();
  const errorMsg = document.getElementById("register-error-msg");

  if (!name || !contact || !dept || !email || !password) {
    errorMsg.innerText = "All fields are required.";
    return;
  }

  if (!/^\d{10}$/.test(contact)) {
    errorMsg.innerText = "Phone number must be 10 digits.";
    return;
  }

  if (!email.endsWith("@college.com")) {
    errorMsg.innerText = "Email must end with @college.com";
    return;
  }

  const passwordRegex = /^(?=.*[A-Z])(?=.*[@$!%*?&]).{6,}$/;
  if (!passwordRegex.test(password)) {
    errorMsg.innerText = "Password must have 6+ characters, 1 capital letter & 1 special character.";
    return;
  }

  try {
    const res = await fetch("/register", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `name=${encodeURIComponent(name)}&contact=${encodeURIComponent(contact)}&department=${encodeURIComponent(dept.toLowerCase())}&email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
    });

    const text = await res.text();
    if (res.ok) {
      alert("✅ Account created successfully!");
      document.getElementById("popup").style.display = "none";
    } else {
      errorMsg.innerText = text;
    }
  } catch (err) {
    console.error("Error:", err);
    errorMsg.innerText = "Registration failed. Please try again.";
  }
}
