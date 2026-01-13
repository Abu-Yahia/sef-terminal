import streamlit as st
import yfinance as yf
import math
import pandas as pd

# --- إعدادات الصفحة ---
st.set_page_config(page_title="SEF Terminal", page_icon="📈", layout="wide")

# --- التصميم الجمالي (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- محرك SEF المنطقي ---
def calculate_sef(current_price, stop_loss, target, balance, risk_pct):
    risk_per_share = abs(current_price - stop_loss)
    reward_per_share = abs(target - current_price)
    rr_ratio = reward_per_share / risk_per_share if risk_per_share > 0 else 0
    
    cash_to_risk = balance * (risk_pct / 100)
    qty = math.floor(cash_to_risk / risk_per_share) if risk_per_share > 0 else 0
    total_cost = qty * current_price
    
    return rr_ratio, qty, total_cost, cash_to_risk

# --- واجهة التطبيق ---
st.title("🛡️ SEF Terminal | محرك الأمان الاستثماري")
st.sidebar.header("⚙️ إعدادات المحفظة")
balance = st.sidebar.number_input("إجمالي المحفظة (SAR/USD)", value=100000)
risk_pct = st.sidebar.slider("نسبة المخاطرة لكل صفقة (%)", 0.5, 5.0, 1.0)

# --- مدخلات الصفقة ---
col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input("رمز السهم (مثال: 4009.SR أو TSLA)", "4009.SR")
with col2:
    stop_loss = st.number_input("مستوى وقف الخسارة (Anchor)", value=31.72)
with col3:
    target = st.number_input("الهدف الأول", value=39.36)

# --- جلب البيانات والتنفيذ ---
if st.button("تحليل الصفقة الآن"):
    with st.spinner('جاري سحب البيانات الحية...'):
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            current_price = round(data['Close'].iloc[-1], 2)
            rr, qty, cost, risk_amt = calculate_sef(current_price, stop_loss, target, balance, risk_pct)
            
            # عرض النتائج في كروت احترافية
            st.markdown("---")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("السعر اللحظي", f"{current_price}")
            kpi2.metric("نسبة العائد/المخاطرة", f"1:{round(rr, 2)}")
            kpi3.metric("الكمية المطلوبة", f"{qty} سهم")
            kpi4.metric("المخاطرة المالية", f"{round(risk_amt, 2)}")

            # رسالة التنبيه (وديع)
            if rr >= 3:
                st.success(f"✅ صفقة مطابقة لمعايير SEF. القيمة الإجمالية: {round(cost, 2)}")
            else:
                st.warning("⚠️ نسبة العائد للمخاطرة ضعيفة (أقل من 3). ابحث عن مرساة (Anchor) أفضل.")
            
            # رسم بياني بسيط
            st.line_chart(yf.Ticker(ticker).history(period="1mo")['Close'])
        else:
            st.error("تعذر جلب بيانات هذا الرمز. تأكد من إضافة .SR للأسهم السعودية.")

st.markdown("---")
st.caption("«إحنا بنغوص معهم لكن هم معهم أنبوبة أكسجين — نفسهم طويل. إحنا بنغرق يا وديع.»")
