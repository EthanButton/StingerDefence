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

    stock_name_to_ticker = {}
    invalid_tickers = []

    for _, row in df_stocks.iterrows():
        ticker = row["ticker"]
        try:
            test = yf.Ticker(ticker).history(period="1d")
            if not test.empty:
                stock_name_to_ticker[row["name"]] = ticker
            else:
                invalid_tickers.append(row["name"])
        except:
            invalid_tickers.append(row["name"])

    if invalid_tickers:
        st.warning(f"⚠️ Skipped invalid or empty tickers: {', '.join(invalid_tickers)}")

    col1, col2 = st.columns(2)
    with col1:
        selected_stocks = st.multiselect("Select Stock(s)", list(stock_name_to_ticker.keys()))
    with col2:
        horizon = st.selectbox("Time Range", ["5d", "7d", "1mo", "3mo", "6mo", "ytd", "1y", "2y", "5y", "10y", "max"])

    if selected_stocks:
        for name in selected_stocks:
            ticker = stock_name_to_ticker[name]
            t = yf.Ticker(ticker)

            # Fundamentals
            info = t.info
            market_cap = info.get("marketCap", "N/A")
            beta = info.get("beta", "N/A")
            pe_ratio = info.get("trailingPE", "N/A")
            dividend_yield = info.get("dividendYield", 0)

            # Price change
            try:
                hist = t.history(period=horizon)
                if len(hist) >= 2:
                    start_price = hist["Close"].iloc[0]
                    end_price = hist["Close"].iloc[-1]
                    percent_change = ((end_price - start_price) / start_price) * 100
                    percent_change_str = f"{percent_change:.2f}%"
                else:
                    percent_change_str = "Not enough data"
            except:
                percent_change_str = "Error loading data"

            st.markdown(f"### 🧾 Fundamentals for **{name}**")
            st.markdown(f"""
            - 💰 **Market Cap**: {market_cap if isinstance(market_cap, str) else f"${market_cap:,.0f}"}
            - ⏱️ **Period**: {horizon}
            - 📊 **Price Change**: {percent_change_str}
            - 📉 **Beta**: {beta}
            - 🧮 **PE Ratio**: {pe_ratio}
            - 💸 **Dividend Yield**: {dividend_yield * 100:.2f}%
            """)

            # Line chart
            fig = px.line(hist, x=hist.index, y="Close", title=f"{name} Stock Price")
            st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"📉 Could not load stock data: {e}")
