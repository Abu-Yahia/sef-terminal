# 🛡️ SEF Terminal | Saudi Equities Framework
**An Institutional-Grade Technical Analysis & Risk Management Engine**

## 📌 Overview
SEF Terminal is a professional decision-support tool designed for traders in the Saudi (TASI) and US markets. Built on the **Saudi Equities Framework (SEF)**, the application filters market noise to focus on institutional "Anchor Levels" and strict Risk/Reward dynamics.

Inspired by Warren Buffett’s principle of "Margin of Safety," this terminal ensures that no trade is executed without a clear technical edge and a predefined invalidation point.

## 🚀 Key Features
- **Smart Money Anchor Detection:** Identifies high-volume clusters where institutional accumulation occurs.
- **Dynamic Risk/Reward Engine:** Automatically calculates position sizing based on portfolio heat and stop-loss distance.
- **Dual-Market Logic:** Handles TASI (Thursday Close) and USA (Friday Close) time-confirmation rules.
- **Live Data Integration:** Real-time price fetching via Yahoo Finance API.
- **Psychological Guardrails:** Built-in reminders to maintain trading discipline and prevent emotional decision-making.

## 🛠️ Tech Stack
- **Language:** Python 3.x
- **Framework:** [Streamlit](https://streamlit.io/)
- **Data Provider:** [yfinance](https://github.com/ranaroussi/yfinance)
- **Deployment:** Streamlit Community Cloud

## 📊 How It Works
1. **Input:** Enter the Ticker (e.g., `4009.SR` or `TSLA`), Anchor Level, and Target.
2. **Analysis:** The engine fetches live data and calculates the R:R ratio.
3. **Execution:** If the R:R is ≥ 3.0, the "Execute" signal is triggered with the exact number of shares to buy.
4. **Invalidation:** A clear "Wadie Alert" is issued if the price breaches the institutional floor.

## 📝 Disclaimer
*This tool is for educational and decision-support purposes only. Trading involves significant risk. Always perform your own due diligence.*

---
> "إحنا بنغوص معهم لكن هم معهم أنبوبة أكسجين — نفسهم طويل. إحنا بنغرق يا وديع."
