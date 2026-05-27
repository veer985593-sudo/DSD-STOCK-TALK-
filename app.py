"""
Streamlit Web UI for Stock Research Assistant
Beautiful dashboard for Indian stock market analysis
"""
import html as html_module
import streamlit as st
import json
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

# Must be first Streamlit command
st.set_page_config(
    page_title="DSD STOCK TALK™",

    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Import tools after streamlit config
from tools.market_data import get_stock_price, get_stock_info, get_historical_data, get_index_data, get_trending_stocks
from tools.news_scraper import get_stock_news
from tools.analysis import calculate_technical_indicators, get_fundamental_metrics, analyze_price_action
from tools.institutional import get_fii_dii_data, get_bulk_block_deals
from config import NIFTY50_STOCKS, SECTORS


# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FF9933, #FFFFFF, #138808);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .positive { color: #00C851; font-weight: bold; }
    .negative { color: #ff4444; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 5px;
    }
    .report-box {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 2rem 2.5rem;
        margin: 1rem 0;
        line-height: 1.7;
    }
    .report-box h1 { font-size: 1.6rem; margin-top: 0; }
    .report-box h2 { font-size: 1.3rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.4rem; }
    .report-box h3 { font-size: 1.1rem; }
    .report-box hr { border-color: rgba(255,255,255,0.08); }
</style>
""", unsafe_allow_html=True)


def format_number(num):
    """Format number in Indian style (lakhs, crores)."""
    if num is None or num == "N/A":
        return "N/A"
    try:
        num = float(num)
        if num >= 10_000_000:
            return f"₹{num/10_000_000:.2f} Cr"
        elif num >= 100_000:
            return f"₹{num/100_000:.2f} L"
        else:
            return f"₹{num:,.2f}"
    except (ValueError, TypeError):
        return str(num)


def get_trend_emoji(change):
    """Get emoji based on price change."""
    if change > 0:
        return "🟢"
    elif change < 0:
        return "🔴"
    return "⚪"


def _safe_val(value, prefix="", suffix=""):
    """Safely format a value for reports, handling None and N/A."""
    if value is None or value == "N/A":
        return "N/A"
    return f"{prefix}{value}{suffix}"


def _clean_report_markdown(report: str) -> str:
    """Clean up LLM-generated report for proper Streamlit rendering.

    Strips wrapping code fences that cause st.markdown to render
    the entire report as a monospace code block.
    """
    import re
    text = report.strip()
    # Remove wrapping ```markdown ... ``` or ``` ... ```
    text = re.sub(r'^```(?:markdown)?\s*\n', '', text)
    text = re.sub(r'\n```\s*$', '', text)
    return text.strip()


def generate_report_text(symbol: str, report_type: str, data: dict) -> str:
    """Generate a downloadable text report from analysis data."""
    if not data or not isinstance(data, dict):
        return f"Report for {symbol}: No data available."

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")

    if report_type == "technical":
        ma = data.get("moving_averages", {})
        momentum = data.get("momentum", {})
        volatility = data.get("volatility", {})
        sr = data.get("support_resistance", {})
        trend = data.get("trend", {})
        signals = data.get("signals", [])
        
        report = f"""
================================================================================
                    TECHNICAL ANALYSIS REPORT - {symbol}
================================================================================
Generated: {timestamp}
Source: Stock Research Assistant

OVERALL SIGNAL: {data.get('overall_signal', 'N/A')}
Signal Strength: {data.get('signal_strength', 'N/A')}

--------------------------------------------------------------------------------
MOVING AVERAGES
--------------------------------------------------------------------------------
SMA 20:  ₹{ma.get('sma_20', 'N/A')}
SMA 50:  ₹{ma.get('sma_50', 'N/A')}
SMA 200: ₹{ma.get('sma_200', 'N/A')}
Price vs SMA20: {ma.get('price_vs_sma20', 'N/A')}
Price vs SMA50: {ma.get('price_vs_sma50', 'N/A')}

--------------------------------------------------------------------------------
MOMENTUM INDICATORS
--------------------------------------------------------------------------------
RSI (14):        {momentum.get('rsi_14', 'N/A')} - {momentum.get('rsi_interpretation', 'N/A')}
MACD Line:       {momentum.get('macd_line', 'N/A')}
MACD Signal:     {momentum.get('macd_signal', 'N/A')}
Rate of Change:  {momentum.get('roc_10_day', 'N/A')}%

--------------------------------------------------------------------------------
VOLATILITY (BOLLINGER BANDS)
--------------------------------------------------------------------------------
Upper Band:  ₹{volatility.get('bollinger_upper', 'N/A')}
Middle Band: ₹{volatility.get('bollinger_middle', 'N/A')}
Lower Band:  ₹{volatility.get('bollinger_lower', 'N/A')}
BB Position: {volatility.get('bb_position', 'N/A')}
ATR %:       {volatility.get('atr_percent', 'N/A')}

--------------------------------------------------------------------------------
SUPPORT & RESISTANCE LEVELS
--------------------------------------------------------------------------------
Resistance 2: ₹{sr.get('resistance_2', 'N/A')}
Resistance 1: ₹{sr.get('resistance_1', 'N/A')}
Pivot:        ₹{sr.get('pivot', 'N/A')}
Support 1:    ₹{sr.get('support_1', 'N/A')}
Support 2:    ₹{sr.get('support_2', 'N/A')}

--------------------------------------------------------------------------------
TREND ANALYSIS
--------------------------------------------------------------------------------
Short-term:  {trend.get('short_term', 'N/A')}
Medium-term: {trend.get('medium_term', 'N/A')}
Long-term:   {trend.get('long_term', 'N/A')}
Golden Cross Active: {trend.get('golden_cross', 'N/A')}

--------------------------------------------------------------------------------
ACTIVE SIGNALS
--------------------------------------------------------------------------------
"""
        for sig in signals:
            report += f"- {sig.get('indicator', '')}: {sig.get('signal', '')} ({sig.get('strength', '')})\n"
        
        report += """
================================================================================
DISCLAIMER: This report is for educational purposes only. Not financial advice.
================================================================================
"""
        return report
    
    elif report_type == "fundamental":
        valuation = data.get("valuation") or {}
        profitability = data.get("profitability") or {}
        leverage = data.get("financial_health") or data.get("leverage") or {}
        growth = data.get("growth") or {}
        dividends = data.get("dividends") or {}
        size = data.get("size") or {}
        assessment = data.get("assessment") or []
        
        report = f"""
================================================================================
                   FUNDAMENTAL ANALYSIS REPORT - {symbol}
================================================================================
Generated: {timestamp}
Source: Stock Research Assistant

OVERALL RATING: {data.get('overall_rating', 'N/A')}
Valuation Status: {data.get('valuation_status', 'N/A')}

--------------------------------------------------------------------------------
VALUATION METRICS
--------------------------------------------------------------------------------
P/E Ratio:     {valuation.get('pe_ratio', 'N/A')}
P/B Ratio:     {valuation.get('pb_ratio', 'N/A')}
EV/EBITDA:     {valuation.get('ev_ebitda', 'N/A')}
Forward P/E:   {valuation.get('forward_pe', 'N/A')}
PEG Ratio:     {valuation.get('peg_ratio', 'N/A')}

--------------------------------------------------------------------------------
PROFITABILITY
--------------------------------------------------------------------------------
ROE:           {profitability.get('roe', 'N/A')}
ROA:           {profitability.get('roa', 'N/A')}
Gross Margin:  {profitability.get('gross_margin', 'N/A')}
Profit Margin: {profitability.get('profit_margin', 'N/A')}
Operating Margin: {profitability.get('operating_margin', 'N/A')}

--------------------------------------------------------------------------------
LEVERAGE & LIQUIDITY
--------------------------------------------------------------------------------
Debt/Equity:    {leverage.get('debt_to_equity', 'N/A')}
Current Ratio:  {leverage.get('current_ratio', 'N/A')}
Quick Ratio:    {leverage.get('quick_ratio', 'N/A')}

--------------------------------------------------------------------------------
GROWTH METRICS
--------------------------------------------------------------------------------
Earnings Growth:   {growth.get('earnings_growth', 'N/A')}
Revenue Growth:    {growth.get('revenue_growth', 'N/A')}
Quarterly EPS Growth: {growth.get('quarterly_earnings_growth', 'N/A')}

--------------------------------------------------------------------------------
DIVIDENDS
--------------------------------------------------------------------------------
Dividend Yield: {dividends.get('dividend_yield', 'N/A')}
Dividend Rate:  {dividends.get('dividend_rate', 'N/A')}
Payout Ratio:   {dividends.get('payout_ratio', 'N/A')}

--------------------------------------------------------------------------------
COMPANY SIZE
--------------------------------------------------------------------------------
Market Cap:       {size.get('market_cap', 'N/A')}
Enterprise Value: {size.get('enterprise_value', 'N/A')}
Revenue:          {size.get('revenue', 'N/A')}
EBITDA:           {size.get('ebitda', 'N/A')}

--------------------------------------------------------------------------------
KEY OBSERVATIONS
--------------------------------------------------------------------------------
"""
        for item in assessment:
            report += f"- {item.get('metric', '')}: {item.get('assessment', '')} [{item.get('impact', '')}]\n"
        
        report += """
================================================================================
DISCLAIMER: This report is for educational purposes only. Not financial advice.
================================================================================
"""
        return report
    
    return "Report not available"


def render_header():
    """Render the main header."""
    st.markdown('<h1 class="main-header">🇮🇳 Stock Research Assistant</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>AI-Powered Research for Indian Markets (NSE/BSE)</p>", unsafe_allow_html=True)
    st.divider()


def render_sidebar():
    """Render sidebar with stock selection."""
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/41/Flag_of_India.svg/1200px-Flag_of_India.svg.png", width=50)
        st.title("📊 Navigation")
        
        # Stock input
        st.subheader("🔍 Search Stock")
        symbol = st.text_input(
            "Enter Stock Symbol",
            placeholder="e.g., RELIANCE, TCS, INFY",
            help="Enter NSE stock symbol"
        ).upper().strip()
        
        # Trending stocks
        st.subheader("🔥 Trending Today")
        trending = get_trending_stocks()
        gainers = trending.get("gainers", [])
        losers = trending.get("losers", [])

        if gainers or losers:
            trend_tab1, trend_tab2 = st.tabs(["Top Gainers", "Top Losers"])

            with trend_tab1:
                for g in gainers[:5]:
                    sym = g.get("symbol", "")
                    chg = g.get("net_price", 0) or g.get("netPrice", 0)
                    st.markdown(f"**{sym}** :green[+{chg}%]")
                gainer_symbols = [g.get("symbol", "") for g in gainers[:5] if g.get("symbol")]
                selected_gainer = st.selectbox(
                    "Select gainer",
                    [""] + gainer_symbols,
                    format_func=lambda x: "Pick a stock..." if x == "" else x,
                    key="gainer_select",
                )
                if selected_gainer:
                    symbol = selected_gainer

            with trend_tab2:
                for ls in losers[:5]:
                    sym = ls.get("symbol", "")
                    chg = ls.get("net_price", 0) or ls.get("netPrice", 0)
                    st.markdown(f"**{sym}** :red[{chg}%]")
                loser_symbols = [ls.get("symbol", "") for ls in losers[:5] if ls.get("symbol")]
                selected_loser = st.selectbox(
                    "Select loser",
                    [""] + loser_symbols,
                    format_func=lambda x: "Pick a stock..." if x == "" else x,
                    key="loser_select",
                )
                if selected_loser:
                    symbol = selected_loser
        else:
            # Fallback to hardcoded list
            st.subheader("⚡ Quick Select")
            selected_stock = st.selectbox(
                "Popular Stocks",
                [""] + NIFTY50_STOCKS[:20],
                format_func=lambda x: "Select a stock..." if x == "" else x,
            )
            if selected_stock:
                symbol = selected_stock
        
        # Sector filter
        st.subheader("🏭 Browse by Sector")
        selected_sector = st.selectbox(
            "Sector",
            [""] + list(SECTORS.keys()),
            format_func=lambda x: "All Sectors" if x == "" else x
        )
        
        if selected_sector:
            sector_stocks = SECTORS.get(selected_sector, [])
            sector_stock = st.selectbox("Stocks", [""] + sector_stocks)
            if sector_stock:
                symbol = sector_stock
        
        st.divider()
        
        # Market status
        now = datetime.now()
        hour = now.hour
        if now.weekday() >= 5:
            status = "🔴 Market Closed (Weekend)"
        elif hour < 9 or (hour == 9 and now.minute < 15):
            status = "🟡 Pre-Market"
        elif hour < 15 or (hour == 15 and now.minute <= 30):
            status = "🟢 Market Open"
        else:
            status = "🔴 Market Closed"
        
        st.markdown(f"**Market Status:** {status}")
        st.markdown(f"**Last Updated:** {now.strftime('%H:%M:%S IST')}")
        
        st.divider()
        st.caption("⚠️ For educational purposes only. Not financial advice.")
        
        return symbol


def render_market_overview():
    """Render market overview section."""
    st.subheader("🏦 Market Overview")
    
    try:
        indices_data = json.loads(get_index_data.run("ALL"))
        
        col1, col2, col3, col4 = st.columns(4)
        
        index_cols = [
            ("NIFTY50", "NIFTY 50", col1),
            ("SENSEX", "SENSEX", col2),
            ("BANKNIFTY", "BANK NIFTY", col3),
            ("NIFTYIT", "NIFTY IT", col4),
        ]
        
        for key, name, col in index_cols:
            if key in indices_data:
                data = indices_data[key]
                value = data.get("value", 0)
                change = data.get("change", 0)
                change_pct = data.get("change_percent", 0)
                
                with col:
                    st.metric(
                        label=name,
                        value=f"{value:,.2f}",
                        delta=f"{change:+,.2f} ({change_pct:+.2f}%)"
                    )
    except Exception as e:
        st.warning(f"Could not fetch market data: {e}")


def _fetch_chart_data(symbol: str, period: str) -> pd.DataFrame:
    """Fetch OHLCV data from yfinance for charting.

    Returns a DataFrame with a **timezone-naive IST** DatetimeIndex.
    Intraday timestamps are shifted to interval-end so the last candle
    of the day reads 3:30 PM (market close).
    For 1D/1W the last candle's Close is patched with the official daily
    closing price so the chart endpoint matches the header price.
    """
    from tools.market_data import _get_nse_symbol
    from datetime import timedelta, time as dt_time

    MARKET_CLOSE = dt_time(15, 30)

    # (yfinance period, interval, timedelta to shift candle to end-of-interval)
    period_map = {
        "1D": ("5d", "5m", timedelta(minutes=5)),
        "1W": ("5d", "5m", timedelta(minutes=5)),
        "1M": ("1mo", "30m", timedelta(minutes=30)),
        "3M": ("3mo", "1h", timedelta(hours=1)),
        "6M": ("6mo", "1d", None),
        "1Y": ("1y", "1d", None),
        "5Y": ("5y", "1d", None),
    }
    yf_period, interval, shift = period_map.get(period, ("1y", "1d", None))

    try:
        ticker = yf.Ticker(_get_nse_symbol(symbol))
        df = ticker.history(period=yf_period, interval=interval)

        if df.empty:
            return df

        # Convert to naive IST (yfinance already returns Asia/Kolkata)
        if df.index.tz is not None:
            df.index = df.index.tz_convert("Asia/Kolkata").tz_localize(None)

        # Shift intraday candles to interval-end timestamps,
        # capping at 15:30 (market close) so the last bar is correct.
        if shift is not None:
            new_idx = df.index + shift
            capped = []
            for ts in new_idx:
                if ts.time() > MARKET_CLOSE:
                    ts = ts.replace(hour=15, minute=30, second=0, microsecond=0)
                capped.append(ts)
            df.index = pd.DatetimeIndex(capped)

        # For 1D, keep only the most recent trading day
        if period == "1D":
            last_date = df.index[-1].date()
            df = df[df.index.date == last_date]

        # Patch the last candle of each intraday day with the official
        # daily close so the chart endpoint matches the header price.
        # (15-min candles miss the closing auction.)
        if shift is not None:
            try:
                daily = ticker.history(period=yf_period, interval="1d")
                if daily.index.tz is not None:
                    daily.index = daily.index.tz_convert("Asia/Kolkata").tz_localize(None)
                daily_close_map = {d.date(): row["Close"] for d, row in daily.iterrows()}
                for i in range(len(df) - 1, -1, -1):
                    ts = df.index[i]
                    if ts.time() == MARKET_CLOSE:
                        official = daily_close_map.get(ts.date())
                        if official is not None:
                            df.iloc[i, df.columns.get_loc("Close")] = official
            except Exception:
                pass  # best-effort; fall back to candle data

        return df
    except Exception:
        return pd.DataFrame()


def _render_range_bar(label: str, low: float, high: float, current: float):
    """Render a horizontal range bar with a triangle marker via HTML/CSS."""
    if high <= low or high == 0:
        return

    pct = max(0, min(100, ((current - low) / (high - low)) * 100))

    html = f"""
    <div style="margin: 0.6rem 0;">
      <div style="display:flex; justify-content:space-between; font-size:0.82rem; color:#aaa; margin-bottom:2px;">
        <span>{label} Low — ₹{low:,.2f}</span>
        <span>₹{high:,.2f} — {label} High</span>
      </div>
      <div style="position:relative; height:6px; background:linear-gradient(90deg,#ff4444 0%,#ffcc00 50%,#00C851 100%); border-radius:3px;">
        <div style="position:absol
