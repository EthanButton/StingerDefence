import streamlit as st
import pandas as pd
import plotly.express as px
from fetchers.fetch_dod_contracts import fetch_dod_contracts
import yfinance as yf
import time

st.set_page_config(page_title="Defense Watch", layout="wide")
st.title("🛡️ Defense Watch Dashboard")

# Optional: Auto-refresh every X seconds
REFRESH_INTERVAL = 300  # 5 minutes
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > REFRESH_INTERVAL:
    fetch_dod_contracts()
    st.session_state.last_refresh = time.time()

if st.button("🔄 Manually Refresh Contracts"):
    fetch_dod_contracts()
    st.success("Contracts updated.")

# Load and display contracts
st.subheader("📄 Recent U.S. Defense Contracts")
try:
    df_contracts = pd.read_csv("data/dod_contracts.csv")
    st.dataframe(df_contracts[["date", "title", "summary", "link"]])

    # Chart: Top companies mentioned
    companies = ["lockheed", "raytheon", "bae", "thales", "saab"]
    df_chart = pd.DataFrame([
        {"company": c.title(), "mentions": df_contracts["summary"].str.lower().str.contains(c).sum()}
        for c in companies
    ])
    fig_mentions = px.bar(df_chart, x="company", y="mentions", title="Company Mentions in Recent Contracts")
    st.plotly_chart(fig_mentions, use_container_width=True)

except Exception as e:
    st.warning("No contract data available.")

# Load and filter companies
st.subheader("🏢 Global Defense Companies")
try:
    df_companies = pd.read_csv("data/defense_companies.csv")
    sector_filter = st.multiselect("Filter by sector", options=df_companies["sector"].unique())
    country_filter = st.multiselect("Filter by country", options=df_companies["country"].unique())

    filtered_df = df_companies
    if sector_filter:
        filtered_df = filtered_df[filtered_df["sector"].isin(sector_filter)]
    if country_filter:
        filtered_df = filtered_df[filtered_df["country"].isin(country_filter)]

    st.dataframe(filtered_df)
    fig_sector = px.histogram(filtered_df, x="sector", title="Company Distribution by Sector")
    st.plotly_chart(fig_sector, use_container_width=True)
except:
    st.warning("No company data loaded.")

# Stock tracker
st.subheader("💹 Stock Tracker")
tickers = {
    "Lockheed Martin": "LMT",
    "Raytheon": "RTX",
    "BAE Systems": "BAESY",
    "Thales": "HO.PA",
    "Saab": "SAAB-B.ST"
}

selected_company = st.selectbox("Select a company", list(tickers.keys()))
if selected_company:
    ticker = yf.Ticker(tickers[selected_company])
    hist = ticker.history(period="1mo")
    current_price = hist["Close"].iloc[-1]
    st.metric(label=f"{selected_company} Stock Price (Last Close)", value=f"${current_price:.2f}")
    fig_stock = px.line(hist, x=hist.index, y="Close", title=f"{selected_company} Stock Price (Last 30 Days)")
    st.plotly_chart(fig_stock, use_container_width=True)

# Alerts
st.subheader("🚨 Contract Alerts")
if "df_contracts" in locals():
    alert_keywords = [name.lower() for name in tickers.keys()]
    recent_alerts = df_contracts[df_contracts["summary"].str.lower().str.contains('|'.join(alert_keywords))]
    if not recent_alerts.empty:
        st.error("⚠️ Companies mentioned in recent contracts!")
        st.dataframe(recent_alerts)
    else:
        st.success("✅ No tracked companies found in recent contracts.")

st.markdown("---")
st.markdown("📡 Built with verified, sourced data only. Sources: defense.gov, Yahoo Finance")
