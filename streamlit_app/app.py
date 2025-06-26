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
# ===== CUSTOM STYLES =====
st.markdown("""
<style>
.yellow-divider {
    border-top: 2px solid #FFCC00;
    margin-top: 2em;
    margin-bottom: 2em;
    width: 100%;
}
.red-down { color: red; font-weight: normal; }
.green-up { color: green; font-weight: bold; }
.positive { color: green; font-weight: bold; }
.negative { color: red; }
td, th { padding: 6px 12px; text-align: left; }
table { width: 100%; border-collapse: collapse; }
</style>
""", unsafe_allow_html=True)

# ========== What's Inside ==========
st.markdown("""
### What's Inside
- **About Stinger Defence**
- **Latest Defense News** — Headlines from the global defense industry
- **Market & Companies Overview** — Sortable, color-coded daily stock data with movement indicators
- **Global Defense Companies** — Filterable directory of major defense firms
- **Stock & Index Tracker** — Compare historical price trends  
  ↳ *Fundamentals for Selected Stocks*
""")
st.markdown("<div class='yellow-divider'></div>", unsafe_allow_html=True)

# ========== ABOUT SECTION ==========
st.markdown('<div id="about"></div>', unsafe_allow_html=True)
st.subheader("About Stinger Defence")
st.markdown("""
**Stinger Defence** is a data-driven aggregator focused on tracking the performance and developments of defence companies across the United States and Europe. Stinger Defence offers a unified platform to explore trends, company profiles, and industry activity within the global defence sector by sourcing from a range of reputable market data providers, public records, and news outlets.

This tool is intended for informational and educational purposes only.  
**It does not constitute financial advice or investment guidance.**
""")
st.markdown("<div class='yellow-divider'></div>", unsafe_allow_html=True)

# ===== HEADLINES & GEOPOLITICAL NOTE =====
st.markdown("### Headlines & Geopolitical Note")
st.markdown("""
NATO leaders today affirmed the 5 percent of GDP defense spending framework at the summit in The Hague. The commitment (3.5 percent for core military, 1.5 percent for infrastructure and cybersecurity) continues to catalyze defense investment across member states :contentReference[oaicite:5]{index=5}.
Germany unveiled a 700 million dollar ammunition plant deal in Lithuania, executed jointly with Rheinmetall. This initiative supports regional resilience and aligns with broader NATO supply chain goals :contentReference[oaicite:6]{index=6}.
The EU’s Readiness 2030 program was reconfirmed, allocating up to 800 billion euros over two years to reinforce industrial capacity, joint procurement, and cyber defense across Europe :contentReference[oaicite:7]{index=7}.
No significant conflict emerged today, allowing markets to focus on strategic budget implementation, European defense industrial partnerships, and execution of long-term procurement—maintaining the positive tone established after the NATO summit.
""")

# ========== NEWS SECTION ==========
st.markdown('<div id="news"></div>', unsafe_allow_html=True)
st.subheader("Latest Defense News")

import re
import pandas as pd

@st.cache_data(ttl=1800)
def load_news():
    try:
        return pd.read_csv("data/defense_news.csv")
    except FileNotFoundError:
        return pd.DataFrame()

# Full list of your defense companies
valid_companies = sorted([
    "Lockheed Martin", "Raytheon Technologies", "Northrop Grumman", "General Dynamics",
    "L3Harris Technologies", "Huntington Ingalls Industries", "Textron", "Leidos",
    "Mercury Systems", "Kratos Defense", "Curtiss-Wright", "CACI International",
    "Boeing", "Oshkosh Corporation", "BAE Systems", "Thales", "Rheinmetall",
    "Saab AB", "Leonardo S.p.A.", "Kongsberg Gruppen", "Airbus", "Dassault Aviation",
    "Hensoldt AG", "Elbit Systems", "Babcock International", "Serco Group",
    "Rolls-Royce Holdings", "QinetiQ Group", "MTU Aero Engines"
])

