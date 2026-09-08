const API_URL = "http://127.0.0.1:8000";


// =====================================================
// GET ADMIN TOKEN
// =====================================================

function getAdminToken() {

    return localStorage.getItem("adminToken");

}


// =====================================================
// CREATE AUTHORIZATION HEADER
// =====================================================

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


// =====================================================
// ADMIN LOGOUT
// =====================================================

function logout() {

    localStorage.removeItem("adminToken");
    localStorage.removeItem("adminRole");
    localStorage.removeItem("adminUsername");

    sessionStorage.removeItem("adminLoggedIn");

    window.location.href = "login.html";

}


// =====================================================
// STORE ALL COMPLAINTS
// =====================================================

let allComplaints = [];


// =====================================================
// CONVERT DATABASE EVIDENCE PATH TO BROWSER URL
// =====================================================

function getEvidenceURL(evidencePath) {

    if (!evidencePath) {
        return null;
    }

    const normalizedPath =
        String(evidencePath).replace(/\\/g, "/");

    const uploadsIndex =
        normalizedPath
            .toLowerCase()
            .indexOf("/uploads/");

    if (uploadsIndex === -1) {
        return null;
    }

    const relativePath =
        normalizedPath.substring(
            uploadsIndex + 1
        );

    const encodedPath =
        relativePath
            .split("/")
            .map(
                part => encodeURIComponent(part)
            )
            .join("/");

    return `${API_URL}/${encodedPath}`;
}


// =====================================================
// LOAD DASHBOARD SUMMARY
// =====================================================

async function loadDashboard() {

    try {

        const response =
            await fetch(
                `${API_URL}/complaints/dashboard/summary`,
                {
                    method: "GET",
                    headers: getAuthHeaders()
                }
            );


        if (!response.ok) {

            const errorText =
                await response.text();

            if (
                response.status === 401 ||
                response.status === 403
            ) {

                throw new Error(
                    "Admin authentication failed. Please login again."
                );

            }

            throw new Error(
                `Dashboard API failed: ${response.status} ${errorText}`
            );
        }


        const data =
            await response.json();


        console.log(
            "Dashboard response:",
            data
        );


        document.getElementById(
            "totalComplaints"
        ).textContent =
            data.total_complaints ?? 0;


        document.getElementById(
            "pendingComplaints"
        ).textContent =
            data.pending ?? 0;


        document.getElementById(
            "inProgressComplaints"
        ).textContent =
            data.in_progress ?? 0;


        document.getElementById(
            "resolvedComplaints"
        ).textContent =
            data.resolved ?? 0;


        document.getElementById(
            "criticalComplaints"
        ).textContent =
            data.critical ?? 0;


        document.getElementById(
            "highComplaints"
        ).textContent =
            data.high_priority ?? 0;


        loadDepartments(
            data.department_wise || {}
        );

    }


    catch (error) {

        console.error(
            "Dashboard error:",
            error
        );


        const departmentContainer =
            document.getElementById(
                "departments"
            );


        if (departmentContainer) {

            departmentContainer.textContent =
                "Failed to load dashboard data.";

        }

    }

}


// =====================================================
// LOAD DEPARTMENT-WISE COMPLAINTS
// =====================================================

