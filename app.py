import streamlit as st
import yfinance as yf
import pandas as pd
import math
from fpdf import FPDF
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="SEF Terminal Pro", page_icon="🛡️", layout="wide")

# --- 1. دالة جلب البيانات (الرادار) ---
def fetch_live_data(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        df = stock.history(period="5d")
        if df.empty: return None, None
        current_mkt_price = round(df['Close'].iloc[-1], 2)
        long_df = stock.history(period="1mo")
        auto_anchor = round(long_df['Low'].tail(20).min(), 2)
        return current_mkt_price, auto_anchor
    except:
        return None, None

# --- 2. دالة توليد الـ PDF ---
def generate_pdf_link(content, ticker):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="SEF STRATEGIC ANALYSIS", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", size=11)
        for line in content.split('\n'):
            pdf.cell(0, 8, txt=line, ln=True)
        pdf_output = pdf.output(dest='S').encode('latin-1')
        b64 = base64.b64encode(pdf_output).decode()
        return f'<a href="data:application/octet-stream;base64,{b64}" download="SEF_{ticker}_Report.pdf" style="background-color: #ff4b4b; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block; margin-top: 10px;">📥 Download PDF Report</a>'
    except:
        return "⚠️ PDF Generation Error"

# --- 3. واجهة المستخدم ---
st.title("🛡️ SEF Terminal | Ultimate Hub")

balance = st.sidebar.number_input("Portfolio Balance", value=100000)
risk_pct = st.sidebar.slider("Risk per Trade (%)", 0.5, 5.0, 1.0)

if 'p_now' not in st.session_state: st.session_state['p_now'] = 33.90
if 'a_now' not in st.session_state: st.session_state['a_now'] = 31.72

st.markdown("---")

# صف المدخلات والأزرار
c1, c2, c3, c4, c5, c6 = st.columns([1.5, 1.2, 1.2, 1.2, 1.2, 1.5])

with c1:
    ticker = st.text_input("Ticker Symbol", "2222.SR").upper()
with c2:
    p_in = st.number_input("Market Price", value=float(st.session_state['p_now']), step=0.01)
with c3:
    a_in = st.number_input("Anchor Level", value=float(st.session_state['a_now']), step=0.01)
with c4:
    t_in = st.number_input("Target Price", value=39.36, step=0.01)
with c5:
    st.write("##")
    if st.button("🛰️ Radar", use_container_width=True):
        p, a = fetch_live_data(ticker)
        if p:
            st.session_state['p_now'] = p
            st.session_state['a_now'] = a
            st.rerun()
with c6:
    st.write("##")
    analyze_trigger = st.button("📊 Analyze", use_container_width=True)

st.markdown("---")

# --- 4. التحليل والنتائج والتقييم ---
if analyze_trigger:
    risk_per_share = abs(p_in - a_in)
    risk_cash = balance * (risk_pct / 100)
    
    if risk_per_share > 0:
        rr = (t_in - p_in) / risk_per_share
        qty = math.floor(risk_cash / risk_per_share)
    else:
        rr, qty = 0, 0

    # --- منطق تقييم العائد إلى المخاطرة ---
    if rr >= 3:
        rr_advice = "🟢 EXCELLENT (Professional Grade)"
    elif 2 <= rr < 3:
        rr_advice = "🟡 GOOD (Acceptable Trade)"
    elif 1 <= rr < 2:
        rr_advice = "🟠 POOR (High Risk / Low Reward)"
    else:
        rr_advice = "🔴 DANGEROUS (Avoid - Statistical Suicide)"

    # عرض المتريكس
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Live Price", p_in)
    m2.metric("R:R Ratio", f"1:{round(rr, 2)}")
    m3.metric("Shares", qty)
    m4.metric("Risk Cash", f"{round(risk_cash, 2)}")

    # بناء التقرير
    full_report = f"""
SEF STRATEGIC ANALYSIS REPORT
Ticker: {ticker} | Price: {p_in}
------------------------------------
1. STRUCTURAL LEVELS:
- Entry Price: {p_in}
- Anchor (Stop Loss): {a_in}
- Target Level: {t_in}

2. EXECUTION METRICS:
- Risk:Reward Ratio: 1:{round(rr, 2)}
- Quantity to Buy: {qty} Shares

3. RISK MANAGEMENT:
- Total Risk Amount: {round(risk_cash, 2)}
"Capital preservation is the first priority."

RESULT: {rr_advice}
    """

    st.markdown("### 📄 SEF Structural Analysis")
    st.code(full_report, language='text')

    # زر الـ PDF
    st.markdown(generate_pdf_link(full_report, ticker), unsafe_allow_html=True)

    # الشارت
    hist = yf.Ticker(ticker).history(period="6mo")
    if not hist.empty:
        c_data = hist[['Close']].copy()
        c_data['Anchor'] = a_in
        c_data['Target'] = t_in
        st.line_chart(c_data)

    if rr >= 3: st.balloons()
