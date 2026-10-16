import pandas as pd
from rich.console import Console
from rich.table import Table
from datetime import datetime
from features.transactions.transactions import load_transactions

def spending_analysis():
    """Analyzes and displays spending patterns for the current month."""
    transactions_df = load_transactions()
    
    if transactions_df.empty:
        print("No transactions found.")
        return

    current_month = datetime.now().month
    current_year = datetime.now().year

    monthly_expenses = transactions_df[
        (transactions_df['date'].dt.month == current_month) &
        (transactions_df['date'].dt.year == current_year) &
        (transactions_df['type'] == 'expense')
    ]

    if monthly_expenses.empty:
        print("No expenses found for the current month.")
        return

    # Spending breakdown by category
    spending_by_category = monthly_expenses.groupby('category')['amount'].sum().reset_index()
    spending_by_category = spending_by_category.sort_values(by='amount', ascending=False)

    table = Table(title=f"Spending Breakdown for {datetime.now().strftime('%B %Y')}")
    table.add_column("Category", justify="left", style="cyan")
    table.add_column("Amount", justify="right", style="magenta")
    table.add_column("% of Total", justify="right", style="green")

    total_spent = spending_by_category['amount'].sum()

    for index, row in spending_by_category.iterrows():
        percentage = (row['amount'] / total_spent) * 100
        table.add_row(
            str(row['category']),
            f"Rs. {row['amount']:,.2f}",
            f"{percentage:.2f}%"
        )
    
    console = Console()
    console.print(table)

    # Top 3 spending categories
    top_3_categories = spending_by_category.head(3)

    top_3_table = Table(title="Top 3 Spending Categories")
    top_3_table.add_column("Category", justify="left", style="cyan")
    top_3_table.add_column("Amount", justify="right", style="magenta")

    for index, row in top_3_categories.iterrows():
        top_3_table.add_row(
            str(row['category']),
            f"Rs. {row['amount']:,.2f}"
        )
    
    console.print(top_3_table)
