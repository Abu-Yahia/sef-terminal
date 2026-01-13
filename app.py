import streamlit as st
import yfinance as yf
import pandas as pd
import math

# --- إعدادات الصفحة ---
st.set_page_config(page_title="SEF Terminal v2.0", page_icon="🛡️", layout="wide")

# --- محرك التحليل الفني الآلي ---
def get_auto_anchor(ticker):
    try:
        data = yf.Ticker(ticker).history(period="1y")
        if data.empty: return None
        # حساب المتوسط المتحرك 200 يوم (مرساة بافيت)
        ema_200 = data['Close'].ewm(span=200, adjust=False).mean().iloc[-1]
        return round(ema_200, 2)
    except:
        return None

def calculate_sef(current_price, stop_loss, target, balance, risk_pct):
    risk_per_share = abs(current_price - stop_loss)
    reward_per_share = abs(target - current_price)
    rr_ratio = reward_per_share / risk_per_share if risk_per_share > 0 else 0
    cash_to_risk = balance * (risk_pct / 100)
    qty = math.floor(cash_to_risk / risk_per_share) if risk_per_share > 0 else 0
    total_cost = qty * current_price
    return rr_ratio, qty, total_cost, cash_to_risk

# --- واجهة التطبيق ---
st.title("🛡️ SEF Terminal | النسخة المطورة")
st.sidebar.header("⚙️ إعدادات المحفظة")
balance = st.sidebar.number_input("إجمالي المحفظة", value=100000)
risk_pct = st.sidebar.slider("نسبة المخاطرة (%)", 0.5, 5.0, 1.0)

# --- مدخلات الصفقة ---
col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input("رمز السهم", "4009.SR")
    if st.button("اكتشاف المرساة آلياً 🤖"):
        suggested_anchor = get_auto_anchor(ticker)
        if suggested_anchor:
            st.info(f"المرساة المقترحة (EMA 200): {suggested_anchor}")
        else:
            st.error("تعذر جلب البيانات")

with col2:
    stop_loss = st.number_input("مستوى وقف الخسارة (Anchor)", value=31.72)
with col3:
    target = st.number_input("الهدف الأول", value=39.36)

if st.button("تحليل الصفقة الآن"):
    data = yf.Ticker(ticker).history(period="6mo")
    if not data.empty:
        current_price = round(data['Close'].iloc[-1], 2)
        rr, qty, cost, risk_amt = calculate_sef(current_price, stop_loss, target, balance, risk_pct)
        
        st.markdown("---")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("السعر اللحظي", current_price)
        k2.metric("نسبة R:R", f"1:{round(rr, 2)}")
        k3.metric("الكمية", f"{qty} سهم")
        k4.metric("المخاطرة", round(risk_amt, 2))

        if rr >= 3:
            st.success(f"✅ صفقة ذهبية! إجمالي التكلفة: {round(cost, 2)}")
        else:
            st.warning("⚠️ العائد ضعيف مقارنة بالمخاطرة.")
        
        # رسم بياني فني مع خط المرساة
        st.subheader("تحليل الشارت الفني")
        data['EMA_200'] = data['Close'].ewm(span=200, adjust=False).mean()
        st.line_chart(data[['Close', 'EMA_200']])
    else:
        st.error("خطأ في الرمز")