function loadDepartments(departments) {

    const container =
        document.getElementById(
            "departments"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    const departmentNames =
        Object.keys(departments);


    if (departmentNames.length === 0) {

        container.innerHTML =
            "<p>No department data available.</p>";

        return;
    }


    departmentNames.forEach(
        department => {

            const div =
                document.createElement(
                    "div"
                );


            div.className =
                "department-item";


            div.innerHTML = `
                <strong>
                    ${escapeHTML(department)}
                </strong>
                :
                ${departments[department]}
                complaints
            `;


            container.appendChild(
                div
            );

        }
    );

}


// =====================================================
// LOAD ALL COMPLAINTS
// =====================================================

async function loadComplaints() {

    const tableBody =
        document.getElementById(
            "complaintTable"
        );


    if (!tableBody) {

        console.error(
            "complaintTable element not found"
        );

        return;
    }


    tableBody.innerHTML = `
        <tr>
            <td colspan="8">
                Loading complaints...
            </td>
        </tr>
    `;


    try {

        const response =
            await fetch(
                `${API_URL}/complaints/`,
                {
                    method: "GET",
                    headers: getAuthHeaders()
                }
            );


        if (!response.ok) {

            const errorText =
                await response.text();


            if (
                response.status === 401 ||
                response.status === 403
            ) {

                throw new Error(
                    "Admin authentication failed. Please login again."
                );

            }


            throw new Error(
                `Complaints API failed: ${response.status} ${errorText}`
            );
        }


        const data =
            await response.json();


        console.log(
            "Complaints API response:",
            data
        );


        allComplaints =
            data.complaints || [];


        displayComplaints(
            allComplaints
        );

    }


    catch (error) {

        console.error(
            "Error loading complaints:",
            error
        );


        tableBody.innerHTML = `
            <tr>
                <td colspan="8">
                    Failed to load complaints.
                    <br>
                    <small>
                        ${escapeHTML(
                            error.message
                        )}
                    </small>
                </td>
            </tr>
        `;

    }

}


// =====================================================
// APPLY SEARCH AND FILTERS
// =====================================================

function applyFilters() {

    const searchInput =
        document.getElementById(
            "searchComplaint"
        );


    const statusFilter =
        document.getElementById(
            "statusFilter"
        );


    const priorityFilter =
        document.getElementById(
            "priorityFilter"
        );


    const categoryFilter =
        document.getElementById(
            "categoryFilter"
        );


    const departmentFilter =
        document.getElementById(
            "departmentFilter"
        );


    const searchText =
        searchInput
            ? searchInput.value
                .trim()
                .toLowerCase()
            : "";


    const selectedStatus =
        statusFilter
            ? statusFilter.value
            : "";


    const selectedPriority =
        priorityFilter
            ? priorityFilter.value
            : "";


    const selectedCategory =
        categoryFilter
            ? categoryFilter.value
            : "";


    const selectedDepartment =
        departmentFilter
            ? departmentFilter.value
            : "";


    const filteredComplaints =
        allComplaints.filter(
            complaint => {

                const passengerName =
                    String(
                        complaint.passenger_name || ""
                    ).toLowerCase();


                const trainNumber =
                    String(
                        complaint.train_number || ""
                    ).toLowerCase();


                const pnrNumber =
                    String(
                        complaint.pnr_number || ""
                    ).toLowerCase();


                const description =
                    String(
                        complaint.description || ""
                    ).toLowerCase();


                const matchesSearch =
                    searchText === "" ||
                    passengerName.includes(
                        searchText
                    ) ||
                    trainNumber.includes(
                        searchText
                    ) ||
                    pnrNumber.includes(
                        searchText
                    ) ||
                    description.includes(
                        searchText
                    );


                const matchesStatus =
                    selectedStatus === "" ||
                    complaint.status === selectedStatus;


                const matchesPriority =
                    selectedPriority === "" ||
                    complaint.priority === selectedPriority;


                const matchesCategory =
                    selectedCategory === "" ||
                    complaint.complaint_category === selectedCategory;


                const matchesDepartment =
                    selectedDepartment === "" ||
                    complaint.department === selectedDepartment;


                return (
                    matchesSearch &&
                    matchesStatus &&
                    matchesPriority &&
                    matchesCategory &&
                    matchesDepartment
                );

            }
        );


    console.log(
        "Filtered complaints:",
        filteredComplaints
    );


    displayComplaints(
        filteredComplaints
    );

}


// =====================================================
// CLEAR ALL FILTERS
// =====================================================

function clearFilters() {

    const searchInput =
        document.getElementById(
            "searchComplaint"
        );


    const statusFilter =
        document.getElementById(
            "statusFilter"
        );


    const priorityFilter =
        document.getElementById(
            "priorityFilter"
        );


    const categoryFilter =
        document.getElementById(
            "categoryFilter"
        );


    const departmentFilter =
        document.getElementById(
            "departmentFilter"
        );


    if (searchInput) {
        searchInput.value = "";
    }


    if (statusFilter) {
        statusFilter.value = "";
    }


    if (priorityFilter) {
        priorityFilter.value = "";
    }


    if (categoryFilter) {
        categoryFilter.value = "";
    }


    if (departmentFilter) {
        departmentFilter.value = "";
    }


    displayComplaints(
        allComplaints
    );

}


// =====================================================
// GET EVIDENCE BUTTON TEXT
// =====================================================

function getEvidenceButtonText(evidenceType) {

    const type =
        String(
            evidenceType || ""
        ).toLowerCase();


    if (
        type === "image" ||
        type === "images"
    ) {

        return "View Image";

    }


    if (
        type === "video" ||
        type === "videos"
    ) {

        return "View Video";

    }


    if (type === "audio") {

        return "Play Audio";

    }


    return "View Evidence";

}


// =====================================================
// DISPLAY COMPLAINTS IN TABLE
// =====================================================

function displayComplaints(
    complaints
) {

    const tableBody =
        document.getElementById(
            "complaintTable"
        );


    if (!tableBody) {
        return;
    }


    tableBody.innerHTML = "";


    if (
        !complaints ||
        complaints.length === 0
    ) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="8">
                    No complaints found.
                </td>
            </tr>
        `;

        return;
    }


    complaints.forEach(
        complaint => {

            const row =
                document.createElement(
                    "tr"
                );


            let evidenceButton = "";


            const evidenceURL =
                getEvidenceURL(
                    complaint.evidence_path
                );


            if (evidenceURL) {

                const buttonText =
                    getEvidenceButtonText(
                        complaint.evidence_type
                    );


                evidenceButton = `
                    <button
                        onclick="viewEvidence(
                            '${escapeAttribute(
                                evidenceURL
                            )}',
                            '${escapeAttribute(
                                complaint.evidence_type || ""
                            )}'
                        )"
                    >
                        ${buttonText}
                    </button>
                `;

            }


            else {

                evidenceButton = `
                    <span>
                        No Evidence
                    </span>
                `;

            }


            row.innerHTML = `

                <td>
                    ${complaint.id ?? "-"}
                </td>

                <td>
                    ${escapeHTML(
                        complaint.passenger_name || "-"
                    )}
                </td>

                <td>
                    ${escapeHTML(
                        complaint.train_number || "-"
                    )}
                </td>

                <td>
                    ${escapeHTML(
                        complaint.complaint_category || "-"
                    )}
                </td>

                <td>
                    <span class="priority">
                        ${escapeHTML(
                            complaint.priority || "-"
                        )}
                    </span>
                </td>

                <td>
                    ${escapeHTML(
                        complaint.department || "-"
                    )}
                </td>

                <td>
                    <span class="status-badge">
                        ${escapeHTML(
                            complaint.status || "-"
                        )}
                    </span>
                </td>

                <td>

                    <button
                        onclick="viewComplaint(
                            ${complaint.id}
                        )"
                    >
                        View
                    </button>

                    ${evidenceButton}

                    <button
                        onclick="changeStatus(
                            ${complaint.id},
                            'Pending'
                        )"
                    >
                        Pending
                    </button>

                    <button
                        onclick="changeStatus(
                            ${complaint.id},
                            'In Progress'
                        )"
                    >
                        In Progress
                    </button>

                    <button
                        onclick="resolveComplaint(
                            ${complaint.id}
                        )"
                    >
                        Resolve
                    </button>

                </td>

            `;


            tableBody.appendChild(
                row
            );

        }
    );

}


// =====================================================
// VIEW EVIDENCE
// =====================================================

function viewEvidence(
    evidenceURL,
    evidenceType
) {

    if (!evidenceURL) {

        alert(
            "Evidence is not available."
        );

        return;
    }


    console.log(
        "Opening evidence:",
        evidenceURL,
        "Type:",
        evidenceType
    );


    window.open(
        evidenceURL,
        "_blank"
    );

}


// =====================================================
// CREATE EVIDENCE HTML FOR MODAL
// =====================================================

function createEvidenceHTML(
    evidenceURL,
    evidenceType
) {

    if (!evidenceURL) {

        return `
            <p>
                No evidence available.
            </p>
        `;

    }


    const type =
        String(
            evidenceType || ""
        ).toLowerCase();


    // -------------------------------------------------
    // IMAGE
    // -------------------------------------------------

    if (
        type === "image" ||
        type === "images"
    ) {

        return `
            <img
                src="${escapeAttribute(
                    evidenceURL
                )}"
                alt="Complaint Evidence"
                class="evidence-image"
                onerror="this.style.display='none'; document.getElementById('imageError').style.display='block';"
            >

            <p
                id="imageError"
                style="display:none;"
            >
                Evidence image could not be loaded.
            </p>
        `;

    }


    // -------------------------------------------------
    // VIDEO
    // -------------------------------------------------

    if (
        type === "video" ||
        type === "videos"
    ) {

        return `
            <video
                controls
                class="evidence-video"
                style="
                    width:100%;
                    max-width:700px;
                    border-radius:10px;
                    display:block;
                    margin-top:10px;
                "
            >
                <source
                    src="${escapeAttribute(
                        evidenceURL
                    )}"
                >

                Your browser does not support
                video playback.
            </video>

            <p>
                <a
                    href="${escapeAttribute(
                        evidenceURL
                    )}"
                    target="_blank"
                >
                    Open video in new tab
                </a>
            </p>
        `;

    }


    // -------------------------------------------------
    // AUDIO
    // -------------------------------------------------

    if (type === "audio") {

        return `
            <audio
                controls
                style="
                    width:100%;
                    max-width:700px;
                    margin-top:10px;
                "
            >
                <source
                    src="${escapeAttribute(
                        evidenceURL
                    )}"
                >

                Your browser does not support
                audio playback.
            </audio>

            <p>
                <a
                    href="${escapeAttribute(
                        evidenceURL
                    )}"
                    target="_blank"
                >
                    Open audio in new tab
                </a>
            </p>
        `;

    }


    // -------------------------------------------------
    // UNKNOWN EVIDENCE TYPE
    // -------------------------------------------------

    return `
        <p>
            Evidence type:
            ${escapeHTML(
                evidenceType || "Unknown"
            )}
        </p>

        <p>
            <a
                href="${escapeAttribute(
                    evidenceURL
                )}"
                target="_blank"
            >
                Open Evidence
            </a>
        </p>
    `;

}


// =====================================================
// VIEW SINGLE COMPLAINT
// =====================================================

async function viewComplaint(
    complaintId
) {

    const modal =
        document.getElementById(
            "complaintModal"
        );


    const details =
        document.getElementById(
            "complaintDetails"
        );


    if (!modal || !details) {

        console.error(
            "Complaint modal elements not found."
        );

        return;
    }


    modal.style.display = "block";


    details.innerHTML = `
        <p>
            Loading complaint details...
        </p>
    `;


    try {

        const response =
            await fetch(
                `${API_URL}/complaints/${complaintId}`,
                {
                    method: "GET",
                    headers: getAuthHeaders()
                }
            );


        if (!response.ok) {

            const errorData =
                await response.json()
                    .catch(
                        () => ({})
                    );


            throw new Error(
                errorData.detail ||
                `Complaint API failed: ${response.status}`
            );

        }


        const complaint =
            await response.json();


        console.log(
            "Complaint details:",
            complaint
        );


        const evidenceURL =
            getEvidenceURL(
                complaint.evidence_path
            );


        const evidenceHTML =
            createEvidenceHTML(
                evidenceURL,
                complaint.evidence_type
            );


        let aiConfidence = "-";


        if (
            complaint.ai_confidence !== null &&
            complaint.ai_confidence !== undefined
        ) {

            aiConfidence =
                (
                    Number(
                        complaint.ai_confidence
                    ) * 100
                ).toFixed(1) + "%";

        }


        details.innerHTML = `

            <div class="complaint-details">

                <div class="detail-box">
                    <strong>Complaint ID</strong>
                    <span>
                        #${complaint.id ?? "-"}
                    </span>
                </div>


                <div class="detail-box">
                    <strong>Status</strong>
                    <span>
                        ${escapeHTML(
                            complaint.status || "-"
                        )}
                    </span>
                </div>


                <div class="detail-box">
                    <strong>Passenger Name</strong>
                    <span>
                        ${escapeHTML(
                            complaint.passenger_name || "-"
                        )}
                    </span>
                </div>


                <div class="detail-box">
                    <strong>Phone Number</strong>
                    <span>
                        ${escapeHTML(
                            complaint.phone_number || "-"
                        )}
                    </span>
                </div>


                <div class="detail-box">
                    <strong>PNR Number</strong>
                    <span>
                        ${escapeHTML(
                            complaint.pnr_number || "-"
                        )}
                    </span>
                </div>


                <div class="detail-box">
                    <strong>Train Number</strong>
                    <span>
                        ${escapeHTML(
                            complaint.train_number || "-"
                        )}
                    </span>
                </div>


                <div class="detail-box">
                    <strong>Coach Number</strong>
                    <span>
                        ${escapeHTML(
                            complaint.coach_number || "-"
                        )}
                    </span>
                </div>


                <div class="detail-box">
                    <strong>Seat Number</strong>
                    <span>
                        ${escapeHTML(
                            complaint.seat_number || "-"
                        )}
                    </span>
                </div>


                <div class="detail-box">
                    <strong>Category</strong>
                    <span>
                        ${escapeHTML(
                            complaint.complaint_category || "-"
                        )}
                    </span>
                </div>


                <div class="detail-box">
                    <strong>AI Category</strong>
                    <span>
                        ${escapeHTML(
                            complaint.ai_category || "-"
                        )}
                    </span>
                </div>


                <div class="detail-box">
                    <strong>AI Confidence</strong>
                    <span>
                        ${aiConfidence}
                    </span>
                </div>


                <div class="detail-box">
                    <strong>Priority</strong>
                    <span>
                        ${escapeHTML(
                            complaint.priority || "-"
                        )}
                    </span>
                </div>


                <div class="detail-box">
                    <strong>Department</strong>
                    <span>
                        ${escapeHTML(
                            complaint.department || "-"
                        )}
                    </span>
                </div>


                <div class="detail-box">
                    <strong>Location</strong>
                    <span>
                        ${escapeHTML(
                            complaint.location || "-"
                        )}
                    </span>
                </div>


                <div class="detail-box">
                    <strong>Evidence Type</strong>
                    <span>
                        ${escapeHTML(
                            complaint.evidence_type || "-"
                        )}
                    </span>
                </div>


                <div class="detail-box">
                    <strong>Created At</strong>
                    <span>
                        ${formatDate(
                            complaint.created_at
                        )}
                    </span>
                </div>


                <div class="detail-box">
                    <strong>Resolved At</strong>
                    <span>
                        ${formatDate(
                            complaint.resolved_at
                        )}
                    </span>
                </div>

            </div>


            <div class="description-box">

                <strong>
                    Complaint Description
                </strong>

                <p>
                    ${escapeHTML(
                        complaint.description || "-"
                    )}
                </p>

            </div>


            <div class="evidence-section">

                <h3>
                    Evidence
                </h3>

                ${evidenceHTML}

            </div>


            <div class="modal-actions">

                <button
                    onclick="changeStatus(
                        ${complaint.id},
                        'Pending'
                    ); closeComplaintModal();"
                >
                    Pending
                </button>


                <button
                    onclick="changeStatus(
                        ${complaint.id},
                        'In Progress'
                    ); closeComplaintModal();"
                >
                    In Progress
                </button>


                <button
                    onclick="resolveComplaint(
                        ${complaint.id}
                    ); closeComplaintModal();"
                >
                    Resolve
                </button>

            </div>

        `;

    }


    catch (error) {

        console.error(
            "View complaint error:",
            error
        );


        details.innerHTML = `
            <p>
                Could not load complaint details.
            </p>

            <p>
                ${escapeHTML(
                    error.message
                )}
            </p>
        `;

    }

}


// =====================================================
// CLOSE COMPLAINT MODAL
// =====================================================

function closeComplaintModal() {

    const modal =
        document.getElementById(
            "complaintModal"
        );


    if (modal) {

        modal.style.display =
            "none";

    }

}


// =====================================================
// CLOSE MODAL WHEN CLICKING OUTSIDE
// =====================================================

window.addEventListener(
    "click",
    function (event) {

        const modal =
            document.getElementById(
                "complaintModal"
            );


        if (
            modal &&
            event.target === modal
        ) {

            closeComplaintModal();

        }

    }
);


// =====================================================
// CHANGE COMPLAINT STATUS
// =====================================================

async function changeStatus(
    complaintId,
    newStatus
) {

    try {

        const formData =
            new FormData();


        formData.append(
            "status",
            newStatus
        );


        const response =
            await fetch(
                `${API_URL}/complaints/${complaintId}/status`,
                {
                    method: "PUT",
                    headers: getAuthHeaders(),
                    body: formData
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Status update failed"
            );

        }


        alert(
            `Complaint #${complaintId} updated to ${newStatus}`
        );


        await loadComplaints();

        await loadDashboard();

    }


    catch (error) {

        console.error(
            "Status update error:",
            error
        );


        alert(
            "Could not update complaint status:\n" +
            error.message
        );

    }

}


