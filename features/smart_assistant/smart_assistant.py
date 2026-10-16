from datetime import datetime
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from features.transactions.transactions import load_transactions
from features.budgets.budgets import load_budgets

def daily_financial_check():
    """Provides a daily financial check-up with spending, alerts, and tips."""
    console = Console()
    
    transactions_df = load_transactions()
    budgets_df = load_budgets()

    today = datetime.now().date()
    
    # Today's Spending
    todays_spending = transactions_df[
        (transactions_df['date'].dt.date == today) &
        (transactions_df['type'] == 'expense')
    ]['amount'].sum()

    # Budget Alerts
    alerts = []
    if not budgets_df.empty:
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        for index, row in budgets_df.iterrows():
            category = row["category"]
            budget_amount = row["amount"]

            monthly_expenses = transactions_df[
                (transactions_df['date'].dt.month == current_month) &
                (transactions_df['date'].dt.year == current_year) &
                (transactions_df['type'] == 'expense') &
                (transactions_df['category'] == category)
            ]
            spent_amount = monthly_expenses['amount'].sum()
            percent_spent = (spent_amount / budget_amount) * 100 if budget_amount > 0 else 0

            if percent_spent > 80:
                alerts.append(f"⚠️  [bold yellow]Budget Alert:[/bold yellow] You have spent {percent_spent:.0f}% of your {category} budget.")

    # Quick Tip
    tip = "💡 [bold cyan]Quick Tip:[/bold cyan] Review your spending from yesterday to see if you can save more today."

    # Display
    display_text = f"📊 [bold]Daily Financial Check ({today.strftime('%B %d, %Y')})[/bold]\n\n"
    display_text += f"Today's Spending: [bold {'red' if todays_spending > 0 else 'green'}]Rs. {todays_spending:,.2f}[/]\n\n"
    
    if alerts:
        display_text += "\n".join(alerts) + "\n\n"
    
    display_text += tip

    panel = Panel.fit(
        display_text,
        title="Smart Financial Assistant"
    )
    
    console.print(panel)
