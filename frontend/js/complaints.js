const API = "http://localhost:8000";

// --- Page guard ---
const role = localStorage.getItem("role");
if (!role) {
    window.location.href = "index.html";
}


// --- Load page on start ---
document.addEventListener("DOMContentLoaded", () => {
    loadProfile();
    loadComplaints();
});


// --- Load user profile ---
async function loadProfile() {
    try {
        const res = await fetch(`${API}/users/me`, {
            credentials: "include"
        });

        if (res.status === 401) {
            window.location.href = "index.html";
            return;
        }

        const data = await res.json();

        document.getElementById("user-name").textContent = data.name;
        document.getElementById("complaint-address").value = data.address;

    } catch (err) {
        console.error("Failed to load profile:", err);
    }
}


// --- Load complaints ---
async function loadComplaints() {
    try {
        const res = await fetch(`${API}/complaints/me`, {
            credentials: "include"
        });

        if (res.status === 401) {
            window.location.href = "index.html";
            return;
        }

        const complaints = await res.json();
        const list = document.getElementById("complaints-list");

        if (complaints.length === 0) {
            list.innerHTML = "<p>No complaints filed yet.</p>";
            return;
        }

        // Hide form if open complaint exists
        const hasOpen = complaints.some(c =>
            c.status === "Pending" || c.status === "Acknowledged"
        );

        if (hasOpen) {
            document.getElementById("complaint-form-card").style.display = "none";
        } else {
            document.getElementById("complaint-form-card").style.display = "block";
        }

        // Render complaints
        list.innerHTML = complaints.map(c => `
            <div class="complaint-item">
                <div class="complaint-header">
                    <span class="complaint-date">
                        ${formatDate(c.created_at)}
                    </span>
                    <span class="badge badge-${c.status.toLowerCase()}">
                        ${c.status}
                    </span>
                </div>
                <p class="complaint-desc">${c.description}</p>
                <p class="complaint-meta">${c.address}</p>
                ${c.eta ? `
                    <p class="complaint-meta" style="color:#185FA5;">
                        Expected by: ${formatDate(c.eta)}
                    </p>` : ""}
                ${c.remarks ? `
                    <p class="complaint-meta">
                        Remark: ${c.remarks}
                    </p>` : ""}
                ${c.status === "Acknowledged" ? `
                    <button class="btn btn-primary"
                        style="margin-top:8px;"
                        onclick="resolveComplaint('${c.complaint_id}')">
                        Mark as resolved
                    </button>` : ""}
            </div>
        `).join("");

    } catch (err) {
        console.error("Failed to load complaints:", err);
    }
}


// --- File a new complaint ---
window.fileComplaint = async function () {
    const desc = document.getElementById("complaint-desc").value.trim();
    const formError = document.getElementById("form-error");
    const formSuccess = document.getElementById("form-success");

    formError.style.display = "none";
    formSuccess.style.display = "none";

    if (!desc) {
        formError.textContent = "Please describe the issue.";
        formError.style.display = "block";
        return;
    }

    try {
        const res = await fetch(`${API}/complaints`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ description: desc })
        });

        const data = await res.json();

        if (res.ok) {
            formSuccess.textContent = "Complaint filed successfully.";
            formSuccess.style.display = "block";
            document.getElementById("complaint-desc").value = "";
            loadComplaints();
        } else {
            formError.textContent = data.detail || "Failed to file complaint.";
            formError.style.display = "block";
        }

    } catch (err) {
        formError.textContent = "Could not reach server. Please try again.";
        formError.style.display = "block";
    }
};


// --- Resolve a complaint ---
window.resolveComplaint = async function (complaintId) {
    try {
        const res = await fetch(`${API}/complaints/${complaintId}/resolve`, {
            method: "PATCH",
            credentials: "include"
        });

        if (res.ok) {
            loadComplaints();
        } else {
            const data = await res.json();
            alert(data.detail || "Could not resolve complaint.");
        }

    } catch (err) {
        alert("Could not reach server. Please try again.");
    }
};


// --- Format date ---
function formatDate(timestamp) {
    if (!timestamp) return "—";
    const date = new Date(timestamp);
    return date.toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric"
    });
}