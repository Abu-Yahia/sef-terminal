import streamlit as st
import pandas as pd
import yfinance as yf
import math
from fpdf import FPDF

# --- 1. Page Config ---
st.set_page_config(page_title="SEF Terminal Pro", layout="wide")

# --- 2. Load TASI Data ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("TASI.csv")
        df.columns = [c.strip() for c in df.columns]
        df['Ticker'] = df['Ticker'].astype(str).str.strip()
        df['Name_Ar'] = df['Company Name (Arabic)'].astype(str).str.strip()
        df['Display'] = df['Name_Ar'] + " | " + df['Ticker']
        mapping = dict(zip(df['Display'], df['Ticker']))
        return sorted(list(mapping.keys())), mapping
    except: return [], {}

options, tasi_mapping = load_data()

# --- 3. Secure Session State ---
if 'ready' not in st.session_state:
    st.session_state.update({
        'price': 0.0, 'stop': 0.0, 'target': 0.0, 
        'sma50': 0.0, 'sma100': 0.0, 'sma200': 0.0, 
        'low52': 0.0, 'high52': 0.0, 'ready': False
    })

# --- 4. UI Layout ---
st.title("🛡️ SEF Terminal Pro | Final Benchmark")

c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1, 1, 1, 0.8, 1])
with c1:
    selected_stock = st.selectbox("Search Stock:", options=options)
    symbol = tasi_mapping[selected_stock]
with c2: p_in = st.number_input("Price", value=float(st.session_state['price']), format="%.2f")
with c3: s_in = st.number_input("Stop Loss", value=float(st.session_state['stop']), format="%.2f")
with c4: t_in = st.number_input("Target", value=float(st.session_state['target']), format="%.2f")

# --- 5. Radar Engine ---
with c5:
    st.write("##")
    if st.button("🛰️ RADAR", use_container_width=True):
        raw = yf.download(f"{symbol}.SR", period="2y", progress=False)
        if not raw.empty:
            if isinstance(raw.columns, pd.MultiIndex): raw.columns = raw.columns.get_level_values(0)
            close = raw['Close']
            st.session_state.update({
                'price': float(close.iloc[-1]),
                'stop': float(raw['Low'].tail(20).min()),
                'target': float(raw['High'].tail(20).max()),
                'sma50': float(close.rolling(50).mean().iloc[-1]),
                'sma100': float(close.rolling(100).mean().iloc[-1]),
                'sma200': float(close.rolling(200).mean().iloc[-1]),
                'low52': float(raw['Low'].tail(252).min()),
                'high52': float(raw['High'].tail(252).max()),
                'ready': True
            })
            st.rerun()

with c6:
    st.write("##")
    analyze_btn = st.button("📊 ANALYZE", use_container_width=True)

# --- 6. Technical Indicators & Visual Range Bar ---
if st.session_state['ready']:
    st.subheader("📈 Technical Indicators")
    m_cols = st.columns(3)
    ma_list = [("SMA 50", st.session_state['sma50']), ("SMA 100", st.session_state['sma100']), ("SMA 200", st.session_state['sma200'])]
    
    for i, (label, val) in enumerate(ma_list):
        diff = p_in - val
        color = "#FF4B4B" if diff < 0 else "#09AB3B"
        dist_pct = (diff / val) * 100
        m_cols[i].markdown(f"""
            <div style="background-color: #f8f9fb; padding: 15px; border-radius: 10px; border-left: 6px solid {color};">
                <p style="margin:0; font-size:14px; color:#5c5c5c;">{label}</p>
                <h3 style="margin:0; color:#31333F;">{val:.2f}</h3>
                <p style="margin:0; font-size:16px; color:{color}; font-weight:bold;">{dist_pct:+.2f}%</p>
            </div>
        """, unsafe_allow_html=True)

    # شريط النطاق السعري البصري
    st.write("##")
    st.write("**Yearly Price Range (52W)**")
    low, high = st.session_state['low52'], st.session_state['high52']
    range_pct = ((p_in - low) / (high - low)) * 100 if (high - low) != 0 else 0
    st.markdown(f"""
        <div style="width: 100%; background-color: #e0e0e0; border-radius: 5px; height: 12px; position: relative;">
            <div style="width: 5px; height: 20px; background-color: #4A90E2; position: absolute; left: {min(max(range_pct, 0), 100)}%; top: -4px; border-radius: 2px;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 5px; color: #555;">
            <span>{low:.2f} (Low)</span>
            <span>Current: {p_in:.2f}</span>
            <span>{high:.2f} (High)</span>
        </div>
    """, unsafe_allow_html=True)

# --- 7. Structural Analysis & PDF ---
if analyze_btn or st.session_state['ready']:
    st.markdown("---")
    risk_amt = abs(p_in - s_in)
    rr_ratio = (t_in - p_in) / risk_amt if risk_amt > 0 else 0
    balance = st.sidebar.number_input("Portfolio", value=100000)
    risk_pct = st.sidebar.slider("Risk %", 0.5, 5.0, 1.0)
    shares = math.floor((balance * (risk_pct/100)) / risk_amt) if risk_amt > 0 else 0

    t_cols = st.columns(4)
    t_cols[0].metric("Live Price", f"{p_in:.2f}")
    t_cols[1].metric("R:R Ratio", f"1:{round(rr_ratio, 2)}")
    t_cols[2].metric("Shares", f"{shares}")
    t_cols[3].metric("Risk Cash", f"{balance * (risk_pct/100):.2f}")

    st.subheader("📄 SEF Structural Analysis")
    
    # حساب المسافات للتقرير
    p50 = ((p_in - st.session_state['sma50']) / st.session_state['sma50']) * 100
    p100 = ((p_in - st.session_state['sma100']) / st.session_state['sma100']) * 100
    p200 = ((p_in - st.session_state['sma200']) / st.session_state['sma200']) * 100

    report_text = f"""
    SEF STRATEGIC ANALYSIS REPORT
    Created By Abu Yahia
    ------------------------------
    Ticker: {symbol}.SR | Price: {p_in:.2f}
    
    1. LEVELS:
    - Entry: {p_in:.2f} | Anchor (SL): {s_in:.2f} | Target: {t_in:.2f}

    2. TECHNICALS (MAs & Distance):
    - SMA 50 : {st.session_state['sma50']:.2f} (Dist: {p50:+.2f}%)
    - SMA 100: {st.session_state['sma100']:.2f} (Dist: {p100:+.2f}%)
    - SMA 200: {st.session_state['sma200']:.2f} (Dist: {p200:+.2f}%)

    3. METRICS:
    - R:R Ratio: 1:{round(rr_ratio, 2)} | Quantity: {shares}
    
    ------------------------------
    This content is for informational purposes only and not investment advice.
    "Capital preservation is the first priority."
    """
    st.code(report_text, language="text")

    # PDF Generation
    def create_pdf(content):
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=11)
        for line in content.split('\n'): pdf.cell(200, 8, txt=line, ln=True, align='L')
        return pdf.output(dest='S').encode('latin-1')

    st.download_button("📥 Download PDF Report", data=create_pdf(report_text), file_name=f"SEF_{symbol}.pdf")

    # Chart & Footer Disclaimer
    st.line_chart(yf.download(f"{symbol}.SR", period="1y", progress=False)['Close'])
    st.markdown("<br><p style='text-align: center; color: gray; font-size: 12px;'>This content is for informational purposes only and not investment advice.</p>", unsafe_allow_html=True)
