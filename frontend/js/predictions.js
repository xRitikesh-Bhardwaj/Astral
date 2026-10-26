/* ==========================================================================
   ASTRAL PREDICTIONS JAVASCRIPT - Dataset-Aware Machine Learning Visualizations
   ========================================================================== */

document.addEventListener("DOMContentLoaded", async () => {
  // 1. Fetch Revenue Predictions
  const revData = await apiFetch("/api/predictions/revenue");
  if (revData) {
    if (revData.supported === false) {
      showUnsupportedNotice("forecast-card-container", revData.reason);
    } else if (revData.forecast && document.getElementById("forecastChart")) {
      renderForecastChart(revData.history, revData.forecast);
      const targetEl = document.getElementById("forecast-7d-target");
      if (targetEl) {
        const totalVal = revData.next_7_days_total;
        targetEl.textContent = totalVal > 10000000 ? `₹${(totalVal / 10000000).toFixed(2)} Cr` : `₹${(totalVal / 100000).toFixed(1)} Lakhs`;
      }
    }
  }

  // 2. Fetch Customer / Outlet Risk Predictions
  const churnData = await apiFetch("/api/predictions/churn");
  if (churnData) {
    if (churnData.supported === false) {
      showUnsupportedNotice("churn-section-container", churnData.reason);
    } else if (churnData.customers) {
      const highEl = document.getElementById("high-risk-count");
      const medEl = document.getElementById("med-risk-count");
      const lowEl = document.getElementById("low-risk-count");
      if (highEl) highEl.textContent = churnData.high_risk_count;
      if (medEl) medEl.textContent = churnData.medium_risk_count;
      if (lowEl) lowEl.textContent = churnData.low_risk_count;

      const churnTableBody = document.getElementById("churn-table-body");
      if (churnTableBody) {
        churnTableBody.innerHTML = churnData.customers.map(c => `
          <tr>
            <td style="font-weight: 600;">${c.name}</td>
            <td>${c.company}</td>
            <td>₹${(c.total_spent / 100000).toFixed(1)}L</td>
            <td>${c.last_order_days_ago} days ago</td>
            <td>
              <span class="badge ${c.risk_level === 'High Risk' ? 'badge-red' : c.risk_level === 'Medium Risk' ? 'badge-amber' : 'badge-green'}">
                ${c.churn_probability}% (${c.risk_level})
              </span>
            </td>
            <td style="font-size: 0.825rem; color: var(--color-navy-muted);">${c.recommended_action}</td>
          </tr>
        `).join("");
      }
    }
  }

  // 3. Fetch Anomaly Detection Data
  const anomalyData = await apiFetch("/api/anomalies");
  if (anomalyData) {
    if (anomalyData.supported === false) {
      showUnsupportedNotice("anomaly-cards-container", anomalyData.reason);
    } else if (anomalyData.anomalies) {
      const anomalyContainer = document.getElementById("anomaly-cards-container");
      if (anomalyContainer) {
        anomalyContainer.innerHTML = anomalyData.anomalies.map(a => `
          <div class="attention-card ${a.severity === 'High' ? 'attention-high' : a.severity === 'Positive' ? 'attention-positive' : 'attention-medium'}">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <h4 style="font-size: 0.925rem;">${a.issue}</h4>
              <span class="badge ${a.severity === 'High' ? 'badge-red' : a.severity === 'Positive' ? 'badge-green' : 'badge-amber'}">${a.date}</span>
            </div>
            <p style="font-size: 0.85rem;">${a.impact}</p>
          </div>
        `).join("");
      }
    }
  }
});

function showUnsupportedNotice(containerId, reason) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = `
    <div style="padding: 24px; background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 12px; text-align: center;">
      <div style="font-size: 1.5rem; margin-bottom: 6px;">ℹ️</div>
      <h4 style="font-size: 0.95rem; color: #F59E0B; margin-bottom: 4px;">Analysis Unavailable for Selected Dataset</h4>
      <p style="font-size: 0.85rem; color: #94A3B8;">${reason}</p>
    </div>
  `;
}

function renderForecastChart(history, forecast) {
  const canvas = document.getElementById("forecastChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  
  const histLabels = history.map(h => h.date);
  const histValues = history.map(h => (h.actual_revenue / 100000).toFixed(2));
  
  const foreLabels = forecast.map(f => f.date);
  const foreValues = forecast.map(f => (f.predicted_revenue / 100000).toFixed(2));
  
  const allLabels = [...histLabels, ...foreLabels];
  const historicalDataset = [...histValues, ...Array(forecast.length).fill(null)];
  
  const lastHistVal = histValues[histValues.length - 1];
  const predictedDataset = [...Array(histValues.length - 1).fill(null), lastHistVal, ...foreValues];

  new Chart(ctx, {
    type: "line",
    data: {
      labels: allLabels,
      datasets: [
        {
          label: "Historical Baseline (₹ Lakhs)",
          data: historicalDataset,
          borderColor: "#00E5FF",
          borderWidth: 2.5,
          tension: 0.3,
          pointRadius: 3
        },
        {
          label: "Predicted Trend (₹ Lakhs)",
          data: predictedDataset,
          borderColor: "#10B981",
          borderDash: [5, 5],
          borderWidth: 2.5,
          tension: 0.3,
          pointRadius: 4,
          pointBackgroundColor: "#10B981"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "top", labels: { color: "#94A3B8", font: { family: "Inter", size: 12 } } },
        tooltip: {
          backgroundColor: "#111827",
          borderColor: "rgba(255,255,255,0.1)",
          borderWidth: 1,
          callbacks: { label: (ctx) => `${ctx.dataset.label}: ₹${ctx.raw} Lakhs` }
        }
      },
      scales: {
        x: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94A3B8" } },
        y: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94A3B8" } }
      }
    }
  });
}
