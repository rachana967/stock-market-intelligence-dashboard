import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

st.set_page_config(page_title="Stock Market Intelligence", page_icon="📈", layout="wide")

# ---------- Styling ----------
st.markdown("""
<style>
    .stApp { background: #0b1220; color: #e5e7eb; }
    [data-testid="stSidebar"] { background: #111827; }
    div[data-testid="stMetric"] {
        background: #151f31; border: 1px solid #263449;
        padding: 16px; border-radius: 12px;
    }
    div[data-testid="stMetric"] label { color: #9ca3af; }
    h1, h2, h3 { color: #f8fafc; }
    .small-muted { color: #94a3b8; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Stock Market Intelligence Dashboard")
st.caption("Market monitoring • Historical performance • Risk analytics • Power BI-ready exports")

# ---------- Sidebar ----------
st.sidebar.header("Dashboard controls")
default_tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN"]
ticker_text = st.sidebar.text_input("Stock symbols (comma-separated)", ",".join(default_tickers))
tickers = list(dict.fromkeys([x.strip().upper() for x in ticker_text.split(",") if x.strip()]))
if not tickers:
    tickers = ["AAPL"]

period_label = st.sidebar.selectbox(
    "Historical period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3
)
interval = st.sidebar.selectbox("Data interval", ["1d", "1wk", "1mo"], index=0)
refresh = st.sidebar.button("🔄 Refresh market data", use_container_width=True)
if refresh:
    st.cache_data.clear()

@st.cache_data(ttl=300, show_spinner=False)
def load_prices(symbols, period, interval):
    raw = yf.download(
        tickers=symbols, period=period, interval=interval,
        auto_adjust=True, group_by="ticker", progress=False, threads=True
    )
    if raw is None or raw.empty:
        return pd.DataFrame()
    frames = []
    if isinstance(raw.columns, pd.MultiIndex):
        available = raw.columns.get_level_values(0).unique()
        for symbol in symbols:
            if symbol in available:
                one = raw[symbol].copy()
                one["Ticker"] = symbol
                one["Date"] = one.index
                frames.append(one.reset_index(drop=True))
    else:
        one = raw.copy()
        one["Ticker"] = symbols[0]
        one["Date"] = one.index
        frames.append(one.reset_index(drop=True))
    if not frames:
        return pd.DataFrame()
    result = pd.concat(frames, ignore_index=True)
    result["Date"] = pd.to_datetime(result["Date"]).dt.tz_localize(None)
    return result.dropna(subset=["Close"])

with st.spinner("Loading market data..."):
    prices = load_prices(tuple(tickers), period_label, interval)

if prices.empty:
    st.error("No market data returned. Check the ticker symbols or try again later.")
    st.info("Examples: AAPL (Apple), MSFT (Microsoft), RELIANCE.NS (Reliance Industries), TCS.NS (TCS).")
    st.stop()

prices = prices.sort_values(["Ticker", "Date"]).copy()
prices["Daily Return"] = prices.groupby("Ticker")["Close"].pct_change() * 100
prices["SMA 20"] = prices.groupby("Ticker")["Close"].transform(lambda s: s.rolling(20, min_periods=1).mean())
prices["SMA 50"] = prices.groupby("Ticker")["Close"].transform(lambda s: s.rolling(50, min_periods=1).mean())
prices["Daily Range"] = prices["High"] - prices["Low"]

latest_rows = prices.sort_values("Date").groupby("Ticker").tail(1)
primary = tickers[0]
primary_df = prices[prices["Ticker"] == primary].sort_values("Date")
if primary_df.empty:
    primary = prices["Ticker"].iloc[0]
    primary_df = prices[prices["Ticker"] == primary].sort_values("Date")

first_close = primary_df["Close"].iloc[0]
last_close = primary_df["Close"].iloc[-1]
period_return = (last_close / first_close - 1) * 100 if first_close else 0
daily_return = primary_df["Daily Return"].iloc[-1]
volatility = primary_df["Daily Return"].std() * np.sqrt(252) if primary_df["Daily Return"].notna().sum() > 1 else np.nan
avg_volume = primary_df["Volume"].mean() if "Volume" in primary_df else np.nan
latest_date = primary_df["Date"].iloc[-1].strftime("%d %b %Y")

st.markdown(f"**Selected stock:** `{primary}` &nbsp; | &nbsp; **Latest available trading date:** {latest_date}")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Latest close", f"{last_close:,.2f}", f"{daily_return:+.2f}%" if pd.notna(daily_return) else None)
c2.metric("Period return", f"{period_return:+.2f}%")
c3.metric("Annualised volatility", f"{volatility:.2f}%" if pd.notna(volatility) else "N/A")
c4.metric("Average volume", f"{avg_volume:,.0f}" if pd.notna(avg_volume) else "N/A")
c5.metric("Trading observations", f"{len(primary_df):,}")

st.divider()

left, right = st.columns([1.7, 1])
with left:
    st.subheader(f"{primary} — Price & moving averages")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=primary_df["Date"], y=primary_df["Close"], name="Close", line=dict(width=2)))
    fig.add_trace(go.Scatter(x=primary_df["Date"], y=primary_df["SMA 20"], name="SMA 20", line=dict(width=1.5, dash="dot")))
    fig.add_trace(go.Scatter(x=primary_df["Date"], y=primary_df["SMA 50"], name="SMA 50", line=dict(width=1.5, dash="dash")))
    fig.update_layout(template="plotly_dark", height=420, margin=dict(l=10,r=10,t=25,b=10),
                      paper_bgcolor="#0b1220", plot_bgcolor="#0b1220",
                      legend=dict(orientation="h", y=1.08), xaxis_title="", yaxis_title="Adjusted price")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Daily trading volume")
    volume_fig = go.Figure(go.Bar(x=primary_df["Date"], y=primary_df["Volume"], name="Volume"))
    volume_fig.update_layout(template="plotly_dark", height=420, margin=dict(l=10,r=10,t=25,b=10),
                             paper_bgcolor="#0b1220", plot_bgcolor="#0b1220",
                             xaxis_title="", yaxis_title="Shares traded", showlegend=False)
    st.plotly_chart(volume_fig, use_container_width=True)

st.subheader("Stock comparison")
comparison = prices.pivot(index="Date", columns="Ticker", values="Close").sort_index()
normalized = comparison.apply(lambda s: (s / s.dropna().iloc[0] * 100) if s.notna().any() else s)
compare_fig = go.Figure()
for symbol in normalized.columns:
    compare_fig.add_trace(go.Scatter(x=normalized.index, y=normalized[symbol], name=symbol, mode="lines"))
compare_fig.update_layout(template="plotly_dark", height=360, margin=dict(l=10,r=10,t=25,b=10),
                          paper_bgcolor="#0b1220", plot_bgcolor="#0b1220",
                          yaxis_title="Indexed price (start = 100)", xaxis_title="")
st.plotly_chart(compare_fig, use_container_width=True)

a, b = st.columns(2)
with a:
    st.subheader("Return distribution")
    returns = primary_df["Daily Return"].dropna()
    hist = go.Figure(go.Histogram(x=returns, nbinsx=35, name="Daily return"))
    hist.update_layout(template="plotly_dark", height=300, paper_bgcolor="#0b1220", plot_bgcolor="#0b1220",
                       xaxis_title="Daily return (%)", yaxis_title="Frequency")
    st.plotly_chart(hist, use_container_width=True)
with b:
    st.subheader("Latest market snapshot")
    snapshot = latest_rows[["Ticker", "Date", "Close", "Daily Return", "Volume"]].copy()
    snapshot["Date"] = pd.to_datetime(snapshot["Date"]).dt.strftime("%d %b %Y")
    snapshot = snapshot.rename(columns={"Close":"Latest close", "Daily Return":"Daily return (%)", "Volume":"Volume"})
    st.dataframe(snapshot, use_container_width=True, hide_index=True)

st.subheader("Historical data")
show_cols = [c for c in ["Date", "Ticker", "Open", "High", "Low", "Close", "Volume", "Daily Return", "SMA 20", "SMA 50"] if c in prices.columns]
st.dataframe(prices[show_cols].sort_values(["Date", "Ticker"], ascending=[False, True]),
             use_container_width=True, hide_index=True, height=300)

csv = prices[show_cols].to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download market data CSV (Power BI ready)", data=csv,
                   file_name="stock_market_data.csv", mime="text/csv")

st.caption("Data source: Yahoo Finance via yfinance. Data may be delayed or unavailable during market closures. This dashboard is for educational purposes only, not investment advice.")
