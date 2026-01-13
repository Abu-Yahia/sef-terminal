import streamlit as st
import yfinance as yf
import pandas as pd
import math
from fpdf import FPDF
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="SEF Terminal Pro", page_icon="🛡️", layout="wide")

# --- 1. دالة جلب البيانات الحقيقية (للرادار) ---
def fetch_live_data(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        df = stock.history(period="5d")
        if df.empty: return None, None, "Invalid"
        current_mkt_price = round(df['Close'].iloc[-1], 2)
        long_df = stock.history(period="1mo")
        auto_anchor = round(long_df['Low'].tail(20).min(), 2)
        return current_mkt_price, auto_anchor, "Active"
    except:
        return None, None, "Error"

# --- 2. دالة توليد ملف PDF (بناءً على الأرقام الحالية) ---
def create_pdf_report(content, filename):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="SEF STRATEGIC REPORT", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        for line in content.split('\n'):
            pdf.cell(0, 10, txt=line, ln=True)
        pdf_output = pdf.output(dest='S').encode('latin-1')
        b64 = base64.b64encode(pdf_output).decode()
        return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" style="background-color: #ff4b4b; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">📥 Download PDF Report</a>'
    except:
        return "PDF Error"

# --- 3. واجهة المستخدم ---
st.title("🛡️ SEF Terminal | Professional Hub")

# الحقول الجانبية
balance = st.sidebar.number_input("Portfolio Balance", value=100000)
risk_pct = st.sidebar.slider("Risk per Trade (%)", 0.5, 5.0, 1.0)

# إدارة الذاكرة المؤقتة للرادار
if 'p_val' not in st.session_state: st.session_state['p_val'] = 33.90
if 'a_val' not in st.session_state: st.session_state['a_val'] = 31.72

st.markdown("---")

# صف المدخلات والأزرار (كلهم جنب بعض في سطر واحد)
c1, c2, c3, c4, c5, c6 = st.columns([1.5, 1.2, 1.2, 1.2, 1.2, 1.5])

with c1:
    ticker = st.text_input("Ticker Symbol", "2222.SR").upper()
with c2:
    price = st.number_input("Market Price", value=float(st.session_state['p_val']), step=0.01)
with c3:
    anchor = st.number_input("Anchor Level", value=float(st.session_state['a_val']), step=0.01)
with c4:
    target = st.number_input("Target Price", value=39.36, step=0.01)
with c5:
    st.write("##") # للمحاذاة
    if st.button("🛰️ Radar", use_container_width=True):
        p, a, s = fetch_live_data(ticker)
        if p:
            st.session_state['p_val'] = p
            st.session_state['a_val'] = a
            st.rerun()
with c6:
    st.write("##") # للمحاذاة
    analyze_btn = st.button("📊 Analyze", use_container_width=True)

st.markdown("---")

# --- 4. عرض النتائج والتحليل (التفاعل الحقيقي) ---
if analyze_btn:
    # الحسابات بناءً على ما يراه المستخدم في الخانات حالياً
    risk_per_share = abs(price - anchor)
    risk_cash = balance * (risk_pct / 100)
    
    if risk_per_share > 0:
        rr = (target - price) / risk_per_share
        qty = math.floor(risk_cash / risk_per_share)
    else:
        rr, qty = 0, 0

    # عرض الأرقام الكبيرة (Metrics)
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Live Price", price)
    m_col2.metric("R:R Ratio", f"1:{round(rr, 2)}")
    m_col3.metric("Shares", qty)
    m_col4.metric("Risk Cash", round(risk_cash, 2))

    # بناء نص التقرير للـ PDF وللعرض
    report_text = f"""
SEF STRATEGIC ANALYSIS REPORT
Ticker: {ticker} | Live Price: {price}
------------------------------------
1. Structure:
- Anchor Level: {anchor}
- Target Level: {target}

2. Strategy:
- Risk:Reward: 1:{round(rr, 2)}
- Quantity: {qty} Shares

3. Risk Management:
- Total Risk: {round(risk_cash, 2)} USD/SAR
"Capital preservation is the first priority."
    """

    st.markdown("### 📄 SEF Structural Analysis")
    st.code(report_text, language='text')

    # --- ظهور زر الـ PDF هنا بناءً على التحليل الحالي ---
    pdf_html = create_pdf_report(report_text, f"SEF_{ticker}_Report.pdf")
    st.markdown(pdf_html, unsafe_allow_html=True)

    # الشارت التفاعلي
    st.subheader("📈 Technical Chart")
    hist = yf.Ticker(ticker).history(period="6mo")
    if not hist.empty:
        df_chart = hist[['Close']].copy()
        df_chart['Anchor'] = anchor
        df_chart['Target'] = target
        st.line_chart(df_chart)

    if rr >= 3: st.balloons()
