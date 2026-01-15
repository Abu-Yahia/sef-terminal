import streamlit as st
import pandas as pd
import yfinance as yf
import math

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SEF Terminal Pro", layout="wide")

# --- 2. تحميل البيانات من ملف TASI.csv ---
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
    except Exception as e:
        st.error(f"خطأ في ملف TASI.csv: {e}")
        return [], {}

options, tasi_mapping = load_tasi_data()

# --- 3. تهيئة مخزن الحالة (Session State) لضمان عمل الأزرار ---
if 'p' not in st.session_state:
    st.session_state.update({
        'p': 0.0, 'a': 0.0, 't': 0.0, 
        'ma50': 0.0, 'ma100': 0.0, 'ma200': 0.0,
        'has_data': False
    })

# --- 4. واجهة المستخدم ---
st.title("🛡️ SEF Terminal Pro | النسخة المستقرة")
st.write(f"✅ تم تفعيل **{len(options)}** شركة من ملفك")

st.markdown("---")

# صف المدخلات
c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1, 1, 1, 0.8, 1])

with c1:
    choice = st.selectbox("🔍 ابحث عن السهم:", options=options)
    t_code = tasi_mapping[choice]

with c2: p_in = st.number_input("السعر", value=float(st.session_state['p']), format="%.2f")
with c3: a_in = st.number_input("الوقف", value=float(st.session_state['a']), format="%.2f")
with c4: t_in = st.number_input("الهدف", value=float(st.session_state['t']), format="%.2f")

# --- 5. وظيفة زر الرادار (تعديل جذري) ---
with c5:
    st.write("##")
    if st.button("🛰️ Radar", use_container_width=True):
        try:
            # جلب البيانات
            raw_df = yf.download(f"{t_code}.SR", period="2y", progress=False)
            if not raw_df.empty:
                # تنظيف الـ Multi-index
                if isinstance(raw_df.columns, pd.MultiIndex):
                    raw_df.columns = raw_df.columns.get_level_values(0)
                
                close = raw_df['Close']
                p = float(close.iloc[-1])
                
                # تحديث الحالة
                st.session_state.update({
                    'p': p,
                    'a': float(raw_df['Low'].tail(20).min()),
                    't': float(raw_df['High'].tail(20).max()),
                    'ma50': float(close.rolling(50).mean().iloc[-1]),
                    'ma100': float(close.rolling(100).mean().iloc[-1]),
                    'ma200': float(close.rolling(200).mean().iloc[-1]),
                    'has_data': True
                })
                st.rerun()
        except Exception as e:
            st.error(f"عطل في جلب البيانات: {e}")

with c6:
    st.write("##")
    analyze_btn = st.button("📊 Analyze", use_container_width=True)

# --- 6. عرض المتوسطات (تظهر فوراً بمجرد توفر البيانات) ---
if st.session_state['has_data']:
    st.markdown("### 📈 المتوسطات الحسابية (SMA)")
    m_cols = st.columns(3)
    
    ma_list = [
        ("SMA 50", st.session_state['ma50']),
        ("SMA 100", st.session_state['ma100']),
        ("SMA 200", st.session_state['ma200'])
    ]
    
    for i, (label, val) in enumerate(ma_list):
        diff = st.session_state['p'] - val
        color = "normal" if diff >= 0 else "inverse"
        m_cols[i].metric(label, f"{val:.2f}", delta=f"{diff:.2f} ريال", delta_color=color)

# --- 7. التحليل المالي والشارت ---
if analyze_btn:
    risk_val = abs(p_in - a_in)
    if risk_val > 0:
        balance = st.sidebar.number_input("المحفظة", value=100000)
        risk_p = st.sidebar.slider("المخاطرة %", 0.5, 5.0, 1.0)
        qty = math.floor((balance * (risk_p/100)) / risk_val)
        
        st.markdown("---")
        st.success(f"📊 تحليل سهم: {choice}")
        res_cols = st.columns(3)
        res_cols[0].metric("الكمية", f"{qty} سهم")
        res_cols[1].metric("الوقف %", f"-{round((risk_val/p_in)*100, 2)}%")
        res_cols[2].metric("الهدف R:R", f"1:{round((t_in - p_in) / risk_val, 2)}")

        # الشارت
        c_df = yf.download(f"{t_code}.SR", period="1y", progress=False)
        if isinstance(c_df.columns, pd.MultiIndex): c_df.columns = c_df.columns.get_level_values(0)
        st.line_chart(c_df['Close'])
