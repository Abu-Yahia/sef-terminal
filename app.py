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
st.title("🛡️ SEF Terminal | Technical Radar")

st.sidebar.header("⚙️ Portfolio Settings")
balance = st.sidebar.number_input("Total Account Balance", value=100000)
risk_pct = st.sidebar.slider("Risk per Trade (%)", 0.5, 5.0, 1.0)

# --- Input Section ---
col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input("Ticker Symbol (e.g., 2222.SR or TSLA)", "4009.SR")
    if st.button("Activate Auto-Radar 🛰️"):
        sup, res, ema, stat = get_technical_levels(ticker)
        if sup:
            st.session_state['anchor_point'] = sup
            st.session_state['market_status'] = stat
            st.info(f"Radar Detected: Support (Anchor) at {sup} | Resistance at {res}")
        else:
            st.error("Failed to fetch data. Please check the ticker.")

with col2:
    default_anchor = st.session_state.get('anchor_point', 31.72)
    anchor_level = st.number_input("Anchor Level (Stop Loss)", value=float(default_anchor))
with col3:
    target_price = st.number_input("Target Price", value=39.36)

# --- Execution & Analysis ---
if st.button("Analyze Trade & Show Chart"):
    data = yf.Ticker(ticker).history(period="6mo")
    if not data.empty:
        current_price = round(data['Close'].iloc[-1], 2)
        
        # Calculations
        risk_per_share = abs(current_price - anchor_level)
        reward_per_share = abs(target_price - current_price)
        rr_ratio = reward_per_share / risk_per_share if risk_per_share > 0 else 0
        
        risk_amount = balance * (risk_pct / 100)
        quantity = math.floor(risk_amount / risk_per_share) if risk_per_share > 0 else 0
        total_investment = quantity * current_price
        
        # Display Results
        current_status = st.session_state.get('market_status', 'Analyzed')
        st.markdown(f"### Market Status: {current_status}")
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Current Price", f"{current_price}")
        k2.metric("Risk:Reward", f"1:{round(rr_ratio, 2)}")
        k3.metric("Shares to Buy", f"{quantity}")
        k4.metric("Risk Amount", f"{round(risk_amount, 2)}")

        # --- Visual Charting ---
        st.subheader("Technical Chart Analysis")
        chart_data = data[['Close']].copy()
        chart_data['Anchor'] = anchor_level
        chart_data['Target'] = target_price
        st.line_chart(chart_data)
        
        # --- PDF Report Link ---
        st.markdown("---")
        if rr_ratio >= 3.0:
            st.success(f"🎯 SEF Standard Met! Excellent Opportunity.")
        
        # PDF Generator Button
        report_link = create_download_link(ticker, current_price, anchor_level, target_price, rr_ratio, quantity, current_status)
        st.markdown(report_link, unsafe_allow_html=True)
    else:
        st.error("Invalid Ticker Symbol.")
