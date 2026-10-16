import os
import sys
import json
from datetime import datetime, date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configure UTF-8 encoding on Windows
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# --- Page Config ---
st.set_page_config(
    page_title="FinPulse | Personal Finance Tracker",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "database")
TRANSACTIONS_FILE = os.path.join(DB_DIR, "transactions.txt")
BUDGETS_FILE = os.path.join(DB_DIR, "budgets.txt")
EXPORT_DIR = os.path.join(BASE_DIR, "export")

os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

# Categories definition per GEMINI.md
EXPENSE_CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]
INCOME_CATEGORIES = ["Salary", "Freelance", "Business", "Investment", "Gift", "Other"]

# --- Custom High-End Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Main Background & Padding */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(240, 244, 255, 0.6) 0%, rgba(247, 249, 252, 0.9) 90%);
    }
    
    /* Metric Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid rgba(226, 232, 240, 0.9);
        border-radius: 16px;
        padding: 22px 24px;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px -4px rgba(15, 23, 42, 0.09);
    }
    .metric-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
    }
    .card-balance::before { background: linear-gradient(90deg, #3b82f6, #6366f1); }
    .card-income::before { background: linear-gradient(90deg, #10b981, #059669); }
    .card-expense::before { background: linear-gradient(90deg, #ef4444, #f43f5e); }
    .card-rate::before { background: linear-gradient(90deg, #8b5cf6, #ec4899); }

    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: #94a3b8;
    }

    /* Section Panels */
    .glass-panel {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.04);
        margin-bottom: 24px;
    }
    
    /* Category Badges */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-income { background: #dcfce7; color: #15803d; }
    .badge-expense { background: #fee2e2; color: #b91c1c; }
    
    /* Health Score Pill */
    .score-badge {
        font-size: 2.2rem;
        font-weight: 800;
        border-radius: 12px;
        padding: 10px 20px;
        display: inline-block;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- Data Access Helpers ---
def load_transactions():
    """Loads transactions from disk, returning structured DataFrame."""
    try:
        if not os.path.exists(TRANSACTIONS_FILE) or os.path.getsize(TRANSACTIONS_FILE) == 0:
            return pd.DataFrame(columns=["date", "type", "category", "amount_paisa", "description", "amount"])
        
        df = pd.read_csv(
            TRANSACTIONS_FILE,
            header=None,
            names=["date", "type", "category", "amount_paisa", "description"],
            dtype={"amount_paisa": "int64"}
        )
        df["amount"] = df["amount_paisa"] / 100.0
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        return df.sort_values(by="date", ascending=False)
    except Exception:
        return pd.DataFrame(columns=["date", "type", "category", "amount_paisa", "description", "amount"])

def load_budgets():
    """Loads budget records."""
    try:
        if not os.path.exists(BUDGETS_FILE) or os.path.getsize(BUDGETS_FILE) == 0:
            return pd.DataFrame(columns=["category", "amount_paisa", "amount"])
        
        df = pd.read_csv(
            BUDGETS_FILE,
            header=None,
            names=["category", "amount_paisa"],
            dtype={"amount_paisa": "int64"}
        )
        df["amount"] = df["amount_paisa"] / 100.0
        return df
    except Exception:
        return pd.DataFrame(columns=["category", "amount_paisa", "amount"])

def save_transaction(date_val, t_type, category, amount_paisa, description):
    """Appends transaction in paisa format."""
    with open(TRANSACTIONS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{date_val},{t_type},{category},{int(amount_paisa)},{description}\n")

def save_budgets(budgets_df):
    """Saves budgets cleanly."""
    clean_df = budgets_df.copy()
    clean_df["amount_paisa"] = clean_df["amount_paisa"].astype(int)
    clean_df[["category", "amount_paisa"]].to_csv(BUDGETS_FILE, header=False, index=False)

def populate_sample_data():
    """Populates realistic demo financial data for portfolio showcase."""
    today = datetime.now()
    sample_records = [
        (f"{today.year}-{today.month:02d}-01", "income", "Salary", 18500000, "Monthly Software Engineer Salary"),
        (f"{today.year}-{today.month:02d}-05", "income", "Freelance", 4500000, "AI Agent UI Design Contract"),
        (f"{today.year}-{today.month:02d}-02", "expense", "Bills", 2500000, "Electricity & High-speed Fiber"),
        (f"{today.year}-{today.month:02d}-03", "expense", "Food", 1800000, "Monthly Grocery Shopping"),
        (f"{today.year}-{today.month:02d}-07", "expense", "Transport", 850000, "Fuel & Toll Charges"),
        (f"{today.year}-{today.month:02d}-09", "expense", "Shopping", 1200000, "Noise Cancelling Headphones"),
        (f"{today.year}-{today.month:02d}-12", "expense", "Entertainment", 600000, "Weekend Dinner & Cinema"),
        (f"{today.year}-{today.month:02d}-14", "expense", "Health", 450000, "Gym Subscription & Supplements"),
        (f"{today.year}-{today.month:02d}-15", "income", "Investment", 1500000, "Stock Dividend Payout"),
    ]
    with open(TRANSACTIONS_FILE, "w", encoding="utf-8") as f:
        for r in sample_records:
            f.write(f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]}\n")
            
    sample_budgets = [
        ("Food", 2500000),
        ("Transport", 1000000),
        ("Shopping", 1500000),
        ("Bills", 3000000),
        ("Entertainment", 1000000),
        ("Health", 600000),
    ]
    sample_b_df = pd.DataFrame(sample_budgets, columns=["category", "amount_paisa"])
    save_budgets(sample_b_df)

# --- Navigation & Header ---
st.sidebar.markdown("""
<div style="text-align: center; padding: 12px 0 20px 0;">
    <h2 style="margin: 0; color: #1e293b; font-weight: 800; letter-spacing: -0.5px;">⚡ FinPulse</h2>
    <p style="margin: 4px 0 0 0; color: #64748b; font-size: 0.85rem;">Smart Financial Management</p>
</div>
""", unsafe_allow_html=True)

nav = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard Overview", "➕ Add Transaction", "🎯 Budgets & Goals", "🧠 Financial Health & Insights", "📁 Data Management"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# Quick Demo Data Button in Sidebar for Reviewers
if st.sidebar.button("✨ Load Rich Demo Data"):
    populate_sample_data()
    st.sidebar.success("Sample transactions and budgets loaded!")
    st.rerun()

st.sidebar.markdown("""
<div style="margin-top: 30px; padding: 12px; background: rgba(241, 245, 249, 0.8); border-radius: 10px; font-size: 0.75rem; color: #64748b; text-align: center;">
    <strong>Built with Python & Streamlit</strong><br>
    Paisa-precision accounting engine
</div>
""", unsafe_allow_html=True)

# Load State
df_trans = load_transactions()
df_budgets = load_budgets()

# Empty state helper
if df_trans.empty:
    st.info("👋 Welcome to **FinPulse**! No transactions found. You can add one from the sidebar or click below to populate instant demo data to explore all charts.")
    if st.button("🚀 Load Instant Showcase Data"):
        populate_sample_data()
        st.rerun()
    st.stop()

# Helper calculations
now = datetime.now()
current_month_df = df_trans[(df_trans["date"].dt.month == now.month) & (df_trans["date"].dt.year == now.year)]

total_income = float(df_trans[df_trans["type"] == "income"]["amount"].sum())
total_expense = float(df_trans[df_trans["type"] == "expense"]["amount"].sum())
net_savings = total_income - total_expense
savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0.0

month_income = float(current_month_df[current_month_df["type"] == "income"]["amount"].sum())
month_expense = float(current_month_df[current_month_df["type"] == "expense"]["amount"].sum())
month_net = month_income - month_expense

# ==========================================
# PAGE 1: DASHBOARD OVERVIEW
# ==========================================
if nav == "📊 Dashboard Overview":
    st.title("Financial Dashboard")
    st.caption(f"Real-time overview for **{now.strftime('%B %Y')}**")

    # Top KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card card-balance">
            <div class="metric-title">Net Balance</div>
            <div class="metric-value">Rs. {net_savings:,.2f}</div>
            <div class="metric-subtitle">{'🟢 Surplus' if net_savings >= 0 else '🔴 Deficit'} all-time</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card card-income">
            <div class="metric-title">Total Income</div>
            <div class="metric-value">Rs. {total_income:,.2f}</div>
            <div class="metric-subtitle">Rs. {month_income:,.2f} this month</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card card-expense">
            <div class="metric-title">Total Expenses</div>
            <div class="metric-value">Rs. {total_expense:,.2f}</div>
            <div class="metric-subtitle">Rs. {month_expense:,.2f} this month</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card card-rate">
            <div class="metric-title">Savings Rate</div>
            <div class="metric-value">{savings_rate:.1f}%</div>
            <div class="metric-subtitle">Target: > 20%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row
    chart_col1, chart_col2 = st.columns([3, 2])
    
    with chart_col1:
        st.subheader("Monthly Income vs Expense Trend")
        # Group by Year-Month
        df_copy = df_trans.copy()
        df_copy["period"] = df_copy["date"].dt.strftime("%Y-%m")
        grouped = df_copy.groupby(["period", "type"])["amount"].sum().reset_index()
        
        if not grouped.empty:
            fig_trend = px.bar(
                grouped,
                x="period",
                y="amount",
                color="type",
                barmode="group",
                color_discrete_map={"income": "#10b981", "expense": "#ef4444"},
                labels={"period": "Month", "amount": "Amount (Rs.)", "type": "Type"},
                height=340
            )
            fig_trend.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="#f1f5f9")
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Not enough data to display trend.")

    with chart_col2:
        st.subheader("Expenses by Category")
        expense_df = df_trans[df_trans["type"] == "expense"]
        if not expense_df.empty:
            cat_sum = expense_df.groupby("category")["amount"].sum().reset_index()
            fig_pie = px.pie(
                cat_sum,
                names="category",
                values="amount",
                hole=0.55,
                color_discrete_sequence=px.colors.qualitative.Pastel,
                height=340
            )
            fig_pie.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="v", yanchor="middle", y=0.5)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense data recorded yet.")

    # Recent Transactions Table
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Recent Transactions")
    
    recent_df = df_trans.head(6).copy()
    recent_df["Formatted Date"] = recent_df["date"].dt.strftime("%d %b, %Y")
    recent_df["Amount Display"] = recent_df.apply(
        lambda r: f"+ Rs. {r['amount']:,.2f}" if r["type"] == "income" else f"- Rs. {r['amount']:,.2f}",
        axis=1
    )
    
    display_table = recent_df[["Formatted Date", "type", "category", "description", "Amount Display"]].rename(
        columns={"type": "Type", "category": "Category", "description": "Description", "Amount Display": "Amount"}
    )
    st.dataframe(display_table, use_container_width=True, hide_index=True)


# ==========================================
# PAGE 2: ADD TRANSACTION
# ==========================================
elif nav == "➕ Add Transaction":
    st.title("Record New Transaction")
    st.caption("Transactions are stored in integer paisa format to eliminate floating point issues.")

    with st.container():
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        
        trans_type = st.radio(
            "Transaction Type",
            ["Expense", "Income"],
            horizontal=True
        )
        
        col1, col2 = st.columns(2)
        with col1:
            amount_val = st.number_input(
                "Amount (in Rupees)",
                min_value=0.01,
                step=10.0,
                format="%.2f",
                help="Enter amount in Rupees (e.g. 1500.50)"
            )
            
            categories = EXPENSE_CATEGORIES if trans_type == "Expense" else INCOME_CATEGORIES
            category_val = st.selectbox("Category", categories)

        with col2:
            trans_date = st.date_input("Date", value=date.today())
            description_val = st.text_input("Description / Memo", placeholder="e.g. Client Freelance Payment or Grocery")

        submit_btn = st.button("💾 Save Transaction", type="primary", use_container_width=True)
        
        if submit_btn:
            if not description_val.strip():
                st.warning("Please provide a short description for clarity.")
            else:
                amount_paisa = round(amount_val * 100)
                save_transaction(
                    trans_date.strftime("%Y-%m-%d"),
                    trans_type.lower(),
                    category_val,
                    amount_paisa,
                    description_val.strip()
                )
                st.success(f"✅ {trans_type} of Rs. {amount_val:,.2f} recorded successfully!")
                st.balloons()
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# PAGE 3: BUDGETS & GOALS
# ==========================================
elif nav == "🎯 Budgets & Goals":
    st.title("Budget Management")
    st.caption("Set monthly category spending limits and monitor budget health.")

    # Form to Set / Update Budget
    with st.expander("➕ Set or Update Category Budget", expanded=df_budgets.empty):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            b_cat = st.selectbox("Budget Category", EXPENSE_CATEGORIES)
        with col2:
            b_amount = st.number_input("Monthly Limit (Rs.)", min_value=1.0, step=100.0, format="%.2f")
        with col3:
            st.write("")
            st.write("")
            b_save = st.button("Save Budget", type="primary")

        if b_save:
            paisa_val = round(b_amount * 100)
            cur_budgets = load_budgets()
            if b_cat in cur_budgets["category"].values:
                cur_budgets.loc[cur_budgets["category"] == b_cat, "amount_paisa"] = paisa_val
            else:
                new_row = pd.DataFrame([{"category": b_cat, "amount_paisa": paisa_val}])
                cur_budgets = pd.concat([cur_budgets, new_row], ignore_index=True)
            save_budgets(cur_budgets)
            st.success(f"Budget for {b_cat} set to Rs. {b_amount:,.2f}")
            st.rerun()

    # Budget Health Cards
    if df_budgets.empty:
        st.info("No budgets configured yet. Use the form above to add your first category budget!")
    else:
        st.subheader(f"Current Month Budget Performance ({now.strftime('%B %Y')})")
        
        # Calculate spending per category for current month
        cur_expenses = current_month_df[current_month_df["type"] == "expense"]
        spent_map = cur_expenses.groupby("category")["amount"].sum().to_dict()
        
        cols = st.columns(2)
        idx = 0
        for _, b_row in df_budgets.iterrows():
            cat = b_row["category"]
            limit = float(b_row["amount"])
            spent = float(spent_map.get(cat, 0.0))
            pct = (spent / limit * 100) if limit > 0 else 0.0
            remaining = limit - spent

            with cols[idx % 2]:
                st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
                
                header_col1, header_col2 = st.columns([2, 1])
                with header_col1:
                    st.markdown(f"### {cat}")
                with header_col2:
                    if pct > 100:
                        st.markdown('<span style="color:#ef4444;font-weight:700;">🚨 Exceeded</span>', unsafe_allow_html=True)
                    elif pct >= 80:
                        st.markdown('<span style="color:#f59e0b;font-weight:700;">⚠️ Alert</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span style="color:#10b981;font-weight:700;">✅ On Track</span>', unsafe_allow_html=True)
                
                # Progress Bar
                progress_val = min(int(pct), 100)
                st.progress(progress_val)
                
                c_a, c_b, c_c = st.columns(3)
                c_a.metric("Spent", f"Rs. {spent:,.0f}")
                c_b.metric("Limit", f"Rs. {limit:,.0f}")
                c_c.metric("Remaining", f"Rs. {remaining:,.0f}", delta=f"{100-pct:.0f}% left")
                
                st.markdown('</div>', unsafe_allow_html=True)
            idx += 1


# ==========================================
# PAGE 4: FINANCIAL HEALTH & INSIGHTS
# ==========================================
elif nav == "🧠 Financial Health & Insights":
    st.title("Financial Health & AI Analytics")
    st.caption("Comprehensive analysis of savings discipline, 50/30/20 balance, and financial fitness.")

    # Calculate Score
    score = 50  # base
    
    # Savings factor (up to 30 pts)
    if savings_rate >= 30:
        score += 30
    elif savings_rate >= 20:
        score += 20
    elif savings_rate >= 10:
        score += 10
    elif savings_rate < 0:
        score -= 20

    # Budget adherence factor (up to 20 pts)
    over_budget_count = 0
    if not df_budgets.empty:
        cur_expenses = current_month_df[current_month_df["type"] == "expense"]
        spent_map = cur_expenses.groupby("category")["amount"].sum().to_dict()
        for _, b_row in df_budgets.iterrows():
            if spent_map.get(b_row["category"], 0.0) > b_row["amount"]:
                over_budget_count += 1
        if over_budget_count == 0:
            score += 20
        elif over_budget_count == 1:
            score += 10
        else:
            score -= 10
    else:
        score += 10

    score = max(5, min(100, score))
    
    if score >= 80:
        grade = "A+ (Excellent)"
        score_color = "#10b981"
        badge_bg = "#dcfce7"
    elif score >= 65:
        grade = "B (Healthy)"
        score_color = "#3b82f6"
        badge_bg = "#dbeafe"
    elif score >= 45:
        grade = "C (Fair)"
        score_color = "#f59e0b"
        badge_bg = "#fef3c7"
    else:
        grade = "D (Critical)"
        score_color = "#ef4444"
        badge_bg = "#fee2e2"

    # Score Banner
    col_score, col_details = st.columns([1, 2])
    with col_score:
        st.markdown(f"""
        <div class="glass-panel" style="text-align: center;">
            <div style="font-size: 0.9rem; font-weight: 700; color: #64748b; margin-bottom: 8px;">FINANCIAL HEALTH SCORE</div>
            <div class="score-badge" style="background: {badge_bg}; color: {score_color};">{score}/100</div>
            <h4 style="margin-top: 12px; color: {score_color}; font-weight: 700;">{grade}</h4>
        </div>
        """, unsafe_allow_html=True)

    with col_details:
        st.markdown("""
        <div class="glass-panel">
            <h4 style="margin-top: 0;">💡 Actionable Financial Insights</h4>
        """, unsafe_allow_html=True)
        
        if savings_rate >= 20:
            st.success(f"🎯 **Strong Savings Rate:** You are saving **{savings_rate:.1f}%** of your income, beating the golden 20% benchmark!")
        else:
            st.warning(f"⚠️ **Boost Your Savings:** Your savings rate is currently **{savings_rate:.1f}%**. Target at least 20% for financial security.")

        if over_budget_count > 0:
            st.error(f"🚨 **Budget Alert:** You have exceeded your budget in **{over_budget_count}** categories this month.")
        else:
            st.info("✅ **Great Discipline:** All category expenses are within your defined budget limits.")

        st.markdown('</div>', unsafe_allow_html=True)

    # 50 / 30 / 20 Rule Breakdown
    st.subheader("50/30/20 Rule Analysis")
    st.caption("Standard guideline: 50% Needs (Bills/Food/Transport), 30% Wants (Shopping/Entertainment), 20% Savings.")

    needs_cats = ["Bills", "Food", "Transport", "Health"]
    wants_cats = ["Shopping", "Entertainment", "Other"]

    needs_spent = float(df_trans[df_trans["category"].isin(needs_cats) & (df_trans["type"] == "expense")]["amount"].sum())
    wants_spent = float(df_trans[df_trans["category"].isin(wants_cats) & (df_trans["type"] == "expense")]["amount"].sum())
    saved_amt = max(0, net_savings)

    total_pie = needs_spent + wants_spent + saved_amt
    if total_pie > 0:
        fig_rule = go.Figure(data=[go.Pie(
            labels=['Needs (Target: 50%)', 'Wants (Target: 30%)', 'Savings (Target: 20%)'],
            values=[needs_spent, wants_spent, saved_amt],
            hole=0.5,
            marker_colors=['#3b82f6', '#f59e0b', '#10b981']
        )])
        fig_rule.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_rule, use_container_width=True)


