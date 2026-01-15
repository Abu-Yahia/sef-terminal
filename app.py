import streamlit as st
import pandas as pd
import yfinance as yf
import math
from fpdf import FPDF
import base64

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SEF Terminal Pro", page_icon="📈", layout="wide")

# --- 2. دالة قراءة الـ 262 شركة من ملف TASI.csv الجديد ---
@st.cache_data
def load_tasi_complete():
    try:
        # قراءة الملف الذي أرسلته (تأكد من تسميته TASI.csv عند رفعه على GitHub)
        df = pd.read_csv("TASI.csv")
        
        # تنظيف البيانات لضمان قراءة كل الأسطر
        df['Ticker'] = df['Ticker'].astype(str).str.strip()
        df['Name_Ar'] = df['Company Name (Arabic)'].astype(str).str.strip()
        df['Sector'] = df['Industry Group'].astype(str).str.strip()
        
        # دمج البيانات للبحث (الاسم | الرمز)
        df['Display'] = df['Name_Ar'] + " | " + df['Ticker'] + " (" + df['Sector'] + ")"
        
        # تحويلها لقاموس
        mapping = dict(zip(df['Display'], df['Ticker']))
        return sorted(list(mapping.keys())), mapping
    except Exception as e:
        st.error(f"خطأ في قراءة الـ 262 شركة: {e}")
        return [], {}

options, tasi_mapping = load_tasi_complete()

# --- 3. وظائف جلب السعر والبيانات ---
def fetch_live_data(ticker_symbol):
    try:
        full_ticker = f"{ticker_symbol}.SR"
        stock = yf.Ticker(full_ticker)
        df = stock.history(period="1mo")
        if df.empty: return None, None, None
        curr = round(df['Close'].iloc[-1], 2)
        low = round(df['Low'].min(), 2)
        high = round(df['High'].max(), 2)
        return curr, low, high
    except: return None, None, None

# --- 4. واجهة المستخدم ---
st.title("🛡️ SEF Terminal Pro | Abu Yahia Edition")
st.write(f"📊 **حالة النظام:** تم تحميل **{len(options)}** شركة من ملفك بنجاح.")

if 'p_val' not in st.session_state: st.session_state.update({'p_val': 0.0, 'a_val': 0.0, 't_val': 0.0})

# الشريط الجانبي
balance = st.sidebar.number_input("Portfolio Balance (المحفظة)", value=100000)
risk_pct = st.sidebar.slider("Risk (%) نسبة المخاطرة", 0.5, 5.0, 1.0)

st.markdown("---")

# صف المدخلات
c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.0, 1.0, 1.0, 0.8, 1.0])

with c1:
    if options:
        selected_stock = st.selectbox("🔍 ابحث في الـ 262 شركة (مثلاً: دراية ريت):", options=options)
        ticker = tasi_mapping[selected_stock]
    else:
        ticker = "4009"

with c2: p_in = st.number_input("السعر", value=float(st.session_state['p_val']), step=0.01)
with c3: a_in = st.number_input("الوقف", value=float(st.session_state['a_val']), step=0.01)
with c4: t_in = st.number_input("الهدف", value=float(st.session_state['t_val']), step=0.01)

with c5:
    st.write("##")
    if st.button("🛰️ Radar", use_container_width=True):
        p, a, t = fetch_live_data(ticker)
        if p:
            st.session_state.update({'p_val': p, 'a_val': a, 't_val': t})
            st.rerun()

with c6:
    st.write("##")
    analyze = st.button("📊 Analyze", use_container_width=True)

# --- 5. الحسابات والنتائج ---
if analyze:
    risk_per_share = abs(p_in - a_in)
    risk_cash = balance * (risk_pct / 100)
    
    if risk_per_share > 0:
        qty = math.floor(risk_cash / risk_per_share)
        rr = (t_in - p_in) / risk_per_share
        
        st.success(f"✅ تم التحليل: {selected_stock}")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("عدد الأسهم", f"{qty}")
        m2.metric("نسبة الوقف", f"-{round((risk_per_share/p_in)*100, 2)}%")
        m3.metric("نسبة الهدف", f"+{round(((t_in-p_in)/p_in)*100, 2)}%")
        m4.metric("مبلغ المخاطرة", f"{round(risk_cash, 2)} ريال")

        st.info(f"📍 معامل العائد للمخاطرة R:R = 1:{round(rr, 2)}")
        
        # عرض شارت بسيط للنمو السنوي
        st.line_chart(yf.Ticker(f"{ticker}.SR").history(period="1y")['Close'])
