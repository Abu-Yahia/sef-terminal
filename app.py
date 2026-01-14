import streamlit as st
import yfinance as yf
import pandas as pd
import math
from fpdf import FPDF
import base64

# --- 1. إعدادات الصفحة ---
icon_url = "https://i.ibb.co/vzR0jXJX/robot-icon.png"
st.set_page_config(page_title="SEF Terminal Pro", page_icon=icon_url, layout="wide")

# --- 2. الدوال الأساسية ---
def get_ticker_info(symbol):
    """جلب اسم السهم وبياناته الحية بناءً على الرمز أو البحث"""
    try:
        # إذا أدخل المستخدم رقماً فقط (مثل 2020) نضيف له .SR
        if symbol.isdigit():
            full_symbol = f"{symbol}.SR"
        elif not symbol.endswith(".SR") and not symbol.isalpha():
            full_symbol = f"{symbol}.SR"
        else:
            full_symbol = symbol.upper()
            
        stock = yf.Ticker(full_symbol)
        # محاولة جلب الاسم الرسمي من الشركة
        name = stock.info.get('longName', full_symbol)
        df = stock.history(period="1mo")
        
        if df.empty: return None, None, None, None
        
        current_p = round(df['Close'].iloc[-1], 2)
        auto_anchor = round(df['Low'].min(), 2)
        auto_target = round(df['High'].max(), 2)
        return current_p, auto_anchor, auto_target, name
    except:
        return None, None, None, None

def generate_pdf_link(content, ticker):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="SEF STRATEGIC ANALYSIS", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", size=11)
        clean_text = content.encode('ascii', 'ignore').decode('ascii')
        for line in clean_text.split('\n'):
            pdf.cell(0, 8, txt=line, ln=True)
        pdf_output = pdf.output(dest='S').encode('latin-1')
        b64 = base64.b64encode(pdf_output).decode()
        return f'<a href="data:application/octet-stream;base64,{b64}" download="SEF_{ticker}_Report.pdf" style="background-color: #ff4b4b; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">📥 Download PDF Report</a>'
    except: return "⚠️ PDF Error"

# --- 3. واجهة المستخدم ---
st.title("🛡️ SEF Terminal | Universal Search")

# إدارة الذاكرة
if 'p_val' not in st.session_state: st.session_state['p_val'] = 0.0
if 'a_val' not in st.session_state: st.session_state['a_val'] = 0.0
if 't_val' not in st.session_state: st.session_state['t_val'] = 0.0
if 'stock_name' not in st.session_state: st.session_state['stock_name'] = "No Stock Selected"

balance = st.sidebar.number_input("Portfolio Balance", value=100000)
risk_pct_input = st.sidebar.slider("Risk per Trade (%)", 0.5, 5.0, 1.0)

st.markdown("---")

# صف المدخلات
c1, c2, c3, c4, c5, c6 = st.columns([1.8, 1.1, 1.1, 1.1, 1.0, 1.2])

with c1:
    user_input = st.text_input("🔍 Enter Ticker (e.g., 2020 or 4335)", "4009").strip()

with c2: p_in = st.number_input("Price", value=float(st.session_state['p_val']), step=0.01)
with c3: a_in = st.number_input("Anchor", value=float(st.session_state['a_val']), step=0.01)
with c4: t_in = st.number_input("Target", value=float(st.session_state['t_val']), step=0.01)

with c5:
    st.write("##")
    if st.button("🛰️ Radar", use_container_width=True):
        p, a, t, name = get_ticker_info(user_input)
        if p:
            st.session_state.update({'p_val': p, 'a_val': a, 't_val': t, 'stock_name': name})
            st.rerun()
        else:
            st.error("Symbol not found. Try numbers like 2020")

with c6:
    st.write("##")
    analyze_trigger = st.button("📊 Analyze", use_container_width=True)

# عرض اسم السهم المختار حالياً
st.info(f"📍 Active Analysis: **{st.session_state['stock_name']}**")

st.markdown("---")

# --- 4. التحليل والتقارير ---
if analyze_trigger:
    risk_per_share = abs(p_in - a_in)
    risk_cash = balance * (risk_pct_input / 100)
    
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
SEF STRATEGIC REPORT | Abu Yahia
------------------------------------
Company: {st.session_state['stock_name']}
Ticker: {user_input}
------------------------------------
1. LEVELS:
- Entry Price: {p_in}
- Anchor (SL): {a_in}
- Target Price: {t_in}

2. RISK METRICS:
- R:R Ratio: 1:{round(rr, 2)}
- Quantity: {qty} Shares
- Cash at Risk: {round(risk_cash, 2)}
- Distance to SL: -{round(dist_to_sl_pct, 2)}%
- Target Reward: +{round(dist_to_t_pct, 2)}%
------------------------------------
    """
    st.code(full_report)
    st.markdown(generate_pdf_link(full_report, user_input), unsafe_allow_html=True)
    
    # جلب الرمز الصحيح للرسم البياني
    graph_ticker = f"{user_input}.SR" if user_input.isdigit() else user_input
    st.line_chart(yf.Ticker(graph_ticker).history(period="1y")['Close'], use_container_width=True)
