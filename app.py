import streamlit as st
import yfinance as yf
import pandas as pd
import math
from fpdf import FPDF
import base64

# --- Page Configuration ---
st.set_page_config(page_title="SEF Terminal Pro", page_icon="🛡️", layout="wide")

# --- Helper Function: PDF Report Generation ---
def create_download_link(ticker, price, anchor, target, rr, qty, status):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Title
    pdf.cell(200, 10, txt="SEF Terminal - Trade Executive Summary", ln=True, align='C')
    pdf.ln(10)
    
    # Content
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Ticker Symbol: {ticker}", ln=True)
    pdf.cell(200, 10, txt=f"Market Price: {price}", ln=True)
    pdf.cell(200, 10, txt=f"Anchor Level (SL): {anchor}", ln=True)
    pdf.cell(200, 10, txt=f"Target Price: {target}", ln=True)
    pdf.cell(200, 10, txt=f"Risk:Reward Ratio: 1:{round(rr, 2)}", ln=True)
    pdf.cell(200, 10, txt=f"Suggested Quantity: {qty} shares", ln=True)
    pdf.cell(200, 10, txt=f"Market Status: {status}", ln=True)
    
    # Recommendation
    pdf.ln(10)
    recommendation = "APPROVED" if rr >= 3 else "REJECTED (High Risk)"
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"Final Decision: {recommendation}", ln=True)
    
    # Convert PDF to bytes
    pdf_output = pdf.output(dest='S').encode('latin-1')
    b64 = base64.b64encode(pdf_output).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="SEF_{ticker}_Report.pdf">📥 Click here to Download Report</a>'

# --- Technical Analysis Engine ---
def get_technical_levels(ticker):
    try:
        data = yf.Ticker(ticker).history(period="6mo")
        if data.empty: return None, None, None, None
        
        # 1. Identify Support (Anchor) & Resistance
        recent_20 = data.tail(20)
        resistance = recent_20['High'].max()
        support = recent_20['Low'].min()
        
        # 2. Institutional Average (EMA 200)
        ema_200 = data['Close'].ewm(span=200, adjust=False).mean().iloc[-
