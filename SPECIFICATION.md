# FinPulse — Technical Specification

**Version:** 1.0.0  
**Status:** Approved  
**Author:** Engineering Team  
**Architecture Type:** Dual-Interface Local-First Fintech Application (CLI + Streamlit Web Dashboard)

---

## 1. Executive Summary & Core Objectives

**FinPulse** is a personal finance tracker and analytics engine engineered with financial-grade precision. It solves the common floating-point inaccuracy issues found in basic ledger apps by adhering strictly to **integer-based micro-currency storage (paisa/cents)**. 

The application offers a dual-interface experience:
1. **Interactive CLI Engine**: Keyboard-driven terminal interface utilizing `questionary` and `rich`.
2. **Fintech Web Dashboard**: A visual analytical cockpit built with `streamlit` and `plotly` featuring automated financial health scoring, budget adherence tracking, and 50/30/20 rule analytics.

---

## 2. System Architecture

```
                                  +-----------------------+
                                  |      User Entry       |
                                  +-----------+-----------+
                                              |
                     +------------------------+------------------------+
                     |                                                 |
         [Interactive Terminal]                               [Web Browser]
                     |                                                 |
         +-----------v-----------+                         +-----------v-----------+
         |    main.py (CLI)      |                         |    web/app.py (Web)   |
         |  (Questionary + Rich) |                         |  (Streamlit + Plotly) |
         +-----------+-----------+                         +-----------+-----------+
                     |                                                 |
         +-----------v--------------------+                            |
         |      features/ Submodules      |<---------------------------+
         | - transactions.py              |
         | - budgets.py                   |
         | - analytics.py                 |
         | - smart_assistant.py           |
         | - data_management.py           |
         +----------------+---------------+
                          |
             +------------v------------+
             |   Local Flat Database   |
             | - database/transactions |
             | - database/budgets.txt  |
             +-------------------------+
```

---

## 3. Critical Financial Engineering Rule

> [!IMPORTANT]
> **Zero Floating-Point Storage Rule:**  
> Monetary amounts must NEVER be stored as floating-point numbers in the ledger. All financial transactions and budget allocations are stored as 64-bit integers in the smallest currency unit (**paisa / cents**).

### Mathematical Model
$$\text{Storage Value (Paisa)} = \text{round}(\text{Display Value (Rupees)} \times 100)$$
$$\text{Display Value (Rupees)} = \frac{\text{Storage Value (Paisa)}}{100.0}$$

### Rationale
Binary floating-point arithmetic (IEEE 754) introduces precision degradation:
```python
# Flawed floating-point conversion:
int(float("19.99") * 100) # Output: 1998 (1 paisa lost!)

# FinPulse precision model:
round(float("19.99") * 100) # Output: 1999 (100% accurate)
```

---

## 4. Data Storage Specifications

Data is persisted in lightweight, local, human-readable comma-delimited flat files (`.txt` / `.csv`) located under `/database`.

### 4.1. Transactions Ledger (`database/transactions.txt`)
* **Format:** Plain text CSV (no header).
* **Fields:** `date,type,category,amount_paisa,description`

| Field | Type | Allowed Values / Format | Description |
| :--- | :--- | :--- | :--- |
| `date` | String | `YYYY-MM-DD` | Date of transaction |
| `type` | String | `expense` \| `income` | Transaction direction |
| `category` | String | See Section 4.3 | Classification category |
| `amount_paisa` | Integer | $> 0$ (e.g. `250000` = Rs. 2,500.00) | Amount in smallest currency unit |
| `description` | String | Text (commas stripped or escaped) | Short memo / description |

### 4.2. Budgets Ledger (`database/budgets.txt`)
* **Format:** Plain text CSV (no header).
* **Fields:** `category,amount_paisa`

| Field | Type | Allowed Values / Format | Description |
| :--- | :--- | :--- | :--- |
| `category` | String | Unique expense category | Target budget category |
| `amount_paisa` | Integer | $> 0$ (e.g. `1000000` = Rs. 10,000.00) | Monthly limit in paisa |

### 4.3. Standard Category Taxonomy
* **Expense Categories:** `Food`, `Transport`, `Shopping`, `Bills`, `Entertainment`, `Health`, `Other`
* **Income Categories:** `Salary`, `Freelance`, `Business`, `Investment`, `Gift`, `Other`

---

## 5. Analytical Engine & Algorithms

### 5.1. Savings Rate Calculation
$$\text{Savings Rate} = \left( \frac{\text{Total Income} - \text{Total Expenses}}{\text{Total Income}} \right) \times 100$$
* **Benchmark:** Minimum $20\%$ recommended for financial health.

### 5.2. Financial Health Score Algorithm ($0 - 100$)
FinPulse computes a composite fitness score to evaluate user financial status:
1. **Base Score:** 50 points
2. **Savings Factor (Up to $\pm 30$ pts):**
   * $\ge 30\%$ savings rate $\rightarrow +30$ pts
   * $20\% - 29\%$ savings rate $\rightarrow +20$ pts
   * $10\% - 19\%$ savings rate $\rightarrow +10$ pts
   * $< 0\%$ (Deficit) $\rightarrow -20$ pts
3. **Budget Adherence Factor (Up to $\pm 20$ pts):**
   * 0 categories over budget $\rightarrow +20$ pts
   * 1 category over budget $\rightarrow +10$ pts
   * $>1$ categories over budget $\rightarrow -10$ pts
4. **Boundary Constraint:** $\text{Score} = \max(5, \min(100, \text{Computed Score}))$

#### Grading Scale
* **80 - 100:** Grade A+ (Excellent Financial Fitness)
* **65 - 79:** Grade B (Healthy)
* **45 - 64:** Grade C (Fair / Caution)
* **< 45:** Grade D (Critical Deficit)

### 5.3. 50/30/20 Rule Breakdown
* **Needs ($50\%$):** `Bills`, `Food`, `Transport`, `Health`
* **Wants ($30\%$):** `Shopping`, `Entertainment`, `Other`
* **Savings ($20\%$):** $\max(0, \text{Net Income} - \text{Total Expenses})$

---

## 6. Interface Specifications

### 6.1. Terminal CLI (`main.py`)
* Interactive arrow-key navigation with `questionary`.
* Colorized terminal tables, panels, and progress bars via `rich`.
* Windows console safety: Automatic detection and reconfiguration of `sys.stdout` and `sys.stderr` to `utf-8` with replacement fallback.
* Input sanitization: `None` checks on keyboard interrupts (`Esc` / `Ctrl+C`).

### 6.2. Web Dashboard (`web/app.py`)
* **Responsive Layout:** Sidebar navigation with custom fintech glassmorphism theme.
* **Top Metric Cockpit:** Net Balance, Monthly Income, Monthly Expenses, Savings Rate.
* **Plotly Visuals:** Interactive Donut breakdown, monthly trend comparisons, and 50/30/20 distribution.
* **Budget Tracking:** Dynamic colored progress bars (Green $<70\%$, Amber $70\%-100\%$, Red $>100\%$).
* **Reviewer Showcase Mode:** 1-click sample data populator for instant portfolio evaluation.
* **Export Engine:** Client-side CSV & JSON download buttons.

---

## 7. Deployment & Environment Standards

* **Python Runtime:** `>= 3.11` (Tested on Python 3.12)
* **Package Manager:** `UV` or standard `pip`
* **Cloud Compatibility:** 
  * Compatible with **Streamlit Community Cloud**, **Render**, and **Hugging Face Spaces**.
  * Auto-discovers and creates missing ledger files and directories on fresh cold boots.
