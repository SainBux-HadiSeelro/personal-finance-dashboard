import os
import questionary
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import pandas as pd

DATABASE_FILE = "database/transactions.txt"

def load_transactions():
    """Loads transactions from the database file into a pandas DataFrame."""
    try:
        df = pd.read_csv(DATABASE_FILE, header=None, names=["date", "type", "category", "amount_paisa", "description"])
        df["amount"] = df["amount_paisa"] / 100
        df["date"] = pd.to_datetime(df["date"])
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=["date", "type", "category", "amount_paisa", "description", "amount"])

def save_transaction(date, transaction_type, category, amount_paisa, description):
    """Saves a transaction to the database file."""
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
    with open(DATABASE_FILE, "a", encoding="utf-8") as f:
        f.write(f"{date},{transaction_type},{category},{amount_paisa},{description}\n")

def _validate_amount(text):
    try:
        val = float(text)
        return True if val > 0 else "Amount must be greater than zero."
    except ValueError:
        return "Please enter a valid numeric amount."

def _validate_date(text):
    try:
        datetime.strptime(text, "%Y-%m-%d")
        return True
    except ValueError:
        return "Date must be in YYYY-MM-DD format."

def add_expense():
    """Adds an expense transaction."""
    amount_str = questionary.text(
        "Enter the expense amount:",
        validate=_validate_amount
    ).ask()
    if amount_str is None:
        return

    amount_paisa = round(float(amount_str) * 100)

    category = questionary.select(
        "Select an expense category:",
        choices=["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"],
    ).ask()
    if category is None:
        return

    description = questionary.text("Enter a description:").ask()
    if description is None:
        return

    date_str = questionary.text(
        "Enter the date (YYYY-MM-DD) or press Enter for today:",
        default=datetime.now().strftime("%Y-%m-%d"),
        validate=_validate_date
    ).ask()
    if date_str is None:
        return

    save_transaction(date_str, "expense", category, amount_paisa, description)
    print("✅ Expense added successfully!")

def add_income():
    """Adds an income transaction."""
    amount_str = questionary.text(
        "Enter the income amount:",
        validate=_validate_amount
    ).ask()
    if amount_str is None:
        return

    amount_paisa = round(float(amount_str) * 100)

    category = questionary.select(
        "Select an income source:",
        choices=["Salary", "Freelance", "Business", "Investment", "Gift", "Other"],
    ).ask()
    if category is None:
        return

    description = questionary.text("Enter a description:").ask()
    if description is None:
        return

    date_str = questionary.text(
        "Enter the date (YYYY-MM-DD) or press Enter for today:",
        default=datetime.now().strftime("%Y-%m-%d"),
        validate=_validate_date
    ).ask()
    if date_str is None:
        return

    save_transaction(date_str, "income", category, amount_paisa, description)
    print("✅ Income added successfully!")

def list_transactions():
    """Lists all transactions in a table."""
    transactions_df = load_transactions()

    if transactions_df.empty:
        print("No transactions found.")
        return

    table = Table(title="All Transactions")
    table.add_column("Date", justify="right", style="cyan", no_wrap=True)
    table.add_column("Type", justify="center", style="magenta")
    table.add_column("Category", justify="left", style="green")
    table.add_column("Description", justify="left", style="white")
    table.add_column("Amount", justify="right", style="yellow")

    transactions_df = transactions_df.sort_values(by="date", ascending=False)

    for index, row in transactions_df.iterrows():
        amount_style = "bold red" if row["type"] == "expense" else "bold green"
        table.add_row(
            row["date"].strftime("%Y-%m-%d"),
            str(row["type"]),
            str(row["category"]),
            str(row["description"]),
            f"[{amount_style}]Rs. {row['amount']:,.2f}[/]",
        )

    console = Console()
    console.print(table)

def show_balance():
    """Shows the balance for the current month."""
    transactions_df = load_transactions()

    if transactions_df.empty:
        print("No transactions found.")
        return

    current_month = datetime.now().month
    current_year = datetime.now().year

    monthly_df = transactions_df[
        (transactions_df['date'].dt.month == current_month) &
        (transactions_df['date'].dt.year == current_year)
    ]

    total_income = monthly_df[monthly_df["type"] == "income"]["amount"].sum()
    total_expenses = monthly_df[monthly_df["type"] == "expense"]["amount"].sum()
    balance = total_income - total_expenses

    balance_text = (
        f"[bold green]Total Income: Rs. {total_income:,.2f}[/bold green]\n"
        f"[bold red]Total Expenses: Rs. {total_expenses:,.2f}[/bold red]\n"
        f"[bold {'green' if balance >= 0 else 'red'}]Balance: Rs. {balance:,.2f}[/bold {'green' if balance >= 0 else 'red'}]"
    )

    panel = Panel.fit(
        balance_text,
        title=f"Balance for {datetime.now().strftime('%B %Y')}"
    )

    console = Console()
    console.print(panel)
