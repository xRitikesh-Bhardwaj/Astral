/* ==========================================================================
   ASTRAL DASHBOARD JAVASCRIPT - Business Overview Data & Chart.js Rendering
   ========================================================================== */

let revenueChartInstance = null;

document.addEventListener("DOMContentLoaded", async () => {
  await loadDashboardData();
  setupFilterTabs();
});

async function loadDashboardData() {
  const data = await apiFetch("/api/dashboard");
  if (!data) return;

  // 1. Populate Business Health Card
  const healthScoreEl = document.getElementById("health-score-val");
  const healthStatusEl = document.getElementById("health-status-val");
  if (healthScoreEl) healthScoreEl.textContent = `${data.business_health.score} / 100`;
  if (healthStatusEl) healthStatusEl.textContent = data.business_health.status;

  // 2. Populate KPI Cards
  if (data.kpis) {
    const setText = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };

    if (data.kpis.revenue) {
      setText("kpi-revenue-val", data.kpis.revenue.value);
      setText("kpi-revenue-change", `↑ ${data.kpis.revenue.change} vs last period`);
    }
    if (data.kpis.orders) {
      setText("kpi-orders-val", data.kpis.orders.value);
      setText("kpi-orders-change", `↑ ${data.kpis.orders.change} vs last period`);
    }
    if (data.kpis.customers) {
      setText("kpi-customers-val", data.kpis.customers.value);
      setText("kpi-customers-change", `↑ ${data.kpis.customers.change} vs last period`);
    }
    if (data.kpis.profit) {
      setText("kpi-profit-val", data.kpis.profit.value);
      setText("kpi-profit-change", `↑ ${data.kpis.profit.change} vs last period`);
    }
  }

  // 3. Render Revenue Trend Chart with Chart.js
  if (data.chart_data && document.getElementById("revenueTrendChart")) {
    renderRevenueChart(data.chart_data.labels, data.chart_data.values);
  }

  // 3b. Render Category Doughnut Chart if present
  if (document.getElementById("categoryDoughnutChart")) {
    renderCategoryDoughnutChart();
  }

  // 4. Daily AI Summary
  const summaryEl = document.getElementById("today-summary-text");
  if (summaryEl) summaryEl.textContent = data.daily_summary;

  // 5. Key Insights List
  const insightsListEl = document.getElementById("insights-list-container");
  if (insightsListEl && data.key_insights) {
    insightsListEl.innerHTML = data.key_insights.map(item => `
      <div class="insight-item">
        <span class="badge ${item.type === 'positive' ? 'badge-green' : item.type === 'warning' ? 'badge-amber' : 'badge-blue'}">Insight</span>
        <span style="color: var(--color-navy-dark); font-weight: 500;">${item.text}</span>
      </div>
    `).join("");
  }

  // 6. Attention Required Items
  const attentionContainer = document.getElementById("attention-items-container");
  if (attentionContainer && data.attention_required) {
    attentionContainer.innerHTML = data.attention_required.map(item => {
      const severityClass = item.severity === 'High' ? 'attention-high' : item.severity === 'Medium' ? 'attention-medium' : 'attention-positive';
      const badgeClass = item.severity === 'High' ? 'badge-red' : item.severity === 'Medium' ? 'badge-amber' : 'badge-green';
      return `
        <div class="attention-card ${severityClass}">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <h4 style="font-size: 0.95rem;">${item.title}</h4>
            <span class="badge ${badgeClass}">${item.badge}</span>
          </div>
          <p style="font-size: 0.85rem; color: var(--color-navy-muted);">${item.desc}</p>
        </div>
      `;
    }).join("");
  }
}

function renderRevenueChart(labels, values) {
  const ctx = document.getElementById("revenueTrendChart").getContext("2d");
  if (revenueChartInstance) revenueChartInstance.destroy();

  const cyanGradient = ctx.createLinearGradient(0, 0, 0, 300);
  cyanGradient.addColorStop(0, "rgba(0, 229, 255, 0.25)");
  cyanGradient.addColorStop(1, "rgba(0, 229, 255, 0.0)");

  // Forecast line projected slightly above/parallel to actual line
  const forecastValues = values.map((v, i) => Math.round(v * (1 + (i * 0.02 + 0.05))));

  revenueChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Actual Revenue",
          data: values,
          borderColor: "#00E5FF",
          borderWidth: 3,
          backgroundColor: cyanGradient,
          fill: true,
          tension: 0.35,
          pointBackgroundColor: "#00E5FF",
          pointBorderColor: "#0B0E14",
          pointBorderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 7
        },
        {
          label: "AI Forecast",
          data: forecastValues,
          borderColor: "#A855F7",
          borderWidth: 2.5,
          borderDash: [6, 4],
          backgroundColor: "transparent",
          fill: false,
          tension: 0.35,
          pointBackgroundColor: "#A855F7",
          pointBorderColor: "#0B0E14",
          pointBorderWidth: 2,
          pointRadius: 3.5,
          pointHoverRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#111827",
          borderColor: "rgba(255,255,255,0.1)",
          borderWidth: 1,
          padding: 12,
          titleFont: { family: "Inter", size: 13 },
          bodyFont: { family: "Inter", size: 12 },
          displayColors: true,
          callbacks: {
            label: (context) => `${context.dataset.label}: ₹${context.raw} Lakhs`
          }
        }
      },
      scales: {
        x: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: { font: { family: "Inter", size: 11 }, color: "#94A3B8" }
        },
        y: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: { font: { family: "Inter", size: 11 }, color: "#94A3B8" }
        }
      }
    }
  });
}

function setupFilterTabs() {
  const tabBtns = document.querySelectorAll(".timeframe-tab");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      // Simulate data slice based on tab
      loadDashboardData();
    });
  });
}

function renderCategoryDoughnutChart() {
  const canvas = document.getElementById("categoryDoughnutChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Electronics & Software", "Home & Living", "Fashion & Apparel", "Beauty & Personal Care", "Others"],
      datasets: [{
        data: [42, 18, 15, 13, 12],
        backgroundColor: ["#10B981", "#00E5FF", "#3B82F6", "#8B5CF6", "#F59E0B"],
        borderWidth: 0,
        hoverOffset: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "75%",
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#111827",
          borderColor: "rgba(255,255,255,0.1)",
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label: (context) => `${context.label}: ${context.raw}%`
          }
        }
      }
    }
  });
}

