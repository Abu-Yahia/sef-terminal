import streamlit as st
import yfinance as yf
import pandas as pd
import math

# --- إعدادات الصفحة ---
st.set_page_config(page_title="SEF Terminal Pro", page_icon="🛡️", layout="wide")

# --- محرك التحليل الفني المتقدم ---
def get_technical_levels(ticker):
    try:
        data = yf.Ticker(ticker).history(period="6mo")
        if data.empty: return None, None, None, None
        
        # 1. تحديد الدعم والمقاومة (أعلى قمة وأدنى قاع لآخر 20 يوم)
        recent_20 = data.tail(20)
        resistance = recent_20['High'].max()
        support = recent_20['Low'].min()
        
        # 2. حساب المتوسط المؤسسي (المرساة)
        ema_200 = data['Close'].ewm(span=200, adjust=False).mean().iloc[-1]
        
        # 3. اكتشاف النماذج البسيطة
        last_close = data['Close'].iloc[-1]
        pattern = "محايد"
        if last_close > resistance * 0.98: pattern = "🔥 اختراق قريب"
        elif last_close < support * 1.02: pattern = "🛡️ ارتداد محتمل"
        
        return round(support, 2), round(resistance, 2), round(ema_200, 2), pattern
    except:
        return None, None, None, None

# --- الواجهة الرئيسية ---
st.title("🛡️ SEF Terminal | الرادار الفني")

st.sidebar.header("⚙️ إعدادات المحفظة")
balance = st.sidebar.number_input("إجمالي المحفظة", value=100000)
risk_pct = st.sidebar.slider("نسبة المخاطرة (%)", 0.5, 5.0, 1.0)

# --- منطقة المدخلات ---
col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input("رمز السهم (مثال: 4009.SR)", "4009.SR")
    if st.button("تفعيل الرادار الآلي 🛰️"):
        sup, res, ema, pat = get_technical_levels(ticker)
        if sup:
            st.session_state['stop_loss'] = sup
            st.session_state['pattern'] = pat
            st.info(f"الرادار اكتشف: دعم عند {sup} | مقاومة عند {res}")
        else:
            st.error("تعذر جلب البيانات")

with col2:
    # استخدام القيمة المكتشفة أو القيمة الافتراضية
    default_sl = st.session_state.get('stop_loss', 31.72)
    stop_loss = st.number_input("مستوى المرساة (Stop Loss)", value=float(default_sl))
with col3:
    target = st.number_input("الهدف المتوقع", value=39.36)

# --- تنفيذ التحليل ---
if st.button("تحليل الصفقة وعرض الشارت"):
    data = yf.Ticker(ticker).history(period="6mo")
    if not data.empty:
        current_price = round(data['Close'].iloc[-1], 2)
        
        # الحسابات المالية
        risk_per_share = abs(current_price - stop_loss)
        rr = (target - current_price) / risk_per_share if risk_per_share > 0 else 0
        qty = math.floor((balance * (risk_pct/100)) / risk_per_share) if risk_per_share > 0 else 0
        
        # عرض النتائج
        st.markdown(f"### الحالة الفنية: {st.session_state.get('pattern', 'جاري التحليل...')}")
        k1, k2, k3 = st.columns(3)
        k1.metric("السعر الحالي", current_price)
        k2.metric("نسبة العائد/المخاطرة", f"1:{round(rr, 2)}")
        k3.metric("الكمية المقترحة", f"{qty} سهم")

        # --- رسم الشارت مع الخطوط الفنية ---
        st.subheader("الشارت الفني المتقدم")
        # إضافة مستويات الدعم والمقاومة للشارت
        data['Support'] = stop_loss
        data['Resistance'] = target
        st.line_chart(data[['Close', 'Support', 'Resistance']])
        
        if rr >= 3:
            st.success("🎯 هذه الصفقة تطابق شروط SEF (مخاطرة منخفضة / عائد عالٍ)")
        else:
            st.warning("⚠️ انتبه: نسبة المخاطرة عالية جداً في هذا المستوى.")
    else:
        st.error("تأكد من رمز السهم بشكل صحيح")
