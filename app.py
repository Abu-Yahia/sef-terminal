import streamlit as st
import pandas as pd
import yfinance as yf
import math

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SEF Terminal Pro", layout="wide")

# --- 2. قراءة ملف الـ 262 شركة ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("TASI.csv")
        df['Ticker'] = df['Ticker'].astype(str).str.strip()
        df['Name_Ar'] = df['Company Name (Arabic)'].astype(str).str.strip()
        df['Display'] = df['Name_Ar'] + " | " + df['Ticker']
        mapping = dict(zip(df['Display'], df['Ticker']))
        return sorted(list(mapping.keys())), mapping
    except Exception as e:
        st.error(f"خطأ في ملف TASI.csv: {e}")
        return [], {}

options, tasi_mapping = load_data()

# --- 3. دالة جلب المتوسطات بدقة ---
def get_technical_indicators(ticker):
    try:
        # جلب بيانات سنتين لضمان حساب متوسط 200 يوم بدقة
        data = yf.download(f"{ticker}.SR", period="2y", interval="1d", progress=False)
        if data.empty or len(data) < 20:
            return None
            
        # استخدام Close فقط ومعالجته
        close = data['Close']
        
        results = {
            "current_price": float(close.iloc[-1]),
            "sma50": float(close.rolling(window=50).mean().iloc[-1]),
            "sma100": float(close.rolling(window=100).mean().iloc[-1]),
            "sma200": float(close.rolling(window=200).mean().iloc[-1]),
            "low": float(data['Low'].tail(20).min()),
            "high": float(data['High'].tail(20).max())
        }
        return results
    except:
        return None

# --- 4. واجهة المستخدم ---
st.title("🛡️ SEF Terminal Pro | Technical Edition")
st.write(f"✅ الشركات المحملة: **{len(options)}**")

# تهيئة مخزن البيانات
if 'results' not in st.session_state:
    st.session_state.update({'results': None, 'p_in': 0.0, 'a_in': 0.0, 't_in': 0.0})

st.markdown("---")

# صف المدخلات
c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1, 1, 1, 0.8, 1])

with c1:
    choice = st.selectbox("🔍 ابحث في الـ 262 شركة:", options=options)
    ticker_code = tasi_mapping[choice]

with c2: p_in = st.number_input("السعر", value=float(st.session_state['p_in']), step=0.01)
with c3: a_in = st.number_input("الوقف", value=float(st.session_state['a_in']), step=0.01)
with c4: t_in = st.number_input("الهدف", value=float(st.session_state['t_in']), step=0.01)

with c5:
    st.write("##")
    if st.button("🛰️ Radar", use_container_width=True):
        res = get_technical_indicators(ticker_code)
        if res:
            st.session_state.update({
                'results': res,
                'p_in': res['current_price'],
                'a_in': res['low'],
                't_in': res['high']
            })
            st.rerun()
        else:
            st.warning("⚠️ تعذر جلب المتوسطات لهذا السهم حالياً")

with c6:
    st.write("##")
    analyze = st.button("📊 Analyze", use_container_width=True)

# --- 5. عرض المتوسطات (SMA) ---
if st.session_state['results']:
    r = st.session_state['results']
    st.markdown("### 📈 المتوسطات المتحركة (SMA)")
    m1, m2, m3 = st.columns(3)
    
    # دالة لعرض المتوسط بلون ذكي
    def show_ma(col, label, val, current):
        diff = round(current - val, 2)
        color = "normal" if diff >= 0 else "inverse"
        col.metric(label, f"{val:.2f}", delta=f"{diff:.2f} ريال", delta_color=color)

    show_ma(m1, "SMA 50 (قصير)", r['sma50'], r['current_price'])
    show_ma(m2, "SMA 100 (متوسط)", r['sma100'], r['current_price'])
    show_ma(m3, "SMA 200 (طويل)", r['sma200'], r['current_price'])

# --- 6. التحليل المالي ---
if analyze:
    risk_ps = abs(p_in - a_in)
    if risk_ps > 0:
        balance = st.sidebar.number_input("المحفظة", value=100000)
        risk_pct = st.sidebar.slider("المخاطرة %", 0.5, 5.0, 1.0)
        qty = math.floor((balance * (risk_pct/100)) / risk_ps)
        
        st.success(f"📈 تحليل: {choice}")
        res_cols = st.columns(3)
        res_cols[0].metric("الكمية", f"{qty} سهم")
        res_cols[1].metric("نسبة الوقف", f"-{round((risk_ps/p_in)*100, 2)}%")
        res_cols[2].metric("معامل R:R", f"1:{round((t_in - p_in) / risk_ps, 2)}")
        
        # الشارت
        st.line_chart(yf.download(f"{ticker_code}.SR", period="1y")['Close'])
