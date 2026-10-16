import os
import json
from datetime import datetime
import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from features.transactions.transactions import load_transactions

class FinancialReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(30, 41, 59)
        self.cell(0, 8, "FinPulse | Personal Financial Statement", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(100, 116, 139)
        self.cell(0, 5, f"Report Generated: {datetime.now().strftime('%B %d, %Y - %I:%M %p')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(226, 232, 240)
        self.line(10, 24, 200, 24)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} | Confidential Personal Ledger", align="C")

def generate_pdf_report(transactions_df, output_path=None):
    """
    Generates a financial statement PDF.
    If output_path is provided, writes to file.
    Always returns bytes of the generated PDF.
    """
    if transactions_df.empty:
        pdf = FinancialReportPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 10, "No transactions found to export.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf_bytes = bytes(pdf.output())
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)
        return pdf_bytes

    pdf = FinancialReportPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Financial Summary Metrics
    total_income = float(transactions_df[transactions_df["type"] == "income"]["amount"].sum())
    total_expense = float(transactions_df[transactions_df["type"] == "expense"]["amount"].sum())
    net_balance = total_income - total_expense
    savings_rate = (net_balance / total_income * 100) if total_income > 0 else 0.0

    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(203, 213, 225)
    pdf.rect(10, 28, 190, 20, style="FD")

    pdf.set_xy(12, 30)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(45, 4, "TOTAL INCOME", align="C")
    pdf.cell(45, 4, "TOTAL EXPENSES", align="C")
    pdf.cell(50, 4, "NET BALANCE", align="C")
    pdf.cell(45, 4, "SAVINGS RATE", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_xy(12, 36)
    pdf.set_font("Helvetica", "B", 10)
    
    # Income (Green)
    pdf.set_text_color(21, 128, 61)
    pdf.cell(45, 7, f"Rs. {total_income:,.2f}", align="C")
    
    # Expense (Red)
    pdf.set_text_color(185, 28, 28)
    pdf.cell(45, 7, f"Rs. {total_expense:,.2f}", align="C")
    
    # Balance
    if net_balance >= 0:
        pdf.set_text_color(30, 41, 59)
    else:
        pdf.set_text_color(185, 28, 28)
    pdf.cell(50, 7, f"Rs. {net_balance:,.2f}", align="C")
    
    # Savings Rate
    pdf.set_text_color(79, 70, 229)
    pdf.cell(45, 7, f"{savings_rate:.1f}%", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(12)

    # Table Header
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(30, 41, 59)
    pdf.set_text_color(255, 255, 255)

    col_widths = [24, 20, 28, 78, 40]
    headers = ["Date", "Type", "Category", "Description", "Amount"]

    for i, h in enumerate(headers):
        align = "R" if h == "Amount" else "L"
        pdf.cell(col_widths[i], 8, h, border=0, fill=True, align=align)
    pdf.ln(8)

    # Table Rows
    pdf.set_font("Helvetica", "", 8)
    df_sorted = transactions_df.sort_values(by="date", ascending=False)
    
    fill = False
    for _, row in df_sorted.iterrows():
        # Clean text for PDF safe ASCII encoding
        date_str = row["date"].strftime("%Y-%m-%d") if hasattr(row["date"], "strftime") else str(row["date"])[:10]
        t_type = str(row["type"]).capitalize()
        category = str(row["category"])[:15]
        desc = str(row["description"]).encode("ascii", "ignore").decode("ascii")[:45]
        amount_val = float(row["amount"])

        if fill:
            pdf.set_fill_color(248, 250, 252)
        else:
            pdf.set_fill_color(255, 255, 255)

        pdf.set_text_color(51, 65, 85)
        pdf.cell(col_widths[0], 7, date_str, fill=fill)
        pdf.cell(col_widths[1], 7, t_type, fill=fill)
        pdf.cell(col_widths[2], 7, category, fill=fill)
        pdf.cell(col_widths[3], 7, desc, fill=fill)

        # Amount styling
        if str(row["type"]).lower() == "income":
            pdf.set_text_color(21, 128, 61)
            pdf.cell(col_widths[4], 7, f"+ Rs. {amount_val:,.2f}", align="R", fill=fill)
        else:
            pdf.set_text_color(185, 28, 28)
            pdf.cell(col_widths[4], 7, f"- Rs. {amount_val:,.2f}", align="R", fill=fill)

        pdf.ln(7)
        fill = not fill

    pdf_bytes = bytes(pdf.output())

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes

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
    
    df_to_export = transactions_df.copy()
    df_to_export['date'] = df_to_export['date'].dt.strftime('%Y-%m-%d')
    
    df_to_export.to_json(export_path, orient="records", indent=4)
    print(f"✅ Transactions exported successfully to {export_path}")

def export_transactions_to_pdf():
    """Exports all transactions to a PDF file."""
    transactions_df = load_transactions()

    if transactions_df.empty:
        print("No transactions to export.")
        return

    export_path = "export/transactions.pdf"
    generate_pdf_report(transactions_df, output_path=export_path)
    print(f"✅ Transactions exported successfully to {export_path}")