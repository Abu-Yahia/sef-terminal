import streamlit as st
import yfinance as yf
import pandas as pd
import math
from fpdf import FPDF
import base64

# --- 1. إعدادات الصفحة ---
icon_url = "https://i.ibb.co/vzR0jXJX/robot-icon.png"
st.set_page_config(page_title="SEF Terminal Pro", page_icon=icon_url, layout="wide")

# --- 2. قاعدة بيانات أسهم تاسي (الرمز والاسم) ---
# يمكنك إضافة أي سهم هنا مستقبلاً باتباع نفس التنسيق
tasi_data = {
    "4009.SR": "Saudi German Health | الألماني",
    "1120.SR": "Al Rajhi Bank | الراجحي",
    "2222.SR": "Saudi Aramco | أرامكو",
    "1150.SR": "Alinma Bank | الإنماء",
    "1180.SR": "SNB | الأهلي",
    "7010.SR": "STC | اس تي سي",
    "2010.SR": "SABIC | سابك",
    "2310.SR": "Sipchem | سبكيم",
    "2280.SR": "Almarai | المراعي",
    "1211.SR": "Ma'aden | معادن",
    "4190.SR": "Jarir | جرير",
    "4003.SR": "Extra | إكسترا",
    "4013.SR": "Dr. Sulaiman Al-Habib | سليمان الحبيب",
    "2020.SR": "SABIC Agri-Nutrients | سابك للمغذيات",
    "1140.SR": "Bank AlBilad | البلاد",
    "4260.SR": "Budget Saudi | بدجت",
    "4030.SR": "NSCSA | البحري",
    "1010.SR": "Riyad Bank | بنك الرياض",
    "8010.SR": "Bupa Arabia | بوبا العربية",
    "2290.SR": "Yansab | ينساب",
    "1111.SR": "Tadawul Group | مجموعة تداول"
}

# عكس القائمة للعرض (الاسم أولاً)
display_options = {v: k for k, v in tasi_data.items()}

# --- 3. الدوال الأساسية ---
def fetch_live_data(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        df = stock.history(period="1mo")
        if df.empty: return None, None, None
        current_p = round(df['Close'].iloc[-1], 2)
        auto_anchor = round(df['Low'].min(), 2)
        auto_target = round(df['High'].max(), 2)
        return current_p, auto_anchor, auto_target
    except: return None, None, None

def generate_pdf_link(content, ticker):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="SEF STRATEGIC ANALYSIS", ln=True, align='C')
        pdf.ln(5)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 7, txt="Created By Abu Yahia", ln=True, align='L')
        pdf.set_text_color(200, 0, 0)
        pdf.cell(200, 7, txt="Disclaimer: Educational purposes only.", ln=True, align='L')
        pdf.set_text_color(0, 0, 0)
        pdf.ln(10)
        clean_text = content.encode('ascii', 'ignore').decode('ascii')
        for line in clean_text.split('\n'):
            pdf.cell(0, 8, txt=line, ln=True)
        pdf_output = pdf.output(dest='S').encode('latin-1')
        b64 = base64.b64encode(pdf_output).decode()
        return f'<a href="data:application/octet-stream;base64,{b64}" download="SEF_{ticker}_Report.pdf" style="background-color: #ff4b4b; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block; margin-top: 10px;">📥 Download PDF Report</a>'
    except: return "⚠️ PDF Error"

# --- 4. واجهة المستخدم ---
st.title("🛡️ SEF Terminal | Abu Yahia")

# إدارة الذاكرة
if 'p_val' not in st.session_state: st.session_state['p_val'] = 0.0
if 'a_val' not in st.session_state: st.session_state['a_val'] = 0.0
if 't_val' not in st.session_state: st.session_state['t_val'] = 0.0

balance = st.sidebar.number_input("Portfolio Balance", value=100000)
risk_pct_input = st.sidebar.slider("Risk per Trade (%)", 0.5, 5.0, 1.0)

st.markdown("---")

# صف المدخلات
c1, c2, c3, c4, c5, c6 = st.columns([2.0, 1.1, 1.1, 1.1, 1.0, 1.2])

with c1:
    # القائمة المنسدلة مع ميزة البحث المدمجة
    selected_stock_name = st.selectbox("🔍 Search & Select Stock", options=list(display_options.keys()))
    ticker = display_options[selected_stock_name]

with c2: p_in = st.number_input("Price", value=float(st.session_state['p_val']), step=0.01)
with c3: a_in = st.number_input("Anchor", value=float(st.session_state['a_val']), step=0.01)
with c4: t_in = st.number_input("Target", value=float(st.session_state['t_val']), step=0.01)

with c5:
    st.write("##")
    # زر الرادار لجلب البيانات الحية للسهم المختار
    if st.button("🛰️ Radar", use_container_width=True):
        with st.spinner('Fetching data...'):
            p, a, t = fetch_live_data(ticker)
            if p:
                st.session_state.update({'p_val': p, 'a_val': a, 't_val': t})
                st.rerun()
            else:
                st.error("Data not found")

with c6:
    st.write("##")
    analyze_trigger = st.button("📊 Analyze", use_container_width=True)

st.markdown("---")

# --- 5. الحسابات والتقرير ---
if analyze_trigger:
    risk_per_share = abs(p_in - a_in)
    risk_cash = balance * (risk_pct_input / 100)
    
    # حساب النسب المئوية
    dist_to_sl_pct = (risk_per_share / p_in) * 100 if p_in != 0 else 0
    dist_to_t_pct = ((t_in - p_in) / p_in) * 100 if p_in != 0 else 0
    
    rr = (t_in - p_in) / risk_per_share if risk_per_share > 0 else 0
    qty = math.floor(risk_cash / risk_per_share) if risk_per_share > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Live Price", p_in)
    m2.metric("R:R Ratio", f"1:{round(rr, 2)}")
    m3.metric("Shares", qty)
    m4.metric("Risk Cash", round(risk_cash, 2))

    full_report = f"""
SEF ANALYSIS REPORT | Abu Yahia
------------------------------------
Stock: {selected_stock_name}
Ticker: {ticker}
------------------------------------
1. LEVELS:
- Entry Price: {p_in}
- Anchor (SL): {a_in}
- Target Price: {t_in}

2. STRATEGIC METRICS:
- R:R Ratio: 1:{round(rr, 2)}
- Quantity: {qty} Shares
- Cash at Risk: {round(risk_cash, 2)}
- Distance to SL: -{round(dist_to_sl_pct, 2)}%
- Potential Reward: +{round(dist_to_t_pct, 2)}%
------------------------------------
    """
    st.markdown("### 📄 SEF Structural Analysis")
    st.code(full_report)
    st.markdown(generate_pdf_link(full_report, ticker), unsafe_allow_html=True)
    
    # رسم بياني توضيحي
    st.line_chart(yf.Ticker(ticker).history(period="1y")['Close'], use_container_width=True)
