import streamlit as st
import yfinance as yf
import pandas as pd
import math
from fpdf import FPDF
import base64

# --- Page Configuration ---
st.set_page_config(page_title="SEF Terminal Pro", page_icon="🛡️", layout="wide")

# --- Function: Generate Professional SEF Report ---
def generate_sef_report(ticker, price, anchor, target, rr, qty, status):
    report_text = f"""
Trend / Structure
-----------------
Trend:
- Daily: Up (Short-term recovery)
- Weekly: Side/Base Forming
- Monthly: Down (Overall structural downtrend remains)
Liquidity Clusters: A Liquidity Void exists above current levels.
POI (Point of Interest): The {anchor} zone is the current accumulation floor.
Time Rule: Waiting for Weekly Close to confirm the hold above {anchor}.
Price Action: Forming a Base at historical support. 
Base Status: Forming.

Key Levels (S/R / POI / Invalidation)
------------------------------------
Support Zones: {anchor} [Strong Anchor].
Resistance Zones: {target} (Primary).
Anchor Level (Smart Money): {anchor}.
Invalidation: Close < {anchor} on a Weekly basis.

Scenarios
---------
Bullish: Trigger at {price} followed by a break of descending trendline.
Bearish: Failure to hold {anchor} leading to panic sell.

Trade Playbook
--------------
Entry: {price} | Stop: {anchor} | Target: {target}
R:R Ratio: 1:{round(rr, 2)} | Quantity: {qty}
Confidence: 4/5

Risk Management Reminder:
"إحنا بنغوص معهم لكن هم معهم أنبوبة أكسجين — نفسهم طويل. إحنا بنغرق يا وديع."
    """
    return report_text

# --- Function: Create PDF with Professional Layout ---
class SEF_PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'SEF STRATEGIC ANALYSIS REPORT', 0, 1, 'C')
        self.ln(5)

def download_pdf(content, filename):
    pdf = SEF_PDF()
    pdf.add_page()
    pdf.set_font("Courier", size=10)
    for line in content.split('\n'):
        pdf.cell(0, 8, txt=line, ln=True)
    pdf_output = pdf.output(dest='S').encode('latin-1')
    b64 = base64.b64encode(pdf_output).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" style="background-color: #ff4b4b; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">📥 Download Full SEF Report (PDF)</a>'

# --- Main Engine ---
st.title("🛡️ SEF Terminal | Structural Analysis")

ticker = st.sidebar.text_input("Ticker Symbol", "4009.SR")
balance = st.sidebar.number_input("Portfolio Balance", value=100000)
risk_pct = st.sidebar.slider("Risk (%)", 0.5, 5.0, 1.0)

col1, col2, col3 = st.columns(3)
with col1:
    price_input = st.number_input("Current Price", value=33.90)
with col2:
    anchor_input = st.number_input("Anchor Level", value=31.72)
with col3:
    target_input = st.number_input("Target 1", value=39.36)

if st.button("Generate SEF Structural Report"):
    # Calculations
    risk_per_share = abs(price_input - anchor_input)
    rr = (target_input - price_input) / risk_per_share if risk_per_share > 0 else 0
    qty = math.floor((balance * (risk_pct/100)) / risk_per_share) if risk_per_share > 0 else 0
    
    # Generate Report Text
    full_report = generate_sef_report(ticker, price_input, anchor_input, target_input, rr, qty, "Forming")
    
    # Visual Display
    st.markdown("### 📄 SEF Executive Summary")
    st.code(full_report, language='text')
    
    # PDF Download
    st.markdown(download_pdf(full_report, f"SEF_Report_{ticker}.pdf"), unsafe_allow_html=True)

    # Mini Footer Info
    st.info(f"SEF_UPDATE | Ticker={ticker} | Exec=PREPARE | RR=1:{round(rr,1)} | Inval={anchor_input}")
