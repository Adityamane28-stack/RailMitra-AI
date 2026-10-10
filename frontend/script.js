// =====================================================
// API CONFIGURATION
// =====================================================

const API_URL = (
    window.location.origin &&
    !window.location.origin.includes(":5500") &&
    !window.location.origin.includes(":3000") &&
    !window.location.origin.startsWith("file:")
) ? window.location.origin : "http://127.0.0.1:8000";

let allComplaints = [];
let currentFilterChip = "ALL";

// =====================================================
// TOAST NOTIFICATION SYSTEM
// =====================================================

function showToast(message, type = "info") {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    let icon = "ℹ️";
    if (type === "success") icon = "✅";
    if (type === "error") icon = "❌";
    if (type === "warning") icon = "⚠️";

    toast.innerHTML = `<span>${icon}</span> <span>${escapeHTML(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(40px)";
        toast.style.transition = "all 0.3s ease";
        setTimeout(() => toast.remove(), 350);
    }, 3800);
}

// =====================================================
// AUTHENTICATION HEADERS
// =====================================================

function getAdminToken() {
    return localStorage.getItem("adminToken");
}

function getAuthHeaders() {
    const token = getAdminToken();
    if (!token) {
        window.location.href = "login.html";
        return {};
    }
    return {
        "Authorization": "Bearer " + token
    };
}

function logout() {
    localStorage.removeItem("adminToken");
    localStorage.removeItem("adminRole");
    localStorage.removeItem("adminUsername");
    sessionStorage.removeItem("adminLoggedIn");
    showToast("Logged out successfully", "info");
    setTimeout(() => {
        window.location.href = "login.html";
    }, 400);
}

// =====================================================
// CONVERT EVIDENCE PATH TO BROWSER URL
// =====================================================

function getEvidenceURL(evidencePath) {
    if (!evidencePath) return null;
    const normalized = String(evidencePath).replace(/\\/g, "/");
    const idx = normalized.toLowerCase().indexOf("/uploads/");
    if (idx === -1) {
        if (normalized.startsWith("uploads/")) {
            return `${API_URL}/${normalized}`;
        }
        return null;
    }
    const rel = normalized.substring(idx + 1);
    return `${API_URL}/${rel}`;
}

// =====================================================
// ANIMATE NUMBERS (KPI COUNTER EFFECT)
// =====================================================

function animateCounter(elementId, target) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const targetNum = Number(target) || 0;
    const duration = 600;
    const startNum = 0;
    const startTime = performance.now();

    function update(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const current = Math.floor(progress * targetNum);
        el.textContent = current;
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            el.textContent = targetNum;
        }
    }
    requestAnimationFrame(update);
}

// =====================================================
// LOAD DASHBOARD SUMMARY (ADMIN)
// =====================================================

async function loadDashboard() {
    try {
        const response = await fetch(`${API_URL}/complaints/dashboard/summary`, {
            method: "GET",
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                logout();
                return;
            }
            throw new Error(`Dashboard API error: ${response.status}`);
        }

        const data = await response.json();

        animateCounter("totalComplaints", data.total_complaints);
        animateCounter("pendingComplaints", data.pending);
        animateCounter("inProgressComplaints", data.in_progress);
        animateCounter("resolvedComplaints", data.resolved);
        animateCounter("criticalComplaints", data.critical);
        animateCounter("highComplaints", data.high_priority);

        loadDepartments(data.department_wise || {}, data.total_complaints || 1);
    } catch (error) {
        console.error("Dashboard error:", error);
    }
}

// =====================================================
// LOAD DEPARTMENT BREAKDOWN WITH ANIMATED PROGRESS BARS
// =====================================================

function loadDepartments(departments, total) {
    const container = document.getElementById("departments");
    if (!container) return;
    container.innerHTML = "";

    const names = Object.keys(departments);
    if (names.length === 0) {
        container.innerHTML = "<p style='color:#64748b;'>No department complaints logged yet.</p>";
        return;
    }

    names.forEach(dept => {
        const count = departments[dept];
        const pct = Math.min(100, Math.round((count / (total || 1)) * 100));

        const div = document.createElement("div");
        div.className = "department-item";
        div.innerHTML = `
            <div class="department-header">
                <span>🚆 ${escapeHTML(dept)}</span>
                <span>${count} (${pct}%)</span>
            </div>
            <div class="dept-bar-bg">
                <div class="dept-bar-fill" style="width: 0%;" data-target="${pct}%"></div>
            </div>
        `;
        container.appendChild(div);
    });

    // Trigger animation
    setTimeout(() => {
        document.querySelectorAll(".dept-bar-fill").forEach(bar => {
            bar.style.width = bar.getAttribute("data-target") || "0%";
        });
    }, 50);
}

// =====================================================
// LOAD ALL COMPLAINTS (ADMIN)
// =====================================================

async function loadComplaints() {
    const tableBody = document.getElementById("complaintTable");
    if (!tableBody) return;

    tableBody.innerHTML = `
        <tr>
            <td colspan="9" style="text-align:center; padding: 25px; color:#64748b;">
                <div style="display:inline-block; animation: spin 1s linear infinite; margin-right: 8px;">⏳</div>
                Loading railway complaints...
            </td>
        </tr>
    `;

    try {
        const response = await fetch(`${API_URL}/complaints/`, {
            method: "GET",
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                logout();
                return;
            }
            throw new Error(`Complaints API failed with status ${response.status}`);
        }

        const data = await response.json();
        allComplaints = data.complaints || [];
        applyFilters();
    } catch (error) {
        console.error("Error loading complaints:", error);
        tableBody.innerHTML = `
            <tr>
                <td colspan="9" style="text-align:center; color:#dc2626; padding:20px;">
                    Failed to fetch complaints: ${escapeHTML(error.message)}
                </td>
            </tr>
        `;
    }
}

// =====================================================
// FILTER & SEARCH LOGIC
// =====================================================

function setFilterChip(chipType, element) {
    currentFilterChip = chipType;
    document.querySelectorAll(".filter-chip").forEach(c => c.classList.remove("active"));
    if (element) element.classList.add("active");
    applyFilters();
}

function applyFilters() {
    const searchVal = (document.getElementById("searchComplaint")?.value || "").trim().toLowerCase();
    const statusVal = document.getElementById("statusFilter")?.value || "";
    const priorityVal = document.getElementById("priorityFilter")?.value || "";
    const categoryVal = document.getElementById("categoryFilter")?.value || "";
    const departmentVal = document.getElementById("departmentFilter")?.value || "";

    const filtered = allComplaints.filter(c => {
        const name = String(c.passenger_name || "").toLowerCase();
        const train = String(c.train_number || "").toLowerCase();
        const pnr = String(c.pnr_number || "").toLowerCase();
        const desc = String(c.description || "").toLowerCase();
        const cat = String(c.complaint_category || "").toLowerCase();
        const dep = String(c.department || "").toLowerCase();

        const matchesSearch = !searchVal || (
            name.includes(searchVal) ||
            train.includes(searchVal) ||
            pnr.includes(searchVal) ||
            desc.includes(searchVal) ||
            cat.includes(searchVal) ||
            dep.includes(searchVal) ||
            String(c.id).includes(searchVal)
        );

        const matchesStatus = !statusVal || c.status === statusVal;
        const matchesPriority = !priorityVal || c.priority === priorityVal;
        const matchesCategory = !categoryVal || c.complaint_category === categoryVal;
        const matchesDepartment = !departmentVal || c.department === departmentVal;

        // Quick chip filter
        let matchesChip = true;
        if (currentFilterChip === "CRITICAL") matchesChip = c.priority === "Critical";
        if (currentFilterChip === "PENDING") matchesChip = c.status === "Pending";
        if (currentFilterChip === "PROGRESS") matchesChip = c.status === "In Progress";
        if (currentFilterChip === "RESOLVED") matchesChip = c.status === "Resolved";

        return matchesSearch && matchesStatus && matchesPriority && matchesCategory && matchesDepartment && matchesChip;
    });

    displayComplaints(filtered);
}

function clearFilters() {
    const inputs = ["searchComplaint", "statusFilter", "priorityFilter", "categoryFilter", "departmentFilter"];
    inputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });
    setFilterChip("ALL", document.querySelector(".filter-chip"));
}

// =====================================================
// DISPLAY COMPLAINTS TABLE
// =====================================================

function displayComplaints(complaints) {
    const tableBody = document.getElementById("complaintTable");
    if (!tableBody) return;
    tableBody.innerHTML = "";

    if (!complaints || complaints.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="9" style="text-align:center; padding: 30px; color:#64748b;">
                    No complaints matched your search criteria.
                </td>
            </tr>
        `;
        return;
    }

    complaints.forEach(c => {
        const row = document.createElement("tr");

        // Priority class
        let prioClass = "prio-medium";
        const p = (c.priority || "").toLowerCase();
        if (p === "critical") prioClass = "prio-critical";
        else if (p === "high") prioClass = "prio-high";
        else if (p === "low") prioClass = "prio-low";

        // Status class
        let statusClass = "pending";
        if (c.status === "In Progress") statusClass = "in-progress";
        else if (c.status === "Resolved") statusClass = "resolved";

        const evUrl = getEvidenceURL(c.evidence_path);
        let evButton = `<span style="color:#94a3b8; font-size:12px;">None</span>`;
        if (evUrl) {
            const evType = (c.evidence_type || "file").toUpperCase();
            evButton = `
                <button class="button-secondary" style="padding:4px 8px; font-size:11px;" onclick="viewEvidence('${escapeAttribute(evUrl)}', '${c.evidence_type || ""}')">
                    📎 ${evType}
                </button>
            `;
        }

        row.innerHTML = `
            <td><strong>#${c.id}</strong></td>
            <td>
                <div style="font-weight:600;">${escapeHTML(c.passenger_name || "Passenger")}</div>
                <div style="font-size:11px; color:#64748b;">${escapeHTML(c.phone_number || "-")}</div>
            </td>
            <td>
                <div>Train: <strong>${escapeHTML(c.train_number || "-")}</strong></div>
                <div style="font-size:11px; color:#64748b;">Coach: ${escapeHTML(c.coach_number || "-")} | PNR: ${escapeHTML(c.pnr_number || "-")}</div>
            </td>
            <td>
                <span style="font-weight:600;">${escapeHTML(c.complaint_category || "General")}</span>
            </td>
            <td>
                <span class="priority-badge ${prioClass}">
                    ${escapeHTML(c.priority || "Medium")}
                </span>
            </td>
            <td>
                <span style="font-size:12px;">${escapeHTML(c.department || "General")}</span>
            </td>
            <td>
                <span class="status-badge ${statusClass}">
                    ${escapeHTML(c.status || "Pending")}
                </span>
            </td>
            <td>${evButton}</td>
            <td>
                <div style="display:flex; gap:4px; flex-wrap:wrap;">
                    <button class="button-primary" style="padding:4px 8px; font-size:11px;" onclick="viewComplaint(${c.id})">
                        🔍 Inspect
                    </button>
                    ${c.status !== "Resolved" ? `
                        <button class="button-accent" style="padding:4px 8px; font-size:11px;" onclick="resolveComplaint(${c.id})">
                            ✅ Resolve
                        </button>
                    ` : ""}
                    <button class="btn-danger" style="padding:4px 8px; font-size:11px;" onclick="deleteComplaint(${c.id})">
                        🗑️
                    </button>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// =====================================================
// VIEW EVIDENCE MODAL / LIGHTBOX
// =====================================================

function viewEvidence(url, type) {
    if (!url) {
        showToast("No evidence file attached", "warning");
        return;
    }
    window.open(url, "_blank");
}

function createEvidenceHTML(url, type) {
    if (!url) return "<p style='color:#64748b;'>No evidence attached.</p>";
    const t = String(type || "").toLowerCase();

    if (t.includes("image") || url.match(/\.(jpg|jpeg|png|webp)$/i)) {
        return `
            <a href="${escapeAttribute(url)}" target="_blank" title="Click to view full size">
                <img src="${escapeAttribute(url)}" class="evidence-image" alt="Evidence Photo">
            </a>
            <div style="margin-top:6px; font-size:12px; color:#64748b;">Click image to open in high-res</div>
        `;
    }
    if (t.includes("video") || url.match(/\.(mp4|mpeg|mov|webm)$/i)) {
        return `
            <video controls class="evidence-video" src="${escapeAttribute(url)}"></video>
            <div style="margin-top:6px;"><a href="${escapeAttribute(url)}" target="_blank" style="color:#2563eb; font-size:12px;">Open Video in New Tab</a></div>
        `;
    }
    if (t.includes("audio") || url.match(/\.(mp3|wav|ogg|webm)$/i)) {
        return `
            <audio controls class="evidence-audio" src="${escapeAttribute(url)}"></audio>
            <div style="margin-top:6px;"><a href="${escapeAttribute(url)}" target="_blank" style="color:#2563eb; font-size:12px;">Open Audio in New Tab</a></div>
        `;
    }
    return `<a href="${escapeAttribute(url)}" target="_blank" class="button button-secondary">📥 Download Evidence File</a>`;
}

// =====================================================
// INSPECT COMPLAINT MODAL (ADMIN)
// =====================================================

async function viewComplaint(id) {
    const modal = document.getElementById("complaintModal");
    const details = document.getElementById("complaintDetails");
    if (!modal || !details) return;

    modal.style.display = "block";
    details.innerHTML = `<div style="text-align:center; padding:30px;"><div style="animation: spin 1s linear infinite; display:inline-block; font-size:24px;">⏳</div><p>Loading complaint #${id}...</p></div>`;

    try {
        const response = await fetch(`${API_URL}/complaints/${id}`, {
            method: "GET",
            headers: getAuthHeaders()
        });

        if (!response.ok) throw new Error("Failed to fetch complaint details");
        const c = await response.json();

        const evUrl = getEvidenceURL(c.evidence_path);
        const evHtml = createEvidenceHTML(evUrl, c.evidence_type);

        let confText = "N/A";
        if (c.ai_confidence != null) {
            confText = `${Math.round(Number(c.ai_confidence) * 100)}%`;
        }

        details.innerHTML = `
            <div class="complaint-details">
                <div class="detail-box">
                    <strong>Complaint ID</strong>
                    <span>#${c.id}</span>
                </div>
                <div class="detail-box">
                    <strong>Status</strong>
                    <span class="status-badge ${c.status === 'Resolved' ? 'resolved' : (c.status === 'In Progress' ? 'in-progress' : 'pending')}">${escapeHTML(c.status || "Pending")}</span>
                </div>
                <div class="detail-box">
                    <strong>Passenger Name</strong>
                    <span>${escapeHTML(c.passenger_name || "-")}</span>
                </div>
                <div class="detail-box">
                    <strong>Phone</strong>
                    <span>${escapeHTML(c.phone_number || "-")}</span>
                </div>
                <div class="detail-box">
                    <strong>PNR Number</strong>
                    <span>${escapeHTML(c.pnr_number || "-")}</span>
                </div>
                <div class="detail-box">
                    <strong>Train Number</strong>
                    <span>${escapeHTML(c.train_number || "-")}</span>
                </div>
                <div class="detail-box">
                    <strong>Coach / Seat</strong>
                    <span>${escapeHTML(c.coach_number || "-")} / ${escapeHTML(c.seat_number || "-")}</span>
                </div>
                <div class="detail-box">
                    <strong>Location</strong>
                    <span>${escapeHTML(c.location || "Onboard / In Transit")}</span>
                </div>
                <div class="detail-box">
                    <strong>AI Detected Issue</strong>
                    <span>${escapeHTML(c.ai_category || c.complaint_category || "-")}</span>
                </div>
                <div class="detail-box">
                    <strong>AI Confidence</strong>
                    <span style="color:#10b981;">${confText}</span>
                </div>
                <div class="detail-box">
                    <strong>Priority</strong>
                    <span class="priority-badge prio-${(c.priority || 'medium').toLowerCase()}">${escapeHTML(c.priority || "Medium")}</span>
                </div>
                <div class="detail-box">
                    <strong>Assigned Department</strong>
                    <span>${escapeHTML(c.department || "General Complaint")}</span>
                </div>
                <div class="detail-box">
                    <strong>Created At</strong>
                    <span>${formatDate(c.created_at)}</span>
                </div>
                <div class="detail-box">
                    <strong>Resolved At</strong>
                    <span>${formatDate(c.resolved_at)}</span>
                </div>
            </div>

            <div class="description-box">
                <strong>Passenger's Description</strong>
                <p>${escapeHTML(c.description || "No text description provided.")}</p>
            </div>

            <div class="evidence-section">
                <h3 style="font-size:16px; margin-bottom:10px;">📎 Evidence (${escapeHTML(c.evidence_type || "None")})</h3>
                ${evHtml}
            </div>

            <div style="margin-top:24px; padding-top:18px; border-top:1px solid #e2e8f0; display:flex; flex-wrap:wrap; gap:10px; align-items:center; justify-content:space-between;">
                <div style="display:flex; gap:8px; align-items:center;">
                    <label style="font-size:13px; font-weight:700;">Status:</label>
                    <select id="modalStatusSelect" style="padding:6px 10px; font-size:13px; border-radius:6px;" onchange="changeStatus(${c.id}, this.value)">
                        <option value="Pending" ${c.status === 'Pending' ? 'selected' : ''}>Pending</option>
                        <option value="In Progress" ${c.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                        <option value="Resolved" ${c.status === 'Resolved' ? 'selected' : ''}>Resolved</option>
                    </select>
                </div>

                <div style="display:flex; gap:8px; align-items:center;">
                    <label style="font-size:13px; font-weight:700;">Priority:</label>
                    <select id="modalPrioritySelect" style="padding:6px 10px; font-size:13px; border-radius:6px;" onchange="changePriority(${c.id}, this.value)">
                        <option value="Critical" ${c.priority === 'Critical' ? 'selected' : ''}>Critical</option>
                        <option value="High" ${c.priority === 'High' ? 'selected' : ''}>High</option>
                        <option value="Medium" ${c.priority === 'Medium' ? 'selected' : ''}>Medium</option>
                        <option value="Low" ${c.priority === 'Low' ? 'selected' : ''}>Low</option>
                    </select>
                </div>

                <div style="display:flex; gap:8px;">
                    <button class="button-accent" onclick="resolveComplaint(${c.id}); closeComplaintModal();">
                        ✅ Resolve Now
                    </button>
                    <button class="button-secondary" onclick="closeComplaintModal()">
                        Close
                    </button>
                </div>
            </div>
        `;
    } catch (err) {
        details.innerHTML = `<p style="color:#dc2626;">Failed to load complaint: ${escapeHTML(err.message)}</p>`;
    }
}

function closeComplaintModal() {
    const modal = document.getElementById("complaintModal");
    if (modal) modal.style.display = "none";
}

window.addEventListener("click", function (event) {
    const modal = document.getElementById("complaintModal");
    if (modal && event.target === modal) closeComplaintModal();
});

// =====================================================
// UPDATE STATUS, PRIORITY & RESOLVE
// =====================================================

async function changeStatus(complaintId, newStatus) {
    try {
        const formData = new FormData();
        formData.append("status", newStatus);

        const response = await fetch(`${API_URL}/complaints/${complaintId}/status`, {
            method: "PUT",
            headers: getAuthHeaders(),
            body: formData
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Status update failed");

        showToast(`Complaint #${complaintId} set to "${newStatus}"`, "success");
        await loadComplaints();
        await loadDashboard();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function changePriority(complaintId, newPriority) {
    try {
        const formData = new FormData();
        formData.append("priority", newPriority);

        const response = await fetch(`${API_URL}/complaints/${complaintId}/priority`, {
            method: "PUT",
            headers: getAuthHeaders(),
            body: formData
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Priority update failed");

        showToast(`Priority updated to "${newPriority}"`, "success");
        await loadComplaints();
        await loadDashboard();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function resolveComplaint(complaintId) {
    if (!confirm(`Are you sure you want to mark complaint #${complaintId} as RESOLVED?`)) return;

    try {
        const response = await fetch(`${API_URL}/complaints/${complaintId}/resolve`, {
            method: "PUT",
            headers: getAuthHeaders()
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Resolution failed");

        showToast(`Complaint #${complaintId} marked as Resolved!`, "success");
        await loadComplaints();
        await loadDashboard();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function deleteComplaint(complaintId) {
    if (!confirm(`Are you sure you want to permanently DELETE complaint #${complaintId}?`)) return;

    try {
        const response = await fetch(`${API_URL}/complaints/${complaintId}`, {
            method: "DELETE",
            headers: getAuthHeaders()
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Deletion failed");

        showToast(`Complaint #${complaintId} deleted`, "success");
        await loadComplaints();
        await loadDashboard();
    } catch (err) {
        showToast(err.message, "error");
    }
}

// =====================================================
// EXPORT TO CSV
// =====================================================

function exportComplaintsToCSV() {
    if (!allComplaints || allComplaints.length === 0) {
        showToast("No complaints available to export", "warning");
        return;
    }

    const headers = ["ID", "Passenger Name", "Phone", "PNR", "Train", "Coach", "Seat", "Category", "Priority", "Department", "Status", "Date"];
    const rows = allComplaints.map(c => [
        c.id,
        `"${(c.passenger_name || '').replace(/"/g, '""')}"`,
        `"${(c.phone_number || '').replace(/"/g, '""')}"`,
        `"${(c.pnr_number || '').replace(/"/g, '""')}"`,
        `"${(c.train_number || '').replace(/"/g, '""')}"`,
        `"${(c.coach_number || '').replace(/"/g, '""')}"`,
        `"${(c.seat_number || '').replace(/"/g, '""')}"`,
        `"${(c.complaint_category || '').replace(/"/g, '""')}"`,
        `"${(c.priority || '').replace(/"/g, '""')}"`,
        `"${(c.department || '').replace(/"/g, '""')}"`,
        `"${(c.status || '').replace(/"/g, '""')}"`,
        `"${c.created_at || ''}"`
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `RailMitra_Complaints_Report_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();

    showToast("CSV report generated and downloaded", "success");
}

// =====================================================
// UTILS
// =====================================================

function formatDate(val) {
    if (!val) return "-";
    try {
        const d = new Date(val);
        if (isNaN(d.getTime())) return String(val);
        return d.toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });
    } catch {
        return String(val);
    }
}

function escapeHTML(str) {
    if (str == null) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function escapeAttribute(str) {
    if (str == null) return "";
    return String(str)
        .replace(/\\/g, "\\\\")
        .replace(/'/g, "\\'")
        .replace(/"/g, "&quot;");
}

// Auto-refresh setup
let refreshInterval = null;
function toggleAutoRefresh(checkbox) {
    if (checkbox.checked) {
        refreshInterval = setInterval(() => {
            loadDashboard();
            loadComplaints();
        }, 30000);
        showToast("Auto-refresh enabled (30s interval)", "info");
    } else {
        if (refreshInterval) clearInterval(refreshInterval);
        showToast("Auto-refresh disabled", "info");
    }
}

// =====================================================
// INIT
// =====================================================

document.addEventListener("DOMContentLoaded", function () {
    if (document.getElementById("complaintTable")) {
        loadDashboard();
        loadComplaints();
    }
});