/* ==========================================================================
   ASTRAL DATASET UPLOAD & SWITCHER JAVASCRIPT
   Handles multi-tenant CSV/XLSX file uploads, automatic profiling, & modal UI
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  createUploadModalMarkup();
  setupUploadModalEvents();
});

function createUploadModalMarkup() {
  if (document.getElementById("astral-upload-modal")) return;

  const modalHTML = `
    <div id="astral-upload-modal" class="astral-modal-backdrop hidden">
      <div class="astral-modal-card">
        
        <div class="astral-modal-header">
          <div style="display: flex; align-items: center; gap: 10px;">
            <div class="modal-header-icon">📁</div>
            <div>
              <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--color-navy-dark);">Upload Custom Dataset</h3>
              <p style="font-size: 0.825rem; color: var(--color-navy-muted);">Upload your CSV or Excel file to analyze with ASTRAL</p>
            </div>
          </div>
          <button class="modal-close-btn" id="close-upload-modal-btn">&times;</button>
        </div>

        <div class="astral-modal-body">
          
          <!-- State 1: Drop Zone -->
          <div id="upload-step-dropzone" class="upload-step-view">
            <div class="drop-zone-box" id="file-drop-zone">
              <div class="drop-zone-icon">☁️</div>
              <h4 style="font-size: 1rem; color: var(--color-navy-dark); margin-bottom: 4px;">Drag & Drop your dataset here</h4>
              <p style="font-size: 0.85rem; color: var(--color-navy-muted); margin-bottom: 14px;">Supports CSV, XLSX, and XLS formats (Max 50MB)</p>
              <label for="dataset-file-input" class="btn-browse-file">Browse Files</label>
              <input type="file" id="dataset-file-input" accept=".csv, .xlsx, .xls" style="display: none;">
            </div>

            <div id="upload-error-msg" class="upload-alert-box alert-danger hidden"></div>
          </div>

          <!-- State 2: Analyzing Dataset Progress -->
          <div id="upload-step-analyzing" class="upload-step-view hidden">
            <div class="analyzing-header">
              <div class="spinner-ring"></div>
              <div>
                <h4 style="font-size: 1rem; color: var(--color-navy-dark);">Analyzing Dataset...</h4>
                <p style="font-size: 0.85rem; color: var(--color-navy-muted);">ASTRAL engine is profiling data structures</p>
              </div>
            </div>

            <div class="analysis-checklist">
              <div class="check-item pending" id="chk-file-up"><span>✓</span> File uploaded</div>
              <div class="check-item pending" id="chk-ds-load"><span>✓</span> Dataset loaded</div>
              <div class="check-item pending" id="chk-rows-cols"><span>✓</span> Rows & columns detected</div>
              <div class="check-item pending" id="chk-types"><span>✓</span> Data types & missing values checked</div>
              <div class="check-item pending" id="chk-semantic"><span>✓</span> Semantic column mapping generated</div>
            </div>
          </div>

          <!-- State 3: Analysis Results Profile Overview -->
          <div id="upload-step-summary" class="upload-step-view hidden">
            <div class="summary-success-banner">
              <span>🎉</span>
              <div>
                <h4 style="font-size: 0.975rem; font-weight: 700; color: #065F46;">Dataset Profile Generated!</h4>
                <p style="font-size: 0.825rem; color: #047857;" id="summary-dataset-name">Client Sales 2026</p>
              </div>
            </div>

            <div class="profile-stats-grid">
              <div class="prof-stat-box">
                <div class="prof-stat-val" id="prof-rows-val">0</div>
                <div class="prof-stat-lbl">Total Rows</div>
              </div>
              <div class="prof-stat-box">
                <div class="prof-stat-val" id="prof-cols-val">0</div>
                <div class="prof-stat-lbl">Attributes</div>
              </div>
              <div class="prof-stat-box">
                <div class="prof-stat-val" id="prof-num-val">0</div>
                <div class="prof-stat-lbl">Numerical Cols</div>
              </div>
              <div class="prof-stat-box">
                <div class="prof-stat-val" id="prof-null-val">0%</div>
                <div class="prof-stat-lbl">Missing Values</div>
              </div>
            </div>

            <div class="semantic-mappings-card">
              <h5 style="font-size: 0.875rem; color: var(--color-navy-dark); margin-bottom: 8px;">Detected Column Mappings</h5>
              <div id="semantic-mappings-list" class="mappings-pill-list"></div>
            </div>
          </div>

        </div>

        <div class="astral-modal-footer">
          <button class="btn-secondary" id="modal-cancel-btn">Cancel</button>
          <button class="btn-primary hidden" id="modal-activate-btn">Set as Active Workspace</button>
        </div>

      </div>
    </div>
  `;

  document.body.insertAdjacentHTML("beforeend", modalHTML);
}

function setupUploadModalEvents() {
  const modal = document.getElementById("astral-upload-modal");
  const closeBtn = document.getElementById("close-upload-modal-btn");
  const cancelBtn = document.getElementById("modal-cancel-btn");
  const fileInput = document.getElementById("dataset-file-input");
  const dropZone = document.getElementById("file-drop-zone");

  if (closeBtn) closeBtn.addEventListener("click", hideUploadModal);
  if (cancelBtn) cancelBtn.addEventListener("click", hideUploadModal);

  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files[0]) {
        handleFileUpload(e.target.files[0]);
      }
    });
  }

  if (dropZone) {
    ["dragenter", "dragover"].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.add("drag-over");
      }, false);
    });

    ["dragleave", "drop"].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.remove("drag-over");
      }, false);
    });

    dropZone.addEventListener("drop", (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files && files[0]) {
        handleFileUpload(files[0]);
      }
    });
  }
}

function openUploadModal() {
  const modal = document.getElementById("astral-upload-modal");
  if (!modal) return;
  
  // Reset states
  document.getElementById("upload-step-dropzone").classList.remove("hidden");
  document.getElementById("upload-step-analyzing").classList.add("hidden");
  document.getElementById("upload-step-summary").classList.add("hidden");
  document.getElementById("modal-activate-btn").classList.add("hidden");
  
  const errBox = document.getElementById("upload-error-msg");
  if (errBox) errBox.classList.add("hidden");
  
  modal.style.display = "flex";
  modal.classList.remove("hidden");
}

function hideUploadModal() {
  const modal = document.getElementById("astral-upload-modal");
  if (modal) {
    modal.style.display = "none";
    modal.classList.add("hidden");
  }
}

async function handleFileUpload(file) {
  const dropzoneView = document.getElementById("upload-step-dropzone");
  const analyzingView = document.getElementById("upload-step-analyzing");
  const summaryView = document.getElementById("upload-step-summary");
  const errBox = document.getElementById("upload-error-msg");
  const activateBtn = document.getElementById("modal-activate-btn");

  if (errBox) errBox.classList.add("hidden");

  // Show analyzing screen
  dropzoneView.classList.add("hidden");
  analyzingView.classList.remove("hidden");

  // Checklist items
  const checkItems = ["chk-file-up", "chk-ds-load", "chk-rows-cols", "chk-types", "chk-semantic"];
  checkItems.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.className = "check-item pending";
    }
  });

  // Animated checklist simulation
  const advanceCheck = (index) => {
    if (index < checkItems.length) {
      const el = document.getElementById(checkItems[index]);
      if (el) el.className = "check-item done";
    }
  };

  advanceCheck(0);
  setTimeout(() => advanceCheck(1), 300);

  const formData = new FormData();
  formData.append("file", file);

  const userStr = localStorage.getItem("astral_user");
  let userId = "1";
  if (userStr) {
    try {
      const u = JSON.parse(userStr);
      if (u.id) userId = String(u.id);
    } catch (e) {}
  }

  try {
    const response = await fetch("/api/datasets/upload", {
      method: "POST",
      headers: {
        "X-User-ID": userId
      },
      body: formData
    });

    const data = await response.json();

    if (!response.ok || data.status !== "success") {
      analyzingView.classList.add("hidden");
      dropzoneView.classList.remove("hidden");
      if (errBox) {
        errBox.textContent = data.detail || "Failed to parse dataset file.";
        errBox.classList.remove("hidden");
      }
      return;
    }

    advanceCheck(2);
    setTimeout(() => advanceCheck(3), 300);
    setTimeout(() => advanceCheck(4), 500);

    setTimeout(() => {
      analyzingView.classList.add("hidden");
      summaryView.classList.remove("hidden");
      activateBtn.classList.remove("hidden");

      document.getElementById("summary-dataset-name").textContent = data.name;
      document.getElementById("prof-rows-val").textContent = data.row_count.toLocaleString();
      document.getElementById("prof-cols-val").textContent = data.col_count;
      document.getElementById("prof-num-val").textContent = data.profile.numeric_cols_count;
      document.getElementById("prof-null-val").textContent = `${data.profile.null_percentage}%`;

      const mappingsContainer = document.getElementById("semantic-mappings-list");
      if (mappingsContainer && data.profile.semantic_mappings) {
        const sm = data.profile.semantic_mappings;
        mappingsContainer.innerHTML = `
          <span class="mapping-tag">Entity: <b>${sm.entity_name_col || 'Not detected'}</b></span>
          <span class="mapping-tag">Category: <b>${sm.category_col || 'Not detected'}</b></span>
          <span class="mapping-tag">Metric/Price: <b>${sm.numeric_value_col || 'Not detected'}</b></span>
          <span class="mapping-tag">Quantity/Votes: <b>${sm.quantity_col || 'Not detected'}</b></span>
        `;
      }

      activateBtn.onclick = () => {
        localStorage.setItem("astral_dataset_id", String(data.dataset_id));
        hideUploadModal();
        window.location.reload();
      };
    }, 700);

  } catch (err) {
    console.error("Upload error:", err);
    analyzingView.classList.add("hidden");
    dropzoneView.classList.remove("hidden");
    if (errBox) {
      errBox.textContent = "Server error uploading file. Please verify connection.";
      errBox.classList.remove("hidden");
    }
  }
}

window.openUploadModal = openUploadModal;
window.hideUploadModal = hideUploadModal;
