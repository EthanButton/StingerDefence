import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
import re
import sys
import os
from streamlit.components.v1 import html

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.set_page_config(page_title="Stinger Defence", layout="wide")

st.title("Stinger Defence")
st.caption("Global Defense Market Dashboard — Stocks, News & Companies")

# ========== SITE OVERVIEW ==========
st.markdown("""
### What's Inside Stinger Defence
- **About Stinger Defence** — Mission and purpose
- **Live Market Snapshot** — Daily gainers & losers in defense stocks
- **Latest Defense News** — Headlines from major defense contractors
- **Global Defense Companies** — Interactive company list and stats
- **Stock & Index Tracker** — Compare performance over time
""")

st.markdown("---")

# ========== ABOUT SECTION ==========
st.markdown('<div id="about"></div>', unsafe_allow_html=True)
st.subheader("About Stinger Defence")
st.markdown("""
**Stinger Defence** is a data-driven aggregator focused on tracking the performance and developments of defence companies across the United States and Europe. Stinger Defence offers a unified platform to explore trends, company profiles, and industry activity within the global defence sector by sourcing from a range of reputable market data providers, public records, and news outlets.

This tool is intended for informational and educational purposes only.  
**It does not constitute financial advice or investment guidance.**
""")
st.markdown("---")

# ========== LIVE MARKET SNAPSHOT ==========
st.markdown('<div id="market"></div>', unsafe_allow_html=True)
st.subheader("Live Market Snapshot")
st.caption("Note: Changes reflect daily movement only.")

def get_price_data(label, ticker, period):
    try:
        stock = yf.Ticker(ticker)
        price = stock.info.get("regularMarketPrice", "N/A")
        change = stock.info.get("regularMarketChangePercent", 0.0)
        hist = stock.history(period=period)["Close"]
        return {
            "label": label,
            "ticker": ticker,
            "price": price,
            "change": change,
            "sparkline": hist if not hist.empty else None
        }
    except:
        return {
            "label": label,
            "ticker": ticker,
            "price": "N/A",
            "change": "N/A",
            "sparkline": None
        }

# Defense stocks
try:
    df_live = pd.read_csv("data/defense_companies.csv")
    df_live = df_live[df_live["ticker"].str.lower() != "not public"]
    stock_items = list(zip(df_live["name"], df_live["ticker"]))
except:
    stock_items = []

# Fetch and filter
trend_period = "1d"  # Default to daily
stock_data = [get_price_data(label, ticker, trend_period) for label, ticker in stock_items]

# Only keep your defined companies
your_companies = {
    "LMT", "RTX", "NOC", "GD", "LHX", "HII", "TXT", "LDOS", "MRCY", "KTOS",
    "CW", "CACI", "BA", "OSK", "BAESY", "HO.PA", "RNMBF", "SAAB-B.ST", "FINMY",
    "KOG.OL", "EADSY", "AM.PA", "HAG.DE"
}
stock_data = [item for item in stock_data if item["ticker"] in your_companies]

# Sort for winners and losers
gainers = sorted(stock_data, key=lambda x: x["change"] if isinstance(x["change"], (int, float)) else -999, reverse=True)
losers = sorted(stock_data, key=lambda x: x["change"] if isinstance(x["change"], (int, float)) else 999)

def render_metrics_block(data, title):
    st.markdown(f"#### {title}")
    table_data = []
    for item in data:
        label = item['label']
        ticker = item['ticker']
        price = item['price']
        change = item['change']

        price_str = f"${price:,.2f}" if isinstance(price, float) else "N/A"
        delta_str = f"{change:.2f}%" if isinstance(change, float) else "N/A"

        color = "green" if isinstance(change, float) and change >= 0 else "red"
        label_colored = f"<span style='color:{color}'>{label}</span>"

        table_data.append({
            "Company": label_colored,
            "Ticker": ticker,
            "Price": price_str,
            "Change": delta_str
        })

    df_table = pd.DataFrame(table_data)
    st.write("", unsafe_allow_html=True)
    st.write(df_table.to_html(escape=False, index=False), unsafe_allow_html=True)

# Show gainers and losers side-by-side
col1, col2 = st.columns(2)

with col1:
    render_metrics_block(gainers[:10], "Top Gainers (Daily Change)")

with col2:
    render_metrics_block(losers[:10], "Top Losers (Daily Change)")

# (You can continue your NEWS, COMPANIES, and STOCK TRACKER sections from here)

# ========== NEWS SECTION ==========
st.subheader("Latest Defense News")

@st.cache_data(ttl=1800)
def load_news():
    try:
        return pd.read_csv("data/defense_news.csv")
    except FileNotFoundError:
        return pd.DataFrame()

news_df = load_news()

if news_df.empty:
    st.warning("No news data found.")
else:
    companies = sorted(news_df["company"].dropna().unique())
    selected_company = st.selectbox("Filter by Company", ["All"] + companies)

    filtered = news_df if selected_company == "All" else news_df[news_df["company"] == selected_company]
    filtered = filtered.sort_values(by="published", ascending=False)

    show_all = st.toggle("Show All News", value=False)
    news_to_show = filtered if show_all else filtered.head(5)

    st.caption(f"Showing {'all' if show_all else 'latest 5'} news items for **{selected_company}**")

    for _, row in news_to_show.iterrows():
        with st.container():
            st.markdown(f"### [{row['title']}]({row['link']})")
            st.caption(f"{row['published']} — {row['company']}")

            summary_parts = []
            if re.search(r"\$\d+[.\d]*\s*(million|billion)?", row["title"], re.IGNORECASE):
                summary_parts.append("Possible contract value mentioned.")

            keywords = ["missile", "radar", "ship", "drone", "contract", "aircraft", "satellite", "cyber"]
            matches = [kw for kw in keywords if re.search(kw, row["title"], re.IGNORECASE)]

            if matches:
                summary_parts.append("Keywords: " + ", ".join(matches))

            if summary_parts:
                st.markdown("**Summary Insight:** " + " | ".join(summary_parts))

            st.markdown("---")

