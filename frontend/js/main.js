/* ==========================================================================
   ASTRAL GLOBAL JAVASCRIPT - Main Utilities, Navigation & Header Dataset Switcher
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Highlight Active Nav Item
  const currentPath = window.location.pathname;
  const navItems = document.querySelectorAll(".portal-nav-links .nav-item, .sidebar-item");
  
  navItems.forEach(item => {
    const link = item.querySelector("a");
    if (link) {
      const href = link.getAttribute("href");
      if (currentPath === href || (href !== "/" && currentPath.includes(href))) {
        item.classList.add("active");
      } else {
        item.classList.remove("active");
      }
    }
  });

  // 2. Set Current Date Display
  const dateElement = document.getElementById("current-date-display");
  if (dateElement) {
    const today = new Date(2026, 7, 11);
    const dateStr = today.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    const dayStr = today.toLocaleDateString('en-US', { weekday: 'long' });
    dateElement.innerHTML = `<div>${dateStr}</div><div style="font-size: 0.75rem; color: #64748B; font-weight: 400; text-align: right;">${dayStr}</div>`;
  }

  // 3. User Profile Information Population
  const userStr = localStorage.getItem("astral_user") || localStorage.getItem("astra_user");
  if (userStr) {
    try {
      const user = JSON.parse(userStr);
      const nameElems = document.querySelectorAll(".user-name-target");
      nameElems.forEach(el => el.textContent = user.name || "Ritika Sharma");
      const roleElems = document.querySelectorAll(".user-role-target");
      roleElems.forEach(el => el.textContent = user.role || "Business Manager");
    } catch (e) {
      console.warn("User parse fallback");
    }
  }

  // 4. Logout Action
  const logoutBtns = document.querySelectorAll(".logout-trigger");
  logoutBtns.forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      localStorage.removeItem("astral_token");
      localStorage.removeItem("astral_user");
      localStorage.removeItem("astral_dataset_id");
      localStorage.removeItem("astra_token");
      localStorage.removeItem("astra_user");
      window.location.href = "/login";
    });
  });

  // 5. Inject Header Dataset Switcher Dropdown
  setupHeaderDatasetSwitcher();
});

// Helper API Fetcher with Dataset Header Injection
async function apiFetch(endpoint, options = {}) {
  const activeDatasetId = localStorage.getItem("astral_dataset_id") || "0";
  const userStr = localStorage.getItem("astral_user");
  let userId = "1";
  if (userStr) {
    try {
      const u = JSON.parse(userStr);
      if (u.id) userId = String(u.id);
    } catch (e) {}
  }

  const defaultHeaders = {
    "X-Dataset-ID": activeDatasetId,
    "X-User-ID": userId
  };

  options.headers = {
    ...defaultHeaders,
    ...(options.headers || {})
  };

  try {
    const response = await fetch(endpoint, options);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    return null;
  }
}

async function setupHeaderDatasetSwitcher() {
  const headerActions = document.querySelector(".header-right-actions");
  if (!headerActions || document.getElementById("header-dataset-switcher")) return;

  const currentDatasetId = localStorage.getItem("astral_dataset_id") || "0";

  let datasets = [];
  try {
    const res = await apiFetch("/api/datasets");
    if (res && res.datasets) {
      datasets = res.datasets;
    }
  } catch (err) {
    console.warn("Failed to fetch datasets list:", err);
  }

  if (datasets.length === 0) {
    datasets = [{ id: 0, name: "Zomato Business Intelligence", type: "demo" }];
  }

  const activeDataset = datasets.find(d => String(d.id) === String(currentDatasetId)) || datasets[0];

  const switcherHTML = `
    <div class="dataset-switcher-box" id="header-dataset-switcher">
      <button class="dataset-switcher-trigger" id="dataset-switcher-btn">
        <span class="ds-icon">${activeDataset.type === 'demo' ? '🌟' : '📁'}</span>
        <span class="ds-label" id="current-dataset-label">${activeDataset.name}</span>
        <span class="ds-arrow">▾</span>
      </button>

      <div class="dataset-dropdown-menu hidden" id="dataset-dropdown-menu" style="display: none;">
        <div class="dropdown-section-title">ACTIVE DATA SOURCE</div>
        ${datasets.map(ds => `
          <div class="dropdown-item ${String(ds.id) === String(currentDatasetId) ? 'active' : ''}" data-id="${ds.id}">
            <span class="item-icon">${ds.type === 'demo' ? '🌟' : '📁'}</span>
            <div class="item-meta">
              <div class="item-name">${ds.name}</div>
              <div class="item-sub">${ds.type === 'demo' ? 'Preloaded Zomato Demo' : `${ds.row_count} rows`}</div>
            </div>
            ${String(ds.id) === String(currentDatasetId) ? '<span class="item-check">✓</span>' : ''}
          </div>
        `).join('')}
        
        <div class="dropdown-divider"></div>
        <div class="dropdown-item btn-upload-item" id="btn-open-upload-modal">
          <span class="item-icon">➕</span>
          <div class="item-meta">
            <div class="item-name" style="color: var(--color-green-primary); font-weight: 600;">Upload New Dataset</div>
            <div class="item-sub">CSV or XLSX file</div>
          </div>
        </div>
      </div>
    </div>
  `;

  headerActions.insertAdjacentHTML("afterbegin", switcherHTML);

  const triggerBtn = document.getElementById("dataset-switcher-btn");
  const menu = document.getElementById("dataset-dropdown-menu");

  if (triggerBtn && menu) {
    triggerBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const isOpen = menu.classList.contains("show");
      if (isOpen) {
        menu.classList.remove("show");
        menu.classList.add("hidden");
        menu.style.display = "none";
      } else {
        menu.classList.add("show");
        menu.classList.remove("hidden");
        menu.style.display = "block";
      }
    });

    document.addEventListener("click", (e) => {
      const switcherBox = document.getElementById("header-dataset-switcher");
      if (switcherBox && !switcherBox.contains(e.target)) {
        menu.classList.remove("show");
        menu.classList.add("hidden");
        menu.style.display = "none";
      }
    });

    // Handle dataset items click
    menu.querySelectorAll(".dropdown-item[data-id]").forEach(item => {
      item.addEventListener("click", () => {
        const dsId = item.getAttribute("data-id");
        localStorage.setItem("astral_dataset_id", dsId);
        menu.style.display = "none";
        menu.classList.add("hidden");
        window.location.reload();
      });
    });

    // Handle Upload Dataset button click
    const uploadBtn = document.getElementById("btn-open-upload-modal");
    if (uploadBtn) {
      uploadBtn.addEventListener("click", () => {
        menu.style.display = "none";
        menu.classList.add("hidden");
        if (window.openUploadModal) {
          window.openUploadModal();
        }
      });
    }
  }
}
