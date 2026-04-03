from fpdf import FPDF
import pandas as pd
import tempfile
import os

def generate_pdf_report(username, month, df):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, "Personal Finance Report", border=False, ln=True, align="C")
    pdf.set_font("Helvetica", "I", 12)
    pdf.cell(0, 10, f"User: {username} | Month: {month}", border=False, ln=True, align="C")
    pdf.ln(10)
    
    # Summary
    total_spent = df['amount'].sum()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, f"Total Spending: Rs. {total_spent:,.2f}", ln=True)
    pdf.ln(5)
    
    # Table Header
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(30, 8, "Date", 1, 0, "C", True)
    pdf.cell(80, 8, "Description", 1, 0, "C", True)
    pdf.cell(40, 8, "Category", 1, 0, "C", True)
    pdf.cell(30, 8, "Amount (Rs)", 1, 1, "C", True)
    
    # Table Rows
    pdf.set_font("Helvetica", "", 10)
    for idx, row in df.iterrows():
        pdf.cell(30, 8, str(row['date'].date()), 1)
        pdf.cell(80, 8, str(row['description'])[:40], 1)
        pdf.cell(40, 8, str(row['category']), 1)
        pdf.cell(30, 8, f"{row['amount']:,.2f}", 1, 1, "R")
    
    # Save to temp file
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"report_{month}.pdf")
    pdf.output(temp_path)
    return temp_path
