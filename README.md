# ASTRAL — AI-Powered Business Intelligence Platform

ASTRAL is an enterprise decision-making business intelligence platform designed specifically for business managers, executives, and decision-makers.

It provides immediate daily clarity on business health, analytics, Scikit-learn machine learning predictions (revenue forecasting, customer churn risk, anomaly detection), a data-connected Python AI Assistant, a Digital Twin What-If simulator, and executive PDF/CSV report generation.

---

## 🌟 Key Features

1. **Business Overview Dashboard**: 
   - 92/100 Healthy Business Health Score
   - 5 core KPI cards (Revenue ₹12.4 Cr, Orders 48,250, Customers 14,120, Profit ₹3.1 Cr)
   - Interactive Revenue Performance trend chart with 7D/30D/3M/1Y timeframe tabs
   - Daily AI Summary & Key Insights
   - Attention Required high-priority alerts
2. **Business Analytics**: 
   - Category distribution breakdown (Electronics, Software, Cloud Services, Hardware, Consulting)
   - Daily order volume trend & top products growth table
3. **Machine Learning Predictions**:
   - **Revenue Forecast**: `RandomForestRegressor` trained on historical daily metrics
   - **Customer Churn Risk**: `LogisticRegression` scoring customer recency and order frequency
   - **Anomaly Detection**: `IsolationForest` detecting unusual metric spikes or drops
4. **Python AI Assistant**:
   - Data-backed conversational AI answering questions about sales, top products, churn risk, and key business drivers with metric badges and actionable recommendations
5. **Digital Twin (What-If Simulator)**:
   - Tune variables (Sales Growth, Customer Expansion, Discount Rate, Marketing Spend) to observe real-time side-by-side comparison of baseline vs simulated revenue, profit, orders, and customer count
6. **Executive Reports**:
   - Automated Daily, Weekly, and Monthly business reports with browser PDF printing and instant CSV export
7. **Clean Enterprise Design**:
   - Built matching premium SaaS aesthetics: Deep Green primary (`#006B50`), Dark Navy (`#101828`), Light Gray (`#F8FAFC`), rounded cards, thin borders, soft elevation

---

## 🏗️ Architecture & Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Chart.js
- **Backend API**: Python 3, FastAPI, Uvicorn, Pydantic
- **Database**: SQLite (`database/astral.db`)
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-Learn (Random Forest, Logistic Regression, Isolation Forest)

---

## 🚀 How to Run ASTRAL

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database & Preseed Metrics
```bash
python backend/database.py
```

### 3. Start FastAPI Server
```bash
python backend/main.py
```
*Or using uvicorn:*
```bash
uvicorn backend.main:app --reload --port 8000
```

### 4. Open in Browser
Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your web browser.

- **Public Landing Page**: `http://127.0.0.1:8000/`
- **Login Page**: `http://127.0.0.1:8000/login`
- **1-Click Executive Demo**: Click **⚡ 1-Click Executive Demo Login** on the login page or sign in with:
  - **Email**: `admin@astral.ai`
  - **Password**: `astral2026`
