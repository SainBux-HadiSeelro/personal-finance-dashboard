import sys

# Configure UTF-8 encoding for Windows terminals to support Unicode and emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import questionary
from features.transactions.transactions import add_expense, add_income, list_transactions, show_balance
from features.budgets.budgets import set_budget, view_budgets
from features.analytics.analytics import spending_analysis
from features.smart_assistant.smart_assistant import daily_financial_check
from features.data_management.data_management import export_transactions_to_csv, export_transactions_to_json, export_transactions_to_pdf

def main():
    """Main function to run the personal finance tracker CLI."""
    while True:
        choice = questionary.select(
            "What do you want to do?",
            choices=[
                "Daily Financial Check",
                "Add Expense",
                "Add Income",
                "Show Balance",
                "Set Budget",
                "View Budgets",
                "Show Transactions",
                "Financial Analytics",
                "Data Management",
                "Exit",
            ],
        ).ask()

        if choice == "Daily Financial Check":
            daily_financial_check()
        elif choice == "Add Expense":
            add_expense()
        elif choice == "Add Income":
            add_income()
        elif choice == "Show Balance":
            show_balance()
        elif choice == "Set Budget":
            set_budget()
        elif choice == "View Budgets":
            view_budgets()
        elif choice == "Show Transactions":
            list_transactions()
        elif choice == "Financial Analytics":
            spending_analysis()
        elif choice == "Data Management":
            data_management_menu()
        elif choice == "Exit" or choice is None:
            break

def data_management_menu():
    """Shows the data management sub-menu."""
    choice = questionary.select(
        "Data Management Options:",
        choices=[
            "Export Transactions to CSV",
            "Export Transactions to JSON",
            "Export Transactions to PDF",
            "Back",
        ],
    ).ask()

    if choice == "Export Transactions to CSV":
        export_transactions_to_csv()
    elif choice == "Export Transactions to JSON":
        export_transactions_to_json()
    elif choice == "Export Transactions to PDF":
        export_transactions_to_pdf()
    elif choice == "Back" or choice is None:
        return

if __name__ == "__main__":
    main()