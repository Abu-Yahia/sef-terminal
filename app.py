import streamlit as st
import pandas as pd
import yfinance as yf
import math
from fpdf import FPDF

# --- 1. Page Config ---
st.set_page_config(page_title="SEF Terminal Pro", layout="wide")
st.markdown("<style>.stAppToolbar {display: none;}</style>", unsafe_allow_html=True)

# --- 2. Load TASI Data ---
@st.cache_data
def load_tasi_data():
    try:
        df = pd.read_csv("TASI.csv")
        df.columns = [c.strip() for c in df.columns]
        df['Ticker'] = df['Ticker'].astype(str).str.strip()
        df['Name_Ar'] = df['Company Name (Arabic)'].astype(str).str.strip()
        df['Display'] = df['Name_Ar'] + " | " + df['Ticker']
        mapping = dict(zip(df['Display'], df['Ticker']))
        return sorted(list(mapping.keys())), mapping
    except Exception:
        return [], {}

options, tasi_mapping = load_tasi_data()

# --- 3. Secure Session State (Persistent Data) ---
if 'ready' not in st.session_state:
    st.session_state.update({
        'price': 0.0, 'stop': 0.0, 'target': 0.0, 'fv_input': 0.0,
        'sma50': 0.0, 'sma100': 0.0, 'sma200': 0.0, 
        'ready': False, 'company_name': '---',
        'chg': 0.0, 'pct': 0.0, 'low52': 0.0, 'high52': 1.0
    })