news_df = load_news()

if news_df.empty:
    st.warning("No news data found.")
else:
    # Filter dropdown to only show valid companies from your list that exist in the data
    available_companies = sorted(set(news_df["company"].dropna()) & set(valid_companies))
    selected_company = st.selectbox("Filter by Company", ["All"] + available_companies)

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

            if re.search(r"\$\d+[\.\d]*\s*(million|billion)?", row["title"], re.IGNORECASE):
                summary_parts.append("Possible contract value mentioned.")

            keywords = ["missile", "radar", "ship", "drone", "contract", "aircraft", "satellite", "cyber", "$", "million", "billion"]
            matches = [kw for kw in keywords if re.search(kw, row["title"], re.IGNORECASE)]

            if matches:
                summary_parts.append("Keywords: " + ", ".join(matches))

            if summary_parts:
                st.markdown("**Summary Insight:** " + " | ".join(summary_parts))

            st.markdown("<div class='yellow-divider'></div>", unsafe_allow_html=True)

# ========== MARKET & COMPANIES OVERVIEW ==========
st.markdown('<div id="market"></div>', unsafe_allow_html=True)
st.subheader("Market & Companies Overview (Live)")
st.caption("Includes real-time price, % change, volume, market cap, P/E ratio, 52-week change — click Refresh to update")

# Manual refresh button
if st.button("Refresh Now"):
    st.rerun()
@st.cache_data(ttl=10)
def fetch_live_data():
    df = pd.read_csv("data/defense_companies.csv")
    df = df[df["ticker"].str.lower() != "not public"]
    # EXCLUDE index tickers before processing
    exclude_tickers = ["^GSPC", "^NDX", "^DJI", "^RUT", "^FTSE", "^STOXX50E", "^GDAXI", "^FCHI", "^N225", "^HSI", "STINGER_INDEX"]
    df = df[~df["ticker"].isin(exclude_tickers)]

    data = []
    for _, row in df.iterrows():
        try:
            stock = yf.Ticker(row["ticker"])
            info = stock.info
            current = {
                "Company": row["name"],
                "Ticker": row["ticker"],
                "Price": info.get("regularMarketPrice", "N/A"),
                "Change %": info.get("regularMarketChangePercent", 0.0),
                "Volume": info.get("volume", "N/A"),
                "Market Cap": info.get("marketCap", "N/A"),
                "P/E Ratio": info.get("trailingPE", "N/A"),
                "52W Change": info.get("52WeekChange", "N/A")
            }
            data.append(current)
        except:
            continue

    df_live = pd.DataFrame(data)
    df_live["Indicator"] = df_live["Change %"].apply(
        lambda x: f"<span class='green-up'>&#9650;</span>" if isinstance(x, float) and x > 0 else (
                  f"<span class='red-down'>&#9660;</span>" if isinstance(x, float) and x < 0 else "")
    )
    df_live["Change % Raw"] = df_live["Change %"]
    df_live["Change %"] = df_live["Change %"].apply(lambda x: f"{x:.2f}%" if isinstance(x, float) else "N/A")
    df_live["Price"] = df_live["Price"].apply(lambda x: f"${x:,.2f}" if isinstance(x, (float, int)) else "N/A")
    df_live["Volume"] = df_live["Volume"].apply(lambda x: f"{int(x):,}" if isinstance(x, (int, float)) else "N/A")
    df_live["Market Cap"] = df_live["Market Cap"].apply(lambda x: f"${int(x):,}" if isinstance(x, (int, float)) else "N/A")
    df_live["P/E Ratio"] = df_live["P/E Ratio"].apply(lambda x: f"{x:.2f}" if isinstance(x, (float, int)) else "N/A")
    df_live["52W Change"] = df_live["52W Change"].apply(lambda x: f"{x*100:.2f}%" if isinstance(x, float) else "N/A")
    return df_live

# ======================== Display Section ========================

