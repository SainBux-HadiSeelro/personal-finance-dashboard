import os
import pandas as pd
from features.transactions.transactions import load_transactions
import json

def export_transactions_to_csv():
    """Exports all transactions to a CSV file."""
    transactions_df = load_transactions()

    if transactions_df.empty:
        print("No transactions to export.")
        return

    export_path = "export/transactions.csv"
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    transactions_df.to_csv(export_path, index=False)
    print(f"✅ Transactions exported successfully to {export_path}")

def export_transactions_to_json():
    """Exports all transactions to a JSON file."""
    transactions_df = load_transactions()

    if transactions_df.empty:
        print("No transactions to export.")
        return

    export_path = "export/transactions.json"
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    
    # Convert date to string for JSON serialization
    df_to_export = transactions_df.copy()
    df_to_export['date'] = df_to_export['date'].dt.strftime('%Y-%m-%d')
    
    df_to_export.to_json(export_path, orient="records", indent=4)
    print(f"✅ Transactions exported successfully to {export_path}")