// =====================================================
// RESOLVE COMPLAINT
// =====================================================

async function resolveComplaint(
    complaintId
) {

    try {

        const confirmed =
            confirm(
                `Are you sure you want to resolve complaint #${complaintId}?`
            );


        if (!confirmed) {
            return;
        }


        const response =
            await fetch(
                `${API_URL}/complaints/${complaintId}/resolve`,
                {
                    method: "PUT",
                    headers: getAuthHeaders()
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Resolve operation failed"
            );

        }


        alert(
            `Complaint #${complaintId} resolved successfully`
        );


        await loadComplaints();

        await loadDashboard();

    }


    catch (error) {

        console.error(
            "Resolve error:",
            error
        );


        alert(
            "Could not resolve complaint:\n" +
            error.message
        );

    }

}


// =====================================================
// FORMAT DATE
// =====================================================

function formatDate(
    dateValue
) {

    if (!dateValue) {
        return "-";
    }


    try {

        const date =
            new Date(
                dateValue
            );


        if (
            Number.isNaN(
                date.getTime()
            )
        ) {

            return escapeHTML(
                dateValue
            );

        }


        return date.toLocaleString();

    }


    catch (error) {

        return escapeHTML(
            dateValue
        );

    }

}


// =====================================================
// HTML ESCAPE FUNCTION
// =====================================================

function escapeHTML(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


// =====================================================
// ATTRIBUTE ESCAPE FUNCTION
// =====================================================

function escapeAttribute(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)

        .replace(
            /\\/g,
            "\\\\"
        )

        .replace(
            /'/g,
            "\\'"
        )

        .replace(
            /"/g,
            "&quot;"
        );

}


// =====================================================
// INITIAL PAGE LOAD
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "RailMitra AI frontend started"
        );


        loadDashboard();

        loadComplaints();

    }
);