const API = "http://localhost:8000";

// --- Page guard ---
const role = localStorage.getItem("role");
if (!role || role !== "rwa_admin") {
    window.location.href = "index.html";
}


// --- Load page on start ---
document.addEventListener("DOMContentLoaded", () => {
    loadComplaints();
    loadWhitelist();
});


// --- Load all complaints ---
async function loadComplaints() {
    try {
        const res = await fetch(`${API}/admin/complaints`, {
            credentials: "include"
        });

        if (res.status === 401) {
            window.location.href = "index.html";
            return;
        }

        if (res.status === 403) {
            window.location.href = "dashboard.html";
            return;
        }

        const complaints = await res.json();

        // Update stats
        document.getElementById("stat-total").textContent = complaints.length;
        document.getElementById("stat-pending").textContent =
            complaints.filter(c => c.status === "Pending").length;
        document.getElementById("stat-acknowledged").textContent =
            complaints.filter(c => c.status === "Acknowledged").length;

        const list = document.getElementById("complaints-list");

        if (complaints.length === 0) {
            list.innerHTML = "<p>No complaints yet.</p>";
            return;
        }

        list.innerHTML = complaints.map(c => `
            <div class="complaint-item">
                <div class="complaint-header">
                    <span class="complaint-date">
                        #${c.complaint_id.slice(0, 8)} · ${formatDate(c.created_at)}
                    </span>
                    <span class="badge badge-${c.status.toLowerCase()}">
                        ${c.status}
                    </span>
                </div>
                <p class="complaint-desc">${c.description}</p>
                <p class="complaint-meta">${c.address} · ${c.locality}</p>

                ${c.status === "Pending" ? `
                    <label style="margin-top:8px;">Set ETA</label>
                    <input type="date" id="eta-${c.complaint_id}"
                        style="margin-bottom:8px;"
                        min="${new Date().toISOString().split("T")[0]}">
                    <button class="btn btn-primary"
                        onclick="acknowledgeComplaint('${c.complaint_id}')">
                        Acknowledge
                    </button>` : ""}

                ${c.status === "Acknowledged" ? `
                    <p class="complaint-meta" style="color:#185FA5; margin-top:6px;">
                        ETA: ${formatDate(c.eta)}
                    </p>
                    <label style="margin-top:8px;">Remark</label>
                    <input type="text" id="remark-${c.complaint_id}"
                        placeholder="Add a remark..."
                        value="${c.remarks || ""}"
                        style="margin-bottom:8px;">
                    <button class="btn btn-primary"
                        onclick="addRemark('${c.complaint_id}')">
                        Save remark
                    </button>` : ""}

                ${c.status === "Resolved" ? `
                    <p class="complaint-meta" style="color:#3B6D11; margin-top:6px;">
                        Resolved on ${formatDate(c.resolved_at)}
                    </p>
                    ${c.remarks ? `
                        <p class="complaint-meta">
                            Remark: ${c.remarks}
                        </p>` : ""}` : ""}
            </div>
        `).join("");

    } catch (err) {
        console.error("Failed to load complaints:", err);
    }
}


// --- Acknowledge complaint ---
window.acknowledgeComplaint = async function (complaintId) {
    const eta = document.getElementById(`eta-${complaintId}`).value;

    if (!eta) {
        alert("Please set an ETA before acknowledging.");
        return;
    }

    try {
        const res = await fetch(
            `${API}/admin/complaints/${complaintId}/acknowledge`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ eta: new Date(eta).toISOString() })
        });

        if (res.ok) {
            loadComplaints();
        } else {
            const data = await res.json();
            alert(data.detail || "Could not acknowledge complaint.");
        }

    } catch (err) {
        alert("Could not reach server. Please try again.");
    }
};


// --- Add remark ---
window.addRemark = async function (complaintId) {
    const remark = document
        .getElementById(`remark-${complaintId}`)
        .value.trim();

    if (!remark) {
        alert("Please enter a remark.");
        return;
    }

    try {
        const res = await fetch(
            `${API}/admin/complaints/${complaintId}/remarks`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ remarks: remark })
        });

        if (res.ok) {
            loadComplaints();
        } else {
            const data = await res.json();
            alert(data.detail || "Could not save remark.");
        }

    } catch (err) {
        alert("Could not reach server. Please try again.");
    }
};


// --- Load whitelist ---
async function loadWhitelist() {
    try {
        const res = await fetch(`${API}/admin/whitelist`, {
            credentials: "include"
        });

        const entries = await res.json();
        const list = document.getElementById("whitelist-list");

        if (entries.length === 0) {
            list.innerHTML = "<p>No numbers whitelisted yet.</p>";
            return;
        }

        list.innerHTML = entries.map(e => `
            <div style="display:flex; align-items:center; 
                gap:8px; padding:8px 0; 
                border-bottom:1px solid #DDE1E7;">
                <span style="flex:1; font-size:13px;">
                    ${e.phone_number}
                </span>
                <span style="font-size:11px; color:#555;">
                    ${e.is_active ? "Active" : "Inactive"}
                </span>
                ${e.is_active ? `
                    <button class="btn btn-danger"
                        style="width:auto; padding:4px 10px; 
                            margin:0; font-size:11px;"
                        onclick="removeFromWhitelist('${e.phone_number}')">
                        Remove
                    </button>` : ""}
            </div>
        `).join("");

    } catch (err) {
        console.error("Failed to load whitelist:", err);
    }
}


// --- Add to whitelist ---
window.addToWhitelist = async function () {
    const digits = document.getElementById("whitelist-phone").value.trim();
    const errorEl = document.getElementById("whitelist-error");
    const successEl = document.getElementById("whitelist-success");

    errorEl.style.display = "none";
    successEl.style.display = "none";

    if (digits.length !== 10) {
        errorEl.textContent = "Please enter a valid 10 digit phone number.";
        errorEl.style.display = "block";
        return;
    }

    const phone = "+91" + digits;

    // Get admin name from profile
    let adminName = "RWA Admin";
    try {
        const profileRes = await fetch(`${API}/users/me`, {
            credentials: "include"
        });
        const profile = await profileRes.json();
        adminName = profile.name || "RWA Admin";
    } catch (err) {
        console.error("Could not fetch admin name:", err);
    }

    try {
        const res = await fetch(`${API}/admin/whitelist`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({
                phone_number: phone,
                added_by: adminName
            })
        });

        const data = await res.json();

        if (res.ok) {
            successEl.textContent = data.message;
            successEl.style.display = "block";
            document.getElementById("whitelist-phone").value = "";
            loadWhitelist();
        } else {
            errorEl.textContent = data.detail || "Could not add number.";
            errorEl.style.display = "block";
        }

    } catch (err) {
        errorEl.textContent = "Could not reach server. Please try again.";
        errorEl.style.display = "block";
    }
};


// --- Remove from whitelist ---
window.removeFromWhitelist = async function (phone) {
    if (!confirm(`Remove ${phone} from whitelist?`)) return;

    try {
        const res = await fetch(
            `${API}/admin/whitelist/${encodeURIComponent(phone)}`, {
            method: "DELETE",
            credentials: "include"
        });

        if (res.ok) {
            loadWhitelist();
        } else {
            const data = await res.json();
            alert(data.detail || "Could not remove number.");
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