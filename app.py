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
    try:
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
        return f'<a href="data:application/octet-stream;base64,{b64}" download="SEF_{ticker}_Report.pdf" style="color: #4CAF50; text-decoration: none; font-weight: bold;">📥 Download Official PDF Report</a>'
    except Exception as e:
        return f"Error generating report: {str(e)}"

# --- Technical Analysis Engine ---
def get_technical_levels(ticker):
    try:
        data = yf.Ticker(ticker).history(period="1y")
        if data.empty: return None, None, None, None
        
        # 1. Identify Support (Anchor) & Resistance
        recent_20 = data.tail(20)
        resistance = recent_20['High'].max()
        support = recent_20['Low'].min()
        
        # 2. Institutional Average (EMA 200)
        ema_200 = data['Close'].ewm(span=200, adjust=False).mean().iloc[-1]
        
        # 3. Market Status Detection
        last_close = data['Close'].iloc[-1]
        status = "Neutral"
        if last_close > resistance * 0.98: status = "🔥 Potential Breakout"
        elif last_close < support * 1.05: status = "🛡️ Near Anchor Zone"
        
        return round(support, 2), round(resistance, 2), round(ema_200, 2), status
    except:
        return None, None, None, None

# --- Main Interface ---
st.title("🛡️ SEF Terminal | Professional Risk Management")
st.markdown("---")

st.sidebar.header("⚙️ Portfolio Configuration")
balance = st.sidebar.number_input("Total Trading Capital", value=100000, step=1000)
risk_pct = st.sidebar.slider("Risk Tolerance per Trade (%)", 0.5, 5.0, 1.0)

# --- Input Section ---
col1, col2, col3 = st.columns(3)
with col1:
    ticker_input = st.text_input("Ticker Symbol (e.g., 2222.SR, AAPL)", "4009.SR").upper()
    if st.button("Run Technical Radar 🛰️"):
        sup, res, ema, stat = get_technical_levels(ticker_input)
        if sup:
            st.session_state['anchor_point'] = sup
            st.session_state['market_status'] = stat
            st.success(f"Radar Findings: Support @ {sup} | Resistance @ {res}")
        else:
            st.error("Data fetch failed. Check symbol format.")

with col2:
    default_anchor = st.session_state.get('anchor_point', 31.72)
    anchor_level = st.number_input("Anchor Level (Stop Loss)", value=float(default_anchor), format="%.2f")
with col3:
    target_price = st.number_input("Profit Target Price", value=39.36, format="%.2f")

st.markdown("---")

# --- Analysis Execution ---
if st.button("Execute Strategic Analysis"):
    data = yf.Ticker(ticker_input).history(period="6mo")
    if not data.empty:
        current_price = round(data['Close'].iloc[-1], 2)
        
        # SEF Core Logic Calculations
        risk_per_share = abs(current_price - anchor_level)
        reward_per_share = abs(target_price - current_price)
        rr_ratio = reward_per_share / risk_per_share if risk_per_share > 0 else 0
        
        risk_capital = balance * (risk_pct / 100)
        share_quantity = math.floor(risk_capital / risk_per_share) if risk_per_share > 0 else 0
        investment_total = share_quantity * current_price
        
        # Displaying Real-time Metrics
        current_status = st.session_state.get('market_status', 'Analyzed')
        st.subheader(f"Strategy Insights: {current_status}")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Current Market Price", f"{current_price}")
        m2.metric("Risk:Reward Ratio", f"1:{round(rr_ratio, 2)}")
        m3.metric("Position Size (Qty)", f"{share_quantity}")
        m4.metric("Risk Amount (Cash)", f"{round(risk_capital, 2)}")

        # --- Chart Visualizer ---
        st.subheader("Technical Chart Visualizer")
        chart_df = data[['Close']].copy()
        chart_df['Anchor'] = anchor_level
        chart_df['Target'] = target_price
        st.line_chart(chart_df)
        
        # --- Decision Branding ---
        if rr_ratio >= 3.0:
            st.balloons()
            st.success("🎯 SEF GOLDEN RATIO MET: This trade aligns with institutional standards.")
        else:
            st.warning("⚠️ RISK WARNING: Reward-to-Risk ratio is below the 1:3 institutional requirement.")
            
        # PDF Report Generator
        st.markdown("### Reporting")
        report_html = create_download_link(ticker_input, current_price, anchor_level, target_price, rr_ratio, share_quantity, current_status)
        st.markdown(report_html, unsafe_allow_html=True)
    else:
        st.error("Invalid Ticker. Use '.SR' for Saudi stocks.")
