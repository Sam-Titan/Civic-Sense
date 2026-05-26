const API = "http://localhost:8000";

// --- Helpers ---
function showError(id, message) {
    const el = document.getElementById(id);
    el.textContent = message;
    el.style.display = "block";
}

function hideError(id) {
    document.getElementById(id).style.display = "none";
}

function showStep(stepId) {
    document.getElementById("step-login").style.display = "none";
    document.getElementById("step-register").style.display = "none";
    document.getElementById(stepId).style.display = "block";
}


// --- Login ---
window.login = async function () {
    const digits = document.getElementById("phone-input").value.trim();
    const password = document.getElementById("password-input").value.trim();
    const role = document.getElementById("role-select").value;
    hideError("login-error");

    // Validate phone
    if (digits.length !== 10) {
        showError("login-error", "Please enter a valid 10 digit phone number.");
        return;
    }

    // Validate password
    if (!password) {
        showError("login-error", "Please enter your password.");
        return;
    }

    const phone = "+91" + digits;

    try {
        const res = await fetch(`${API}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",             // send and receive cookies
            body: JSON.stringify({ phone_number: phone, password, role })
        });

        const data = await res.json();

        if (!res.ok) {
            showError("login-error", data.detail || "Login failed.");
            return;
        }

        // Store role for page guards
        localStorage.setItem("role", data.role);

        if (data.is_new_user) {
            showStep("step-register");
        } else {
            redirectByRole(data.role);
        }

    } catch (err) {
        showError("login-error", "Could not reach server. Please try again.");
    }
};


// --- Register profile (first time only) ---
window.registerUser = async function () {
    const name = document.getElementById("reg-name").value.trim();
    const address = document.getElementById("reg-address").value.trim();
    const locality = document.getElementById("reg-locality").value.trim();
    hideError("register-error");

    if (!name || !address || !locality) {
        showError("register-error", "Please fill in all fields.");
        return;
    }

    try {
        const res = await fetch(`${API}/users/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",             // send session cookie
            body: JSON.stringify({ name, address, locality })
        });

        const data = await res.json();

        if (res.ok) {
            redirectByRole(localStorage.getItem("role"));
        } else {
            showError("register-error", data.detail || "Registration failed.");
        }

    } catch (err) {
        showError("register-error", "Could not reach server. Please try again.");
    }
};


// --- Redirect by role ---
function redirectByRole(role) {
    if (role === "rwa_admin") {
        window.location.href = "admin.html";
    } else {
        window.location.href = "dashboard.html";
    }
}


// --- Logout (called from dashboard and admin pages) ---
window.logout = async function () {
    try {
        await fetch(`${API}/auth/logout`, {
            method: "POST",
            credentials: "include"
        });
    } catch (err) {
        console.error("Logout error:", err);
    } finally {
        localStorage.clear();
        window.location.href = "index.html";
    }
}