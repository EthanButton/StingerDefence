import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from fetchers.fetch_dod_contracts import fetch_dod_contracts
import time
import os

st.set_page_config(page_title="Defense Watch", layout="wide")
st.title("🛡️ Defense Watch: Global Defense Market Tracker")

# --- Auto-refresh every X seconds ---
REFRESH_INTERVAL = 300
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
if time.time() - st.session_state.last_refresh > REFRESH_INTERVAL:
    try:
        fetch_dod_contracts()
        st.session_state.last_refresh = time.time()
    except:
        st.warning("⚠️ Failed to auto-refresh DoD contracts.")

if st.button("🔄 Refresh Contracts Now"):
    try:
        fetch_dod_contracts()
        st.success("Contracts updated.")
    except:
        st.error("Failed to update contracts.")

# --- Load contracts ---
st.subheader("📄 Latest U.S. Defense Contracts")
try:
    df_contracts = pd.read_csv("data/dod_contracts.csv")
    st.dataframe(df_contracts[["date", "title", "summary", "link"]])

    companies = pd.read_csv("data/defense_companies.csv")["name"].str.lower()
    matched_contracts = df_contracts[df_contracts["summary"].str.lower().apply(
        lambda s: any(name in s for name in companies)
    )]
    if not matched_contracts.empty:
        st.error("⚠️ Recent contracts include tracked companies!")
        st.dataframe(matched_contracts)
    else:
        st.success("✅ No tracked companies found in recent contracts.")
except Exception as e:
    st.warning("No contract data available. Scraper may not have run yet.")

# --- Company data ---
st.subheader("🏢 Global Defense Companies")
try:
    df_companies = pd.read_csv("data/defense_companies.csv")
    col1, col2 = st.columns(2)
    with col1:
        sector_filter = st.multiselect("Filter by Country", options=sorted(df_companies["country"].unique()))
    with col2:
        search_term = st.text_input("Search Company Name")

    filtered = df_companies.copy()
    if sector_filter:
        filtered = filtered[filtered["country"].isin(sector_filter)]
    if search_term:
        filtered = filtered[filtered["name"].str.contains(search_term, case=False)]

    st.dataframe(filtered)
    fig = px.histogram(filtered, x="country", title="Companies by Country")
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.warning("No company data loaded.")

# --- Stock tracker ---
st.subheader("📈 Stock Tracker")

try:
    df_tickers = pd.read_csv("data/defense_companies.csv")
    public_df = df_tickers[df_tickers["ticker"].str.lower() != "not public"]
    name_to_ticker = dict(zip(public_df["name"], public_df["ticker"]))

    col1, col2 = st.columns(2)
    with col1:
        selected = st.selectbox("Select a company", list(name_to_ticker.keys()))
    with col2:
        horizon = st.selectbox("Select time range", ["7d", "1mo", "3mo", "6mo", "ytd", "1y"])

    ticker = yf.Ticker(name_to_ticker[selected])
    hist = ticker.history(period=horizon)

    st.metric(label=f"{selected} (Last Close)", value=f"${hist['Close'].iloc[-1]:.2f}")
    fig = px.line(hist, x=hist.index, y="Close", title=f"{selected} Stock Price")
    st.plotly_chart(fig, use_container_width=True)
except:
    st.warning("📉 Could not load stock data. Ticker may be invalid or unavailable.")

st.markdown("---")
st.caption("📡 Data from defense.gov, Yahoo Finance, and open sources. Auto-updates every 30 min.")
