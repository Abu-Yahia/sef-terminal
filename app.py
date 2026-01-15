import streamlit as st
import yfinance as yf
import pandas as pd
import math
from fpdf import FPDF
import base64

# --- 1. إعدادات الصفحة ---
icon_url = "https://i.ibb.co/vzR0jXJX/robot-icon.png"
st.set_page_config(page_title="SEF Terminal Pro", page_icon=icon_url, layout="wide")

# --- 2. دالة جلب البيانات من ملفك المرفوع ---
@st.cache_data
def load_full_tasi_list():
    file_name = "TASI.xlsx - Market Watch Today-2025-10-27.csv"
    try:
        # قراءة الملف وتخطي الأسطر التعريفية للوصول للرأس (Header)
        df = pd.read_csv(file_name, skiprows=4)
        
        # تنظيف البيانات: إزالة الأسطر الفارغة واختيار الأعمدة المطلوبة
        df = df.dropna(subset=[df.columns[0], df.columns[2]])
        
        # بناء قائمة البحث: "الاسم العربي | الرمز"
        # العمود 0 هو الرمز، والعمود 2 هو الاسم العربي
        df['Display'] = df.iloc[:, 2].astype(str) + " | " + df.iloc[:, 0].astype(str).str.split('.').str[0]
        
        # إنشاء قاموس لربط العرض بالرمز البرمجي
        mapping = dict(zip(df['Display'], df.iloc[:, 0].astype(str).str.split('.').str[0]))
        
        # ترتيب القائمة أبجدياً
        sorted_options = sorted(list(mapping.keys()))
        return sorted_options, mapping
    except Exception as e:
        st.error(f"⚠️ لم يتم العثور على ملف الأسهم أو التنسيق غير صحيح: {e}")
        return [], {}

options, tasi_mapping = load_full_tasi_list()

# --- 3. الدوال الأساسية ---
def fetch_live_data(ticker_symbol):
    try:
        full_ticker = f"{ticker_symbol}.SR"
        stock = yf.Ticker(full_ticker)
        df = stock.history(period="1mo")
        if df.empty: return None, None, None
        return round(df['Close'].iloc[-1], 2), round(df['Low'].min(), 2), round(df['High'].max(), 2)
    except: return None, None, None

# --- 4. واجهة المستخدم ---
st.title("🛡️ SEF Terminal Pro | الإصدار الشامل")
st.write(f"🖋️ **المطور: أبو يحيى** | تم تحميل {len(options)} سهم من القائمة")

if 'p_val' not in st.session_state: st.session_state.update({'p_val': 0.0, 'a_val': 0.0, 't_val': 0.0})

balance = st.sidebar.number_input("Portfolio Balance (المحفظة)", value=100000)
risk_pct_input = st.sidebar.slider("Risk (%) نسبة المخاطرة", 0.5, 5.0, 1.0)

st.markdown("---")

c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.0, 1.0, 1.0, 0.8, 1.0])

with c1:
    if options:
        selected_stock = st.selectbox("🔍 ابحث عن السهم (دراية، الراجحي، 4339...)", options=options)
        ticker_code = tasi_mapping[selected_stock]
    else:
        ticker_code = st.text_input("أدخل الرمز يدوياً (مثال: 2222)", "2222")

with c2: p_in = st.number_input("Price", value=float(st.session_state['p_val']), step=0.01)
with c3: a_in = st.number_input("Anchor", value=float(st.session_state['a_val']), step=0.01)
with c4: t_in = st.number_input("Target", value=float(st.session_state['t_val']), step=0.01)

with c5:
    st.write("##")
    if st.button("🛰️ Radar", use_container_width=True):
        p, a, t = fetch_live_data(ticker_code)
        if p:
            st.session_state.update({'p_val': p, 'a_val': a, 't_val': t})
            st.rerun()

with c6:
    st.write("##")
    analyze_trigger = st.button("📊 Analyze", use_container_width=True)

# --- 5. الحسابات والنتائج ---
if analyze_trigger:
    risk_per_share = abs(p_in - a_in)
    risk_cash = balance * (risk_pct_input / 100)
    
    if risk_per_share > 0:
        dist_sl = (risk_per_share / p_in) * 100
        dist_tp = ((t_in - p_in) / p_in) * 100
        rr = (t_in - p_in) / risk_per_share
        qty = math.floor(risk_cash / risk_per_share)

        st.success(f"📈 تحليل: {selected_stock}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("الكمية", f"{qty} سهم")
        m2.metric("نسبة الوقف", f"-{round(dist_sl, 2)}%")
        m3.metric("نسبة الهدف", f"+{round(dist_tp, 2)}%")
        m4.metric("المخاطرة ريال", f"{round(risk_cash, 1)}")

        st.info(f"📊 معامل العائد للمخاطرة (R:R) = 1:{round(rr, 2)}")
        st.line_chart(yf.Ticker(f"{ticker_code}.SR").history(period="1y")['Close'])
