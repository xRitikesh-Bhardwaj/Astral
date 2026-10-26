/* ==========================================================================
   ASTRAL REPORTS JAVASCRIPT - Executive Report Generation & Export
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  const reportTabs = document.querySelectorAll(".report-type-tab");
  const downloadCsvBtn = document.getElementById("download-csv-btn");
  const printPdfBtn = document.getElementById("print-pdf-btn");

  reportTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      reportTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      const type = tab.getAttribute("data-type");
      loadReport(type);
    });
  });

  if (downloadCsvBtn) {
    downloadCsvBtn.addEventListener("click", () => {
      window.location.href = "/api/reports/export-csv";
    });
  }

  if (printPdfBtn) {
    printPdfBtn.addEventListener("click", () => {
      window.print();
    });
  }

  // Initial Load
  loadReport("daily");
});

async function loadReport(type) {
  const report = await apiFetch(`/api/reports/${type}`);
  if (!report) return;

  document.getElementById("report-title").textContent = report.title;
  document.getElementById("report-date").textContent = `Generated on: ${report.generated_at}`;

  if (report.metrics) {
    document.getElementById("rep-rev").textContent = report.metrics.formatted_revenue;
    document.getElementById("rep-orders").textContent = report.metrics.total_orders.toLocaleString();
    document.getElementById("rep-cust").textContent = report.metrics.average_active_customers.toLocaleString();
    document.getElementById("rep-profit").textContent = `₹${(report.metrics.total_profit / 10000000).toFixed(2)} Cr (${report.metrics.profit_margin_pct}%)`;
  }

  // Populate Top Products
  const prodContainer = document.getElementById("report-top-products");
  if (prodContainer && report.top_products) {
    prodContainer.innerHTML = report.top_products.map(p => `
      <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--color-border-subtle); font-size: 0.875rem;">
        <span><strong>${p.name}</strong> (${p.category})</span>
        <span style="color: var(--color-green-primary); font-weight: 700;">₹${(p.revenue / 10000000).toFixed(2)} Cr</span>
      </div>
    `).join("");
  }

  // Insights & Recommendations
  const insightsContainer = document.getElementById("report-insights");
  if (insightsContainer && report.business_insights) {
    insightsContainer.innerHTML = report.business_insights.map(item => `<li>${item}</li>`).join("");
  }

  const recContainer = document.getElementById("report-recommendations");
  if (recContainer && report.recommendations) {
    recContainer.innerHTML = report.recommendations.map(item => `<li>${item}</li>`).join("");
  }
}