# --- 4. Main UI Header & Branding ---
st.title("🛡️ SEF Terminal | Ultimate Hub")
st.markdown("""
    <div style='text-align: left; margin-top: -20px; margin-bottom: 20px;'>
        <p style='margin:0; font-size: 1.2em; font-weight: bold; color: #555;'>Created By Abu Yahia</p>
        <p style='margin:0; font-size: 0.85em; color: #cc0000;'>⚠️ Educational purposes only. Not financial advice.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. Ticker Info Bar (Visual Indicators) ---
if st.session_state['ready']:
    color = "#09AB3B" if st.session_state['chg'] >= 0 else "#FF4B4B"
    # 52-Week Range Logic
    r52 = st.session_state['high52'] - st.session_state['low52']
    p52 = ((st.session_state['price'] - st.session_state['low52']) / r52) * 100 if r52 > 0 else 0
    
    # Fair Value Logic (Visual relative to input)
    fv_diff = st.session_state['price'] - st.session_state['fv_input']
    fv_pos = 50 + (fv_diff / (st.session_state['price'] * 0.2) * 50) if st.session_state['fv_input'] > 0 else 50
    fv_pos = max(0, min(100, fv_pos))

    st.markdown(f"""
        <div style="background-color: #f8f9fb; padding: 20px; border-radius: 10px; border-left: 8px solid {color}; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="margin: 0; color: #131722; font-size: 1.6em;">{st.session_state['company_name']}</h2>
                <div style="display: flex; align-items: baseline; gap: 15px; margin-top: 10px;">
                    <span style="font-size: 2.8em; font-weight: bold; color: #131722;">{st.session_state['price']:.2f}</span>
                    <span style="font-size: 1.3em; color: {color}; font-weight: bold;">
                        {st.session_state['chg']:+.2f} ({st.session_state['pct']:+.2f}%)
                    </span>
                </div>
            </div>
            <div style="display: flex; gap: 40px; text-align: right;">
                <div style="width: 180px;">
                    <p style="margin:0; font-size: 0.85em; color: #787b86;">Fair Value Status</p>
                    <div style="display: flex; justify-content: space-between; font-size: 0.75em; font-weight: bold; margin-bottom: 5px;">
                        <span style="color:#FF4B4B">Under</span><span style="color:#09AB3B">Fair</span><span style="color:#FF4B4B">Over</span>
                    </div>
                    <div style="height: 6px; background: linear-gradient(to right, #FF4B4B, #09AB3B, #FF4B4B); border-radius: 3px; position: relative;">
                        <div style="position: absolute; left: {fv_pos}%; top: -4px; width: 14px; height: 14px; background: #131722; border-radius: 50%; border: 2px solid white;"></div>
                    </div>
                </div>
                <div style="width: 180px;">
                    <p style="margin:0; font-size: 0.85em; color: #787b86;">52 wk Range</p>
                    <div style="display: flex; justify-content: space-between; font-size: 0.9em; font-weight: bold; margin-bottom: 5px;">
                        <span>{st.session_state['low52']:.2f}</span><span>{st.session_state['high52']:.2f}</span>
                    </div>
                    <div style="height: 6px; background: #e0e3eb; border-radius: 3px; position: relative;">
                        <div style="position: absolute; left: {p52}%; top: -4px; width: 14px; height: 14px; background: #131722; border-radius: 50%; border: 2px solid white;"></div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 6. Input Controls (Updated Layout) ---
# c1: Ticker | c2: Market | c3: Anchor | c4: Target | c5: Fair Value (NEW) | c6: Radar/Analyze
cols = st.columns([2, 1, 1, 1, 1, 1])

with cols[0]:
    selected_stock = st.selectbox("Ticker Symbol", options=options)
    symbol = tasi_mapping[selected_stock]

with cols[1]: p_in = st.number_input("Market Price", value=float(st.session_state['price']), format="%.2f")
with cols[2]: s_in = st.number_input("Anchor Level", value=float(st.session_state['stop']), format="%.2f")
with cols[3]: t_in = st.number_input("Target Price", value=float(st.session_state['target']), format="%.2f")
# This is the NEW input box in the red square location
with cols[4]: fv_in = st.number_input("Fair Value", value=float(st.session_state['fv_input']), format="%.2f")

# --- 7. Radar & Analyze Buttons ---
with cols[5]:
    st.write("##")
    radar_col, analyze_col = st.columns(2)
    with radar_col:
        radar_btn = st.button("🛰️ Radar", use_container_width=True)
    with analyze_col:
        analyze_btn = st.button("📊 Analyze", use_container_width=True)

if radar_btn:
    raw = yf.download(f"{symbol}.SR", period="2y", progress=False)
    if not raw.empty:
        if isinstance(raw.columns, pd.MultiIndex): raw.columns = raw.columns.get_level_values(0)
        close = raw['Close']
        cur, prev = float(close.iloc[-1]), float(close.iloc[-2])
        st.session_state.update({
            'price': cur, 'chg': cur - prev, 'pct': ((cur - prev) / prev) * 100,
            'company_name': selected_stock.split('|')[0].strip(),
            'low52': float(raw['Low'].tail(252).min()),
            'high52': float(raw['High'].tail(252).max()),
            'stop': float(raw['Low'].tail(20).min()),
            'target': float(raw['High'].tail(20).max()),
            'fv_input': cur, # Default FV to current price on radar click
            'sma50': float(close.rolling(50).mean().iloc[-1]),
            'sma100': float(close.rolling(100).mean().iloc[-1]),
            'sma200': float(close.rolling(200).mean().iloc[-1]),
            'ready': True
        })
        st.rerun()

# Update FV in session state when user types
st.session_state['fv_input'] = fv_in

# --- 8. Technical Indicators Display ---
if st.session_state['ready']:
    st.subheader("📈 Technical Indicators")
    m_cols = st.columns(3)
    ma_data = [("SMA 50", st.session_state['sma50']), ("SMA 100", st.session_state['sma100']), ("SMA 200", st.session_state['sma200'])]
    for i, (label, val) in enumerate(ma_data):
        diff = p_in - val
        ma_color = "#FF4B4B" if diff < 0 else "#09AB3B"
        dist = (diff / val) * 100 if val != 0 else 0
        m_cols[i].markdown(f"""
            <div style="background-color: #f8f9fb; padding: 15px; border-radius: 10px; border-left: 6px solid {ma_color};">
                <p style="margin:0; font-size:14px; color:#5c5c5c;">{label}</p>
                <h3 style="margin:0; color:#31333F;">{val:.2f}</h3>
                <p style="margin:0; color:{ma_color}; font-weight:bold;">{dist:+.2f}%</p>
            </div>
        """, unsafe_allow_html=True)

# --- 9. Final Report & Chart (Original Features Preserved) ---
if analyze_btn or st.session_state['ready']:
    risk = abs(p_in - s_in)
    rr = (t_in - p_in) / risk if risk > 0 else 0
    res = "VALID" if rr >= 2 else "DANGEROUS"
    
    p50 = ((p_in - st.session_state['sma50']) / st.session_state['sma50']) * 100 if st.session_state['sma50'] else 0
    p100 = ((p_in - st.session_state['sma100']) / st.session_state['sma100']) * 100 if st.session_state['sma100'] else 0
    p200 = ((p_in - st.session_state['sma200']) / st.session_state['sma200']) * 100 if st.session_state['sma200'] else 0

    report = f"Ticker: {symbol} | Price: {p_in:.2f} | Fair Value: {fv_in:.2f}\nSMA 50 Dist: {p50:+.2f}%\nSMA 100 Dist: {p100:+.2f}%\nSMA 200 Dist: {p200:+.2f}%\nR:R Ratio: 1:{round(rr, 2)}\nRESULT: {res}"
    st.code(report, language="text")

    chart_raw = yf.download(f"{symbol}.SR", period="1y", progress=False)
    if not chart_raw.empty:
        if isinstance(chart_raw.columns, pd.MultiIndex): chart_raw.columns = chart_raw.columns.get_level_values(0)
        pdf = chart_raw[['Close']].copy()
        pdf['SMA 50'], pdf['SMA 100'], pdf['SMA 200'] = pdf['Close'].rolling(50).mean(), pdf['Close'].rolling(100).mean(), pdf['Close'].rolling(200).mean()
        st.line_chart(pdf)
