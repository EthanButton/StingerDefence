import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.set_page_config(page_title="Stinger Defence", layout="wide")
st.title("🛡️ Stinger Defence")
st.caption("Global Defense Market Dashboard — Stocks, News & Companies")
st.markdown("---")

# ========== NEWS SECTION ==========
import streamlit as st
import pandas as pd
import re

st.subheader("📰 Latest Defense News")

@st.cache_data(ttl=1800)
def load_news():
    try:
        return pd.read_csv("data/defense_news.csv")
    except FileNotFoundError:
        return pd.DataFrame()

news_df = load_news()

if news_df.empty:
    st.warning("⚠️ No news data found.")
else:
    companies = sorted(news_df["company"].dropna().unique())
    selected_company = st.selectbox("Filter by Company", ["All"] + companies)

    filtered = news_df if selected_company == "All" else news_df[news_df["company"] == selected_company]
    filtered = filtered.sort_values(by="published", ascending=False)

    show_all = st.toggle("Show All News", value=False)
    news_to_show = filtered if show_all else filtered.head(5)

    st.caption(f"📰 Showing {'all' if show_all else 'latest 5'} news items for **{selected_company}**")

    for _, row in news_to_show.iterrows():
        with st.container():
            st.markdown(f"### [{row['title']}]({row['link']})")
            st.caption(f"📅 {row['published']} — 🏢 {row['company']}")

            # Simple smart summary based on keywords
            summary_parts = []

            # Detect financial mentions
            if re.search(r"\$\d+[.\d]*\s*(million|billion)?", row["title"], re.IGNORECASE):
                summary_parts.append("💰 Possible contract value mentioned.")

            # Detect domain-specific terms
            keywords = ["missile", "radar", "ship", "drone", "contract", "aircraft", "satellite", "cyber"]
            matches = [kw for kw in keywords if re.search(kw, row["title"], re.IGNORECASE)]

            if matches:
                summary_parts.append("🧩 Keywords: " + ", ".join(matches))

            if summary_parts:
                st.markdown("**🔍 Summary Insight:** " + " | ".join(summary_parts))

            st.markdown("---")

# ========== COMPANIES SECTION ==========
st.subheader("🏢 Global Defense Companies")

try:
    df_companies = pd.read_csv("data/defense_companies.csv")
    col1, col2 = st.columns(2)

    with col1:
        filter_country = st.multiselect("🌍 Filter by Country", sorted(df_companies["country"].unique()))
    with col2:
        search_term = st.text_input("🔎 Search Company Name")

    df_filtered = df_companies.copy()
    if filter_country:
        df_filtered = df_filtered[df_filtered["country"].isin(filter_country)]
    if search_term:
        df_filtered = df_filtered[df_filtered["name"].str.contains(search_term, case=False)]

    st.dataframe(df_filtered, use_container_width=True)
    fig = px.histogram(df_filtered, x="country", title="Number of Companies by Country")
    st.plotly_chart(fig, use_container_width=True)
except:
    st.warning("Company data not available.")

# ========== STOCK TRACKER ==========
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
        st.warning(f"⚠️ Skipped invalid/empty tickers: {', '.join(invalid_tickers)}")

    col1, col2 = st.columns(2)
    with col1:
        selected = st.selectbox("Select Company", list(name_to_ticker.keys()))
    with col2:
        horizon = st.selectbox("Select Time Range", ["7d", "1mo", "3mo", "6mo", "ytd", "1y"])

    ticker_data = yf.Ticker(name_to_ticker[selected])
    hist = ticker_data.history(period=horizon)

    st.metric(label=f"{selected} (Last Close)", value=f"${hist['Close'].iloc[-1]:.2f}")
    fig = px.line(hist, x=hist.index, y="Close", title=f"{selected} Stock Price")
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"📉 Could not load stock data: {e}")

# ========== FOOTER ==========
st.markdown("---")
st.caption("📡 Data from Yahoo Finance, Google News, and public sources. Auto-updates every 30 minutes.")
