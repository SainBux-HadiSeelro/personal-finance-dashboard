<div align="center">

# ⚡ FinPulse
### Modern Personal Finance Tracker & Analytics Engine

*Take control of your wealth with dual-interface ledger management, precision micro-currency accounting, and AI-inspired financial health scoring.*

<br/>

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)
[![Built with UV](https://img.shields.io/badge/UV-Packager-DE5FE9?style=for-the-badge)](https://github.com/astral-sh/uv)
[![Zero Database](https://img.shields.io/badge/Database-Zero--DB%20Flatfile-22c55e?style=for-the-badge)](https://github.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.style=for-the-badge)](LICENSE)

<br/>

[Key Features](#-key-features) • [Architecture](#-architecture) • [Getting Started](#-getting-started) • [Live Demo Guide](#-one-click-portfolio-showcase) • [Specifications](#-engineering-specification)

<br/>

</div>

---

## 💡 Overview

**FinPulse** is a personal financial ledger and intelligence system built for modern developers and fintech enthusiasts. Combining the velocity of an interactive terminal CLI with the elegance of a Streamlit web application, FinPulse offers complete financial observability without heavyweight database dependencies.

Built from the ground up to eliminate common binary floating-point errors, every currency calculation in FinPulse is strictly powered by **64-bit integer paisa/cents arithmetic**.

---

## 🚀 Key Features

<table>
  <tr>
    <td width="50%">
      <h3>📊 Fintech Web Dashboard</h3>
      <ul>
        <li><b>Glassmorphism UI:</b> High-contrast KPI cards tracking Net Balance, Monthly Inflows, Outflows, and Savings Rate.</li>
        <li><b>Interactive Plotly Visuals:</b> Donut category breakdowns and monthly income vs expense comparative bar charts.</li>
        <li><b>In-App Transaction Logging:</b> Intuitive forms for instant expense and income logging with instant state refresh.</li>
      </ul>
    </td>
    <td width="50%">
      <h3>⌨️ Interactive Terminal CLI</h3>
      <ul>
        <li><b>Keyboard-Driven UX:</b> Fast arrow-key navigation with Questionary select lists.</li>
        <li><b>Rich Formatting:</b> Beautiful ASCII tables, custom stylized panels, and colored progress bars.</li>
        <li><b>Windows Safe:</b> Configured UTF-8 rendering preventing console charmap encode crashes.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🎯 Smart Budgeting & Alerts</h3>
      <ul>
        <li><b>Monthly Category Limits:</b> Allocate budgets for Food, Transport, Bills, Shopping, and more.</li>
        <li><b>Dynamic Status Indicators:</b> Visual color-coded progress bars (🟢 <code>&lt;70%</code>, 🟡 <code>70-100%</code>, 🔴 <code>&gt;100% Exceeded</code>).</li>
      </ul>
    </td>
    <td width="50%">
      <h3>🧠 Financial Health & Insights</h3>
      <ul>
        <li><b>Health Score (0-100):</b> Automated score grading (A+, B, C, D) assessing savings discipline and budget adherence.</li>
        <li><b>50/30/20 Rule Analysis:</b> Visual pie breakdown of Needs (50%), Wants (30%), and Wealth Retention (20%).</li>
      </ul>
    </td>
  </tr>
</table>

---

## 💎 The Engineering Principle: Zero Floating-Point Errors

Most casual finance apps make the fatal mistake of storing currency as floats (`12.50`), causing binary approximation bugs (`19.99 * 100 == 1998.9999999999998`).

**FinPulse enforces banking-grade integer micro-units:**

```python
# ❌ INCORRECT (Common floating-point bug)
amount = 19.99
paisa = int(amount * 100) # Output: 1998 (1 paisa lost!)

# ✅ FINPULSE ARCHITECTURE (Precision Integer Arithmetic)
amount = 19.99
paisa = round(float(amount) * 100) # Output: 1999 (100% mathematically exact)
display = paisa / 100 # Display: Rs. 19.99
```

---

## 🏗️ Architecture & Project Structure

```bash
personal_finance_tracker/
├── main.py                     # CLI entrypoint with interactive menu loop
├── pyproject.toml              # Project dependencies & packaging specs
├── requirements.txt            # Streamlit Community Cloud deployment spec
├── SPECIFICATION.md            # Technical & mathematical specification
├── database/                   # Lightweight flat-file storage
│   ├── transactions.txt        # All transactions (date, type, category, paisa, memo)
│   └── budgets.txt             # Category monthly allocations (category, paisa)
├── features/                   # Core business logic modules
│   ├── __init__.py             # UTF-8 terminal safety handler
│   ├── transactions/           # Transaction entry, query, & balance logic
│   ├── budgets/                # Budget allocation & threshold calculation
│   ├── analytics/              # Spending breakdown & top category analytics
│   ├── smart_assistant/        # Daily checkup & smart recommendation engine
│   └── data_management/        # CSV & JSON export routines
└── web/
    └── app.py                  # High-end Streamlit web dashboard
```

---

## ⚡ Quickstart

### Prerequisites
* **Python 3.11+** installed
* Recommended: [UV package manager](https://github.com/astral-sh/uv) (fastest Python workflow)

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/finpulse.git
cd finpulse
```

### 2. Install Dependencies
Using **UV** (Recommended):
```bash
uv sync
```
*Or standard Python virtual environment:*
```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

---

## 🎮 How to Run

### 🖥️ Option A: Run the Fintech Web Dashboard
```bash
uv run streamlit run web/app.py
```
> Opens automatically in your browser at `http://localhost:8501`.

### 💻 Option B: Run the Interactive Terminal CLI
```bash
uv run python main.py
```
*Use arrow keys `↑` `↓` and `Enter` to navigate.*

---

## 🌟 One-Click Portfolio Showcase

Recruiters or visitors reviewing your GitHub repository will want to see rich data immediately without having to manually input 20 records.

FinPulse includes an **Instant Showcase Engine**:
1. Open the Web Dashboard.
2. In the sidebar, click **`✨ Load Rich Demo Data`**.
3. Realistic engineering income, freelancer payouts, utility bills, and category budgets will be instantly populated across all Plotly charts!

---

## 🌐 Deploy to Streamlit Community Cloud (Free)

Deploy your own live URL in 2 minutes:
1. Push your code to GitHub.
2. Visit **[share.streamlit.io](https://share.streamlit.io/)** and connect your GitHub account.
3. Select your repository and set the **Main file path** to:
   ```text
   web/app.py
   ```
4. Click **Deploy** — your live portfolio link is ready to share!

---

## 📄 Engineering Specification
Detailed mathematical definitions, schema formats, and system constraints are documented in [SPECIFICATION.md](file:///c:/Users/dell/Desktop/programming%20files/Gemini_cli_projects/personal_finance_tracker/SPECIFICATION.md).

---

## 🛡️ License
Distributed under the **MIT License**. See `LICENSE` for more information.

<div align="center">
  <sub>Engineered with precision for portfolio excellence • Made with Python & Streamlit</sub>
</div>
