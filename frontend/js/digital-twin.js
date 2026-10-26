/* ==========================================================================
   ASTRAL DIGITAL TWIN JAVASCRIPT - What-If Business Simulation Engine
   ========================================================================== */

let simChartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
  const salesSlider = document.getElementById("slider-sales");
  const custSlider = document.getElementById("slider-cust");
  const discSlider = document.getElementById("slider-disc");
  const mktgSlider = document.getElementById("slider-mktg");

  const salesVal = document.getElementById("val-sales");
  const custVal = document.getElementById("val-cust");
  const discVal = document.getElementById("val-disc");
  const mktgVal = document.getElementById("val-mktg");

  const runBtn = document.getElementById("run-sim-btn");

  // Sync Slider values
  if (salesSlider) {
    salesSlider.addEventListener("input", () => salesVal.textContent = `${salesSlider.value}%`);
  }
  if (custSlider) {
    custSlider.addEventListener("input", () => custVal.textContent = `${custSlider.value}%`);
  }
  if (discSlider) {
    discSlider.addEventListener("input", () => discVal.textContent = `${discSlider.value}%`);
  }
  if (mktgSlider) {
    mktgSlider.addEventListener("input", () => mktgVal.textContent = `₹${(mktgSlider.value / 100000).toFixed(1)} Lakhs`);
  }

  if (runBtn) {
    runBtn.addEventListener("click", runSimulation);
  }

  // Initial Run
  runSimulation();
});

async function runSimulation() {
  const sales_growth = parseFloat(document.getElementById("slider-sales")?.value || 10);
  const customer_growth = parseFloat(document.getElementById("slider-cust")?.value || 8);
  const discount_rate = parseFloat(document.getElementById("slider-disc")?.value || 5);
  const marketing_spend = parseFloat(document.getElementById("slider-mktg")?.value || 500000);

  const res = await fetch("/api/digital-twin/simulate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sales_growth, customer_growth, discount_rate, marketing_spend, order_volume: sales_growth * 0.8 })
  });

  if (!res.ok) return;

  const data = await res.json();
  
  // 1. Update Comparison Card Text
  document.getElementById("cur-rev").textContent = data.current_scenario.formatted_revenue;
  document.getElementById("sim-rev").textContent = data.simulated_scenario.formatted_revenue;
  document.getElementById("rev-diff").textContent = data.impact_analysis.revenue_change_pct;

  document.getElementById("cur-orders").textContent = data.current_scenario.orders.toLocaleString();
  document.getElementById("sim-orders").textContent = data.simulated_scenario.orders.toLocaleString();
  document.getElementById("orders-diff").textContent = data.impact_analysis.orders_change_pct;

  document.getElementById("cur-profit").textContent = data.current_scenario.formatted_profit;
  document.getElementById("sim-profit").textContent = data.simulated_scenario.formatted_profit;
  document.getElementById("profit-diff").textContent = data.impact_analysis.profit_change_pct;

  document.getElementById("cur-cust").textContent = data.current_scenario.customers.toLocaleString();
  document.getElementById("sim-cust").textContent = data.simulated_scenario.customers.toLocaleString();
  document.getElementById("cust-diff").textContent = data.impact_analysis.customers_change_pct;

  document.getElementById("sim-recommendation-text").textContent = data.recommendation;

  // 2. Render Side-by-side Comparison Chart
  renderSimulationChart(
    data.current_scenario.revenue / 10000000, data.simulated_scenario.revenue / 10000000,
    data.current_scenario.profit / 10000000, data.simulated_scenario.profit / 10000000
  );
}

function renderSimulationChart(curRev, simRev, curProfit, simProfit) {
  const ctx = document.getElementById("simChart").getContext("2d");
  if (simChartInstance) simChartInstance.destroy();

  simChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Revenue (₹ Cr)", "Profit (₹ Cr)"],
      datasets: [
        {
          label: "Current Baseline",
          data: [curRev, curProfit],
          backgroundColor: "#475569",
          borderRadius: 6
        },
        {
          label: "Simulated Scenario",
          data: [simRev, simProfit],
          backgroundColor: "#10B981",
          borderRadius: 6
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
          borderWidth: 1
        }
      },
      scales: {
        x: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94A3B8" } },
        y: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94A3B8" } }
      }
    }
  });
}
