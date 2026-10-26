/* ==========================================================================
   ASTRAL ANALYTICS JAVASCRIPT - Multi-dimensional Data Visualizations
   ========================================================================== */

document.addEventListener("DOMContentLoaded", async () => {
  const data = await apiFetch("/api/analytics");
  if (!data) return;

  // 1. Render Category Doughnut Chart
  if (data.category_distribution && document.getElementById("categoryDoughnutChart")) {
    const ctx = document.getElementById("categoryDoughnutChart").getContext("2d");
    new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: Object.keys(data.category_distribution),
        datasets: [{
          data: Object.values(data.category_distribution),
          backgroundColor: ["#10B981", "#00E5FF", "#3B82F6", "#F59E0B", "#8B5CF6"],
          borderWidth: 2,
          borderColor: "#111827"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom", labels: { color: "#94A3B8", font: { family: "Inter", size: 12 } } },
          tooltip: { backgroundColor: "#111827", borderColor: "rgba(255,255,255,0.1)", borderWidth: 1 }
        },
        cutout: "68%"
      }
    });
  }

  // 2. Render Order Trend Bar Chart
  if (data.order_trend && document.getElementById("orderTrendChart")) {
    const ctx = document.getElementById("orderTrendChart").getContext("2d");
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: data.order_trend.labels,
        datasets: [{
          label: "Daily Order Volume",
          data: data.order_trend.values,
          backgroundColor: "#00E5FF",
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94A3B8" } },
          y: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94A3B8" } }
        }
      }
    });
  }

  // 3. Populate Top Products Table
  const tableBody = document.getElementById("products-table-body");
  if (tableBody && data.top_products) {
    tableBody.innerHTML = data.top_products.map(prod => `
      <tr>
        <td style="font-weight: 600; color: #FFFFFF;">${prod.name}</td>
        <td><span class="badge badge-blue">${prod.category}</span></td>
        <td style="color: #E2E8F0;">${prod.sales_count.toLocaleString()} units</td>
        <td style="font-weight: 700; color: #00E5FF;">₹${(prod.revenue_generated / 10000000).toFixed(2)} Cr</td>
        <td><span class="badge badge-green">+${prod.growth_rate}% YoY</span></td>
      </tr>
    `).join("");
  }
});
