import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.subheader("📰 Latest Defense News")

try:
    df_news = pd.read_csv("data/defense_news.csv")

    if df_news.empty:
        st.info("No news articles found.")
    else:
        for _, row in df_news.iterrows():
            st.markdown(f"**{row['company']}** — [{row['title']}]({row['link']})")
            st.caption(f"Published: {row['published']}")
            st.markdown("---")
except FileNotFoundError:
    st.warning("⚠️ News feed not available yet. Please wait for it to update.")

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