# ========== COMPANIES SECTION ==========
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

    st.dataframe(df_filtered, use_container_width=True)
    fig = px.histogram(df_filtered, x="country", title="Number of Companies by Country")
    st.plotly_chart(fig, use_container_width=True)
except:
    st.warning("Company data not available.")

# ========== STOCK TRACKER ==========
st.subheader("Stock & Index Tracker")

try:
    df_stocks = pd.read_csv("data/defense_companies.csv")
    df_stocks = df_stocks[df_stocks["ticker"].str.lower() != "not public"]
    stock_name_to_ticker = {row["name"]: row["ticker"] for _, row in df_stocks.iterrows()}

    index_tickers = {
        "S&P 500": "^GSPC", "Nasdaq 100": "^NDX", "Dow Jones": "^DJI",
        "Russell 2000": "^RUT", "FTSE 100": "^FTSE", "Euro Stoxx 50": "^STOXX50E",
        "DAX": "^GDAXI", "CAC 40": "^FCHI", "Nikkei 225": "^N225", "Hang Seng": "^HSI",
        "Stinger Defense Index": "STINGER_INDEX"
    }

    col1, col2 = st.columns(2)
    with col1:
        selected_stocks = st.multiselect("Select Defense Companies", list(stock_name_to_ticker.keys()))
    with col2:
        selected_indexes = st.multiselect("Select Indexes", list(index_tickers.keys()))

    col3, col4 = st.columns(2)
    with col3:
        horizon = st.selectbox("Time Range", [
            "1d", "5d", "1mo", "3mo", "6mo",
            "ytd", "1y", "2y", "5y", "10y", "max"
        ])
    with col4:
        normalize = st.checkbox("Normalize Prices (Start at 100%)", value=False)

    if selected_stocks or selected_indexes:
        fig = px.line(title="Price Comparison")
        skipped = []

        for name in selected_stocks:
            ticker = stock_name_to_ticker[name]
            try:
                data = yf.Ticker(ticker).history(period=horizon)
                if not data.empty:
                    series = data["Close"]
                    if normalize:
                        series = (series / series.iloc[0]) * 100
                    fig.add_scatter(x=series.index, y=series, mode="lines", name=name)
                else:
                    skipped.append(name)
            except:
                skipped.append(name)

        for name in selected_indexes:
            ticker = index_tickers[name]

            if ticker == "STINGER_INDEX":
                try:
                    index_series_list = []
                    for stock_name, stock_ticker in stock_name_to_ticker.items():
                        try:
                            data = yf.Ticker(stock_ticker).history(period=horizon)["Close"]
                            if not data.empty:
                                norm_series = (data / data.iloc[0]) * 100
                                norm_series.name = stock_name
                                index_series_list.append(norm_series)
                        except:
                            continue

                    if index_series_list:
                        combined_df = pd.concat(index_series_list, axis=1)
                        combined_df = combined_df.fillna(method="ffill").dropna()
                        combined_index = combined_df.mean(axis=1)

                        if normalize:
                            combined_index = (combined_index / combined_index.iloc[0]) * 100

                        fig.add_scatter(
                            x=combined_index.index,
                            y=combined_index.values,
                            mode="lines",
                            name="Stinger Defense Index"
                        )
                    else:
                        skipped.append("Stinger Defense Index")
                except:
                    skipped.append("Stinger Defense Index")
            else:
                try:
                    data = yf.Ticker(ticker).history(period=horizon)
                    if not data.empty:
                        series = data["Close"]
                        if normalize:
                            series = (series / series.iloc[0]) * 100
                        fig.add_scatter(x=series.index, y=series, mode="lines", name=name)
                    else:
                        skipped.append(name)
                except:
                    skipped.append(name)

        if skipped:
            st.warning(f"Skipped: {', '.join(skipped)}")

        st.plotly_chart(fig, use_container_width=True, key="main_price_chart")

        if "Stinger Defense Index" in selected_indexes:
            st.caption("The Stinger Defense Index is an informational, equal-weighted index of select global defense companies.")

        # ========== Dynamic Fundamentals Based on Horizon (Multiple Stocks) ==========
        if selected_stocks:
            st.markdown(f"## Fundamentals for Selected Stocks ({horizon})")

            for selected_name in selected_stocks:
                ticker = stock_name_to_ticker[selected_name]
                ticker_obj = yf.Ticker(ticker)
                hist = ticker_obj.history(period=horizon)

                if not hist.empty:
                    price_change = ((hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0]) * 100
                    latest_volume = hist["Volume"].iloc[-1] if "Volume" in hist.columns else "N/A"
                    info = ticker_obj.info

                    st.markdown(f"### {selected_name}")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Price Change", f"{price_change:.2f}%", delta=f"{hist['Close'].iloc[-1] - hist['Close'].iloc[0]:.2f}")
                    col2.metric("Volume", f"{latest_volume:,}" if latest_volume != "N/A" else "N/A")
                    col3.metric("Market Cap", f"${info.get('marketCap', 'N/A'):,}" if isinstance(info.get('marketCap'), int) else "N/A")
                    col4.metric("Beta", f"{info.get('beta', 'N/A')}")
                    st.markdown("---")
    else:
        st.info("Select at least one company or index to compare.")
except Exception as e:
    st.error(f"Could not load data: {e}")
