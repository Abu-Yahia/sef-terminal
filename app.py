import streamlit as st
import pandas as pd
import yfinance as yf
import math
from fpdf import FPDF

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SEF Terminal Pro", layout="wide")
st.markdown("<style>.stAppToolbar {display: none;}</style>", unsafe_allow_html=True)

# --- 2. جلب بيانات TASI ---
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
    except:
        return [], {}

options, tasi_mapping = load_tasi_data()

# --- 3. إدارة الذاكرة (حل مشكلة KeyError) ---
if 'ready' not in st.session_state:
    st.session_state.update({
        'price': 0.0, 'stop': 0.0, 'target': 0.0,
        'sma50': 0.0, 'sma100': 0.0, 'sma200': 0.0, 
        'ready': False, 'company_name': '---', 
        'chg': 0.0, 'pct': 0.0, 'low52': 0.0, 'high52': 0.0
    })

# --- 4. العنوان والتوقيع (Created By Abu Yahia) ---
st.title("🛡️ SEF Terminal Pro | Final Benchmark")
st.markdown("""
    <div style='text-align: left; margin-top: -20px; margin-bottom: 20px;'>
        <span style='color: #555; font-size: 1.1em; font-weight: bold;'>🖋️ Created By Abu Yahia</span>
        <span style='color: #cc0000; font-size: 0.85em; margin-left: 20px;'>
            ⚠️ تعليمي فقط | Educational purposes only
        </span>
    </div>
    """, unsafe_allow_html=True)

# --- 5. شريط المعلومات الاحترافي (نفس شكل مجموعة تداول) ---
if st.session_state['ready']:
    color = "#09AB3B" if st.session_state['chg'] >= 0 else "#FF4B4B"
    range_52 = st.session_state['high52'] - st.session_state['low52']
    pos_52 = ((st.session_state['price'] - st.session_state['low52']) / range_52) * 100 if range_52 > 0 else 0
    
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
            <div style="width: 300px;">
                <p style="margin:0; font-size: 0.85em; color: #787b86; text-align: right;">52-Week Range</p>
                <div style="display: flex; justify-content: space-between; font-size: 0.9em; font-weight: bold; margin-bottom: 5px;">
                    <span>{st.session_state['low52']:.2f}</span>
                    <span>{st.session_state['high52']:.2f}</span>
                </div>
                <div style="height: 6px; background: #e0e3eb; border-radius: 3px; position: relative;">
                    <div style="position: absolute; left: {pos_52}%; top: -4px; width: 14px; height: 14px; background: #131722; border-radius: 50%; border: 2px solid white;"></div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 6. واجهة المدخلات ---
c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1, 1, 1, 0.8, 1])
with c1:
    selected_stock = st.selectbox("Search Stock:", options=options)
    symbol = tasi_mapping[selected_stock]
with c2: p_in = st.number_input("Price", value=float(st.session_state['price']), format="%.2f")
with c3: s_in = st.number_input("Stop Loss", value=float(st.session_state['stop']), format="%.2f")
with c4: t_in = st.number_input("Target", value=float(st.session_state['target']), format="%.2f")

# --- 7. الرادار (RADAR) ---
with c5:
    st.write("##")
    if st.button("🛰️ RADAR", use_container_width=True):
        raw = yf.download(f"{symbol}.SR", period="2y", progress=False)
        if not raw.empty:
            if isinstance(raw.columns, pd.MultiIndex): raw.columns = raw.columns.get_level_values(0)
            close = raw['Close']
            cur = float(close.iloc[-1])
            prev = float(close.iloc[-2])
            st.session_state.update({
                'price': cur, 'chg': cur - prev, 'pct': ((cur - prev) / prev) * 100,
                'company_name': selected_stock.split('|')[0].strip(),
                'low52': float(raw['Low'].tail(252).min()),
                'high52': float(raw['High'].tail(252).max()),
                'stop': float(raw['Low'].tail(20).min()),
                'target': float(raw['High'].tail(20).max()),
                'sma50': float(close.rolling(50).mean().iloc[-1]),
                'sma100': float(close.rolling(100).mean().iloc[-1]),
                'sma200': float(close.rolling(200).mean().iloc[-1]),
                'ready': True
            })
            st.rerun()

with c6:
    st.write("##")
    analyze_btn = st.button("📊 ANALYZE", use_container_width=True)

# (بقية كود التحليل والمؤشرات والـ PDF تظل كما هي في ملفك الأصلي)
if st.session_state['ready']:
    # ... نفس كود الـ Technical Indicators والـ PDF من ملف app (1).py
    pass