def render_table(df):
    def colorize(val):
        try:
            if isinstance(val, str) and "%" in val:
                num = float(val.strip('%').replace(',', ''))
            elif isinstance(val, str) and val.startswith('$'):
                num = float(val.strip('$').replace(',', ''))
            else:
                num = float(val)
            css = "positive" if num > 0 else "negative"
            return f"<td class='{css}'>{val}</td>"
        except:
            return f"<td>{val}</td>"

    headers = ''.join(f"<th>{col}</th>" for col in df.columns if col != "Change % Raw")
    rows = []
    for _, row in df.iterrows():
        html_row = "<tr>"
        for col in df.columns:
            if col == "Change % Raw":
                continue
            html_row += colorize(row[col])
        html_row += "</tr>"
        rows.append(html_row)
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"

try:
    df_live_display = fetch_live_data()

    # ====== Company Search ======
    st.markdown("#### Filter Companies by Name")
    company_search = st.text_input("Enter full or partial name:")
    if company_search:
        df_live_display = df_live_display[df_live_display["Company"].str.contains(company_search, case=False)]

    # ====== Sorting Options ======
    sort_options = ["Change %", "Price", "Volume", "Market Cap", "P/E Ratio", "52W Change"]
    sort_by = st.selectbox("Sort by metric:", sort_options, index=0)
    ascending = st.radio("Sort order:", ["Descending", "Ascending"]) == "Ascending"

    sort_col_map = {
        "Change %": "Change % Raw",
        "Price": "Price",
        "Volume": "Volume",
        "Market Cap": "Market Cap",
        "P/E Ratio": "P/E Ratio",
        "52W Change": "52W Change"
    }
    sort_col = sort_col_map[sort_by]
    df_live_display = df_live_display.sort_values(by=sort_col, ascending=ascending)

    df_live_display.drop(columns=["Change % Raw"], inplace=True)

    # ====== Table Display ======
    st.markdown("""
    <style>
    .stDataFrame tbody td div { font-size: 15px; }
    table { width: 100%; border-collapse: collapse; margin-top: 1em; }
    th { text-align: left; padding: 6px 10px; font-weight: bold; border-bottom: 1px solid #444; }
    td { padding: 6px 10px; }
    .positive { color: green; font-weight: bold; }
    .negative { color: red; }
    </style>
    """, unsafe_allow_html=True)

    st.write(render_table(df_live_display), unsafe_allow_html=True)

except Exception as e:
    st.warning(f"Live stock data unavailable. Error: {e}")

# ===== MARKET & COMPANIES NOTE =====
st.markdown("### Market & Companies Note")
st.markdown("""
Today’s trading showed positive momentum across key U.S. defense names, backed by NATO and industrial developments in Europe.
Lockheed Martin LMT climbed near 461 dollars on strengthening sentiment around LRDR and Golden Dome production momentum. Raytheon Technologies RTX rose to about 143 dollars after recent U.S. Navy radar contract deliveries.
Northrop Grumman NOC jumped to nearly 496 dollars following news of expanded ammunition co production in Lithuania and ongoing development of integrated air defense systems. General Dynamics GD advanced toward 292 dollars, supported by its ongoing submarine support contract.
In Europe, Rheinmetall shares edged higher as Germany committed to build a 155 mm ammunition plant in Lithuania and brokered a strategic partnership with India’s Reliance Defense. BAE Systems saw a modest uptick amid increased U.K. procurement and confirmation of its role in the Global Combat Air Programme with Leonardo. Leonardo remained elevated as Italy demonstrated its commitment to the GCAP timeline and funding.
Overall, both U.S. and European defense equities sustained gains reflecting supportive spending policies, active procurement, and cross border cooperation.
""")

st.markdown("<div class='yellow-divider'></div>", unsafe_allow_html=True)
# ========== COMPANIES SECTION ==========
st.subheader("Global Defense Companies")

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
st.markdown("<div class='yellow-divider'></div>", unsafe_allow_html=True)

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
