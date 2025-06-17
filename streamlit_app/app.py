import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from fetchers.fetch_dod_contracts import fetch_dod_contracts
import time

st.set_page_config(page_title="Defense Watch", layout="wide")
st.title("🛡️ Defense Watch: Global Defense Market Tracker")

# Auto-refresh contracts every 30 minutes
REFRESH_INTERVAL = 1800
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
if time.time() - st.session_state.last_refresh > REFRESH_INTERVAL:
    try:
        fetch_dod_contracts()
        st.session_state.last_refresh = time.time()
    except:
        st.warning("⚠️ Could not auto-refresh DoD contracts.")

if st.button("🔄 Refresh Contracts Now"):
    try:
        fetch_dod_contracts()
        st.success("Contracts updated.")
    except:
        st.error("❌ Failed to update contracts.")

# --- Load contract data ---
st.subheader("📄 Latest U.S. Defense Contracts")
try:
    df_contracts = pd.read_csv("data/dod_contracts.csv")
    st.dataframe(df_contracts[["date", "title", "summary", "link"]])

    companies = pd.read_csv("data/defense_companies.csv")["name"].str.lower()
    matched = df_contracts[df_contracts["summary"].str.lower().apply(lambda s: any(name in s for name in companies))]

    if not matched.empty:
        st.error("⚠️ Recent contracts include tracked companies:")
        st.dataframe(matched)
    else:
        st.success("✅ No tracked companies found in recent contracts.")
except Exception as e:
    st.warning("No contract data available. Waiting for update.")

# --- Load company list ---
st.subheader("🏢 Global Defense Companies")
try:
    df_companies = pd.read_csv("data/defense_companies.csv")
    col1, col2 = st.columns(2)
    with col1:
        filter_country = st.multiselect("Filter by Country", sorted(df_companies["country"].unique()))
    with col2:
        search_term = st.text_input("Search Company Name")

    df_filtered = df_companies.copy()
    if filter_country:
        df_filtered = df_filtered[df_filtered["country"].isin(filter_country)]
    if search_term:
        df_filtered = df_filtered[df_filtered["name"].str.contains(search_term, case=False)]

    st.dataframe(df_filtered)
    fig = px.histogram(df_filtered, x="country", title="Companies by Country")
    st.plotly_chart(fig, use_container_width=True)
except:
    st.warning("Company data not available.")

# --- Stock tracker ---
st.subheader("📈 Stock Tracker")

try:
    df_stocks = pd.read_csv("data/defense_companies.csv")
    df_stocks = df_stocks[df_stocks["ticker"].str.lower() != "not public"]

    name_to_ticker = {}
    invalid_tickers = []

    for _, row in df_stocks.iterrows():
        ticker = row["ticker"]
        try:
            test = yf.Ticker(ticker).history(period="1d")
            if not test.empty:
                name_to_ticker[row["name"]] = ticker
            else:
                invalid_tickers.append(row["name"])
        except:
            invalid_tickers.append(row["name"])

    if invalid_tickers:
        st.warning(f"⚠️ Skipped invalid or empty tickers: {', '.join(invalid_tickers)}")

    col1, col2 = st.columns(2)
    with col1:
        selected = st.selectbox("Select a Company", list(name_to_ticker.keys()))
    with col2:
        horizon = st.selectbox("Time Range", ["7d", "1mo", "3mo", "6mo", "ytd", "1y"])

    ticker_data = yf.Ticker(name_to_ticker[selected])
    hist = ticker_data.history(period=horizon)

    st.metric(label=f"{selected} (Last Close)", value=f"${hist['Close'].iloc[-1]:.2f}")
    fig = px.line(hist, x=hist.index, y="Close", title=f"{selected} Stock Price")
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"📉 Could not load stock data: {e}")

st.markdown("---")
st.caption("📡 Data from defense.gov, Yahoo Finance, and public sources. Auto-updates every 30 min.")