# ==========================================
# PAGE 5: DATA MANAGEMENT & EXPORT
# ==========================================
elif nav == "📁 Data Management":
    st.title("Data Management & Exports")
    st.caption("Export your ledger in standard formats or filter records.")

    # Export Buttons
    col1, col2 = st.columns(2)
    with col1:
        csv_data = df_trans.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Transactions (CSV)",
            data=csv_data,
            file_name=f"finance_tracker_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        json_copy = df_trans.copy()
        json_copy["date"] = json_copy["date"].dt.strftime("%Y-%m-%d")
        json_str = json_copy.to_json(orient="records", indent=4)
        st.download_button(
            label="📥 Download Transactions (JSON)",
            data=json_str,
            file_name=f"finance_tracker_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Filter Section
    st.subheader("Filter Ledger Records")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        f_type = st.multiselect("Filter by Type", ["income", "expense"], default=["income", "expense"])
    with f_col2:
        all_cats = list(df_trans["category"].unique())
        f_cat = st.multiselect("Filter by Category", all_cats, default=all_cats)

    filtered_df = df_trans[(df_trans["type"].isin(f_type)) & (df_trans["category"].isin(f_cat))].copy()
    filtered_df["Formatted Date"] = filtered_df["date"].dt.strftime("%Y-%m-%d")
    filtered_df["Amount Display"] = filtered_df.apply(lambda r: f"Rs. {r['amount']:,.2f}", axis=1)

    st.dataframe(
        filtered_df[["Formatted Date", "type", "category", "description", "Amount Display"]],
        use_container_width=True,
        hide_index=True
    )