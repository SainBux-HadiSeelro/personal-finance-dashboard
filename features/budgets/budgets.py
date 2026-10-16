import os
import questionary
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress_bar import ProgressBar
from datetime import datetime
from features.transactions.transactions import load_transactions

BUDGET_FILE = "database/budgets.txt"

def load_budgets():
    """Loads budgets from the database file into a pandas DataFrame."""
    try:
        df = pd.read_csv(BUDGET_FILE, header=None, names=["category", "amount_paisa"])
        df["amount"] = df["amount_paisa"] / 100
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=["category", "amount_paisa", "amount"])

def save_budgets(budgets_df):
    """Saves the budgets DataFrame to the database file."""
    os.makedirs(os.path.dirname(BUDGET_FILE), exist_ok=True)
    df_to_save = budgets_df.copy()
    df_to_save["amount_paisa"] = df_to_save["amount_paisa"].astype(int)
    df_to_save[["category", "amount_paisa"]].to_csv(BUDGET_FILE, header=False, index=False)

def _validate_budget_amount(text):
    try:
        val = float(text)
        return True if val > 0 else "Budget must be greater than zero."
    except ValueError:
        return "Please enter a valid numeric amount."

def set_budget():
    """Sets a budget for a specific expense category."""
    category = questionary.select(
        "Select a category to set a budget for:",
        choices=["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"],
    ).ask()
    if category is None:
        return

    amount_str = questionary.text(
        f"Enter the budget amount for {category}:",
        validate=_validate_budget_amount
    ).ask()
    if amount_str is None:
        return

    amount_paisa = round(float(amount_str) * 100)

    budgets_df = load_budgets()

    if category in budgets_df["category"].values:
        budgets_df.loc[budgets_df["category"] == category, "amount_paisa"] = amount_paisa
    else:
        new_budget = pd.DataFrame([{"category": category, "amount_paisa": amount_paisa}])
        budgets_df = pd.concat([budgets_df, new_budget], ignore_index=True)

    save_budgets(budgets_df)
    print(f"✅ Budget for {category} set to Rs. {float(amount_str):,.2f}.")

def view_budgets():
    """Displays the budget status for all categories."""
    budgets_df = load_budgets()
    transactions_df = load_transactions()

    if budgets_df.empty:
        print("No budgets set. Please set a budget first.")
        return

    table = Table(title="Budget Status")
    table.add_column("Category", justify="left", style="cyan")
    table.add_column("Budget", justify="right", style="magenta")
    table.add_column("Spent", justify="right", style="green")
    table.add_column("Remaining", justify="right", style="yellow")
    table.add_column("% Spent", justify="center")

    current_month = datetime.now().month
    current_year = datetime.now().year

    for index, row in budgets_df.iterrows():
        category = str(row["category"])
        budget_amount = float(row["amount"])

        monthly_expenses = transactions_df[
            (transactions_df['date'].dt.month == current_month) &
            (transactions_df['date'].dt.year == current_year) &
            (transactions_df['type'] == 'expense') &
            (transactions_df['category'] == category)
        ]
        spent_amount = float(monthly_expenses['amount'].sum())
        remaining_amount = budget_amount - spent_amount
        percent_spent = (spent_amount / budget_amount) * 100 if budget_amount > 0 else 0

        # Progress bar color
        if percent_spent < 70:
            progress_style = "green"
        elif 70 <= percent_spent < 100:
            progress_style = "yellow"
        else:
            progress_style = "red"

        progress_bar = ProgressBar(total=100, completed=min(percent_spent, 100), width=30, style=progress_style)

        table.add_row(
            category,
            f"Rs. {budget_amount:,.2f}",
            f"Rs. {spent_amount:,.2f}",
            f"Rs. {remaining_amount:,.2f}",
            progress_bar,
        )

    console = Console()
    console.print(table)