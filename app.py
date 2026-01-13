import streamlit as st
import yfinance as yf
import pandas as pd
import math
from fpdf import FPDF
import base64

# --- Page Configuration ---
st.set_page_config(page_title="SEF Terminal Pro", page_icon="🛡️", layout="wide")

# --- 1. Functions ---
def get_radar_data(ticker):
    try:
        data = yf.Ticker(ticker).history(period="1y")
        if data.empty: return None, None, "Invalid"
        # التقاط آخر سعر وإغلاق
        last_price = round(data['Close'].iloc[-1], 2)
        support = round(data['Low'].tail(20).min(), 2)
        status = "🛡️ Near Anchor" if last_price < support * 1.05 else "🔥 Breakout"
        return last_price, support, status
    except:
        return None, None, "Error"

def generate_sef_full_text(ticker, price, anchor, target, rr, qty, status):
    return f"""
SEF STRATEGIC ANALYSIS REPORT
Ticker: {ticker} | Price: {price}

1. Trend / Structure: {status}
2. Anchor Level (SL): {anchor}
3. Primary Target: {target}
4. Risk:Reward: 1:{round(rr, 2)}
5. Recommended Qty: {qty} Shares

"Capital preservation is the first priority."
    """

def download_pdf(content, filename):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        clean_content = content.encode('ascii', 'ignore').decode('ascii')
        for line in clean_content.split('\n'):
            pdf.cell(0, 8, txt=line, ln=True)
        pdf_output = pdf.output(dest='S').encode('latin-1')
        b64 = base64.b64encode(pdf_output).decode()
        return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" style="background-color: #ff4b4b; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">📥 PDF Report</a>'
    except: return "Error"

# --- 2. UI Layout ---
st.title("🛡️ SEF Terminal | Professional Hub")

# Sidebar
balance = st.sidebar.number_input("Portfolio Balance", value=100000)
risk_pct = st.sidebar.slider("Risk per Trade (%)", 0.5, 5.0, 1.0)

# Initialize Session States if not exist
if 'price_val' not in st.session_state: st.session_state['price_val'] = 33.90
if 'anchor_val' not in st.session_state: st.session_state['anchor_val'] = 31.72
if 'status_val' not in st.session_state: st.session_state['status_val'] = "Forming"

st.markdown("---")

# --- ROW 1: Inputs & Buttons ---
c1, c2, c3, c4, c5, c6 = st.columns([1.5, 1.2, 1.2, 1.2, 1.2, 1.5])

with c1:
    ticker = st.text_input("Ticker", "4009.SR").upper()
with c2:
    # ربط الخانة بـ session_state مباشرة
    curr_p = st.number_input("Price", value=st.session_state['price_val'], key="p_input")
with c3:
    anc_p = st.number_input("Anchor", value=st.session_state['anchor_val'], key="a_input")
with c4:
    tar_p = st.number_input("Target", value=39.36)
with c5:
    st.write("##")
    if st.button("🛰️ Radar", use_container_width=True):
        new_price, new_support, new_status = get_radar_data(ticker)
        if new_price:
            # تحديث القيم في الـ State
            st.session_state['price_val'] = new_price
            st.session_state['anchor_val'] = new_support
            st.session_state['status_val'] = new_status
            st.rerun() # إعادة التشغيل لتحديث الأرقام في الخانات
with c6:
    st.write("##")
    run_btn = st.button("📊 Analyze", use_container_width=True)

st.markdown("---")

# --- 3. Results ---
if run_btn:
    # استخدام القيم الحالية من الخانات
    risk_s = abs(st.session_state.p_input - st.session_state.a_input)
    rr = (tar_p - st.session_state.p_input) / risk_s if risk_s > 0 else 0
    qty = math.floor((balance * (risk_pct/100)) / risk_s) if risk_s > 0 else 0
    
    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Current Price", st.session_state.p_input)
    m2.metric("R:R Ratio", f"1:{round(rr, 2)}")
    m3.metric("Shares", qty)
    m4.metric("Risk Cash", round(balance * (risk_pct/100), 2))

    # Report
    st.markdown("---")
    report = generate_sef_full_text(ticker, st.session_state.p_input, st.session_state.a_input, tar_p, rr, qty, st.session_state['status_val'])
    st.code(report, language='text')
    st.markdown(download_pdf(report, f"SEF_{ticker}.pdf"), unsafe_allow_html=True)

    # Chart
    hist = yf.Ticker(ticker).history(period="6mo")
    if not hist.empty:
        chart_df = hist[['Close']].copy()
        chart_df['Anchor'] = st.session_state.a_input
        chart_df['Target'] = tar_p
        st.line_chart(chart_df)
    
    if rr >= 3: st.balloons()
