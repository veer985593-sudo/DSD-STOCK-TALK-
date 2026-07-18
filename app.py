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
import re

# Must be first Streamlit command
st.set_page_config(
    page_title="DSD STOCK TALK™",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
        background: linear-gradient(135deg, #1e1e2f 0%, #252540 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
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

# Mock/Import placeholders for foundational configurations
NIFTY50_STOCKS = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "BHARTIARTL", "SBIN", "LICI", "ITC", "HINDUNILVR"]
SECTORS = {
    "IT": ["TCS", "INFY", "WIPRO", "HCLTECH"],
    "Banking": ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK"],
    "Energy": ["RELIANCE", "ONGC", "NTPC"]
}

# --- 🚀 52-Week High Scanner (With Volume) ---
@st.cache_data(ttl=86400) # हर 24 घंटे में सिर्फ एक बार अपडेट होगा (Safe for API)
def scan_52w_high_stocks():
    nifty_stocks = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", 
        "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "LT.NS", "BAJFINANCE.NS",
        "AXISBANK.NS", "KOTAKBANK.NS", "MARUTI.NS", "SUNPHARMA.NS", "TATAMOTORS.NS",
        "M&M.NS", "ASIANPAINT.NS", "TITAN.NS", "HAL.NS", "ZOMATO.NS", "TRENT.NS", "ADANIENT.NS"
    ]
    breakout_list = []
    try:
        data = yf.download(nifty_stocks, period="1y", progress=False)
        if not data.empty:
            for stock in nifty_stocks:
                try:
                    close_prices = data['Close'][stock].dropna()
                    volumes = data['Volume'][stock].dropna()
                    
                    if len(close_prices) > 200:
                        current_price = close_prices.iloc[-1]
                        year_high = close_prices.max()
                        
                        # अगर स्टॉक 52W High के 3% के अंदर है (ताकि कोई अच्छा स्टॉक मिस न हो)
                        if current_price >= (year_high * 0.97): 
                            current_vol = volumes.iloc[-1]
                            avg_vol_20 = volumes.tail(20).mean()
                            
                            # Volume चेक: अगर आज का वॉल्यूम 20-दिन के एवरेज से 50% ज़्यादा है, तो असली ब्रेकआउट
                            vol_status = "🔥 High Volume" if current_vol > (avg_vol_20 * 1.5) else "📊 Normal"
                            
                            breakout_list.append({
                                "Symbol": stock.replace(".NS", ""),
                                "Price": f"₹{current_price:,.2f}",
                                "52W High": f"₹{year_high:,.2f}",
                                "Distance": f"{((current_price/year_high)-1)*100:.1f}%",
                                "Volume Trend": vol_status
                            })
                except Exception:
                    continue
    except Exception:
        pass
    return pd.DataFrame(breakout_list)

# --- Mock/Fallback Functions for Interface Binding ---
def get_trending_stocks():
    return {"gainers": [{"symbol": "RELIANCE", "net_price": 2.4}], "losers": [{"symbol": "TCS", "net_price": -1.8}]}

def get_index_data():
    return json.dumps({
        "NIFTY50": {"value": 22450.30, "change": 120.4, "change_percent": 0.54},
        "SENSEX": {"value": 73900.50, "change": 410.2, "change_percent": 0.56},
        "BANKNIFTY": {"value": 47800.10, "change": -50.3, "change_percent": -0.10},
        "NIFTYIT": {"value": 35200.80, "change": 280.9, "change_percent": 0.80}
    })

def format_number(num):
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
    if change > 0: return "🟢"
    elif change < 0: return "🔴"
    return "⚪"

def _safe_val(value, prefix="", suffix=""):
    if value is None or value == "N/A": return "N/A"
    return f"{prefix}{value}{suffix}"

def _clean_report_markdown(report: str) -> str:
    text = report.strip()
    text = re.sub(r'^```(?:markdown)?\s*\n', '', text)
    text = re.sub(r'\n```\s*$', '', text)
    return text.strip()

def _render_range_bar(label: str, low: float, high: float, current: float):
    if high <= low or high == 0:
        return
    pct = max(0, min(100, ((current - low) / (high - low)) * 100))
    
    html_content = f"""
    <div style="margin: 0.8rem 0; width: 100%;">
      <div style="display:flex; justify-content:space-between; font-size:0.82rem; color:#aaa; margin-bottom:4px;">
        <span style="flex:1; text-align:left;">{label} Low: <b>₹{low:,.2f}</b></span>
        <span style="flex:1; text-align:right;">{label} High: <b>₹{high:,.2f}</b></span>
      </div>
      <div style="position:relative; height:8px; background:linear-gradient(90deg, #ff4444 0%, #ffcc00 50%, #00C851 100%); border-radius:4px; width:100%;">
        <div style="position:absolute; left:calc({pct}% - 6px); top:-4px; width:0; height:0; border-left:6px solid transparent; border-right:6px solid transparent; border-bottom:12px solid #fff;"></div>
      </div>
      <div style="text-align:center; font-size:0.85rem; color:#fff; margin-top:4px;">
        Current: <b>₹{current:,.2f}</b> ({pct:.1f}% of Range)
      </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

def render_header():
    st.markdown('<h1 class="main-header">🇮🇳 Stock Research Assistant</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>AI-Powered Research for Indian Markets (NSE/BSE)</p>", unsafe_allow_html=True)
    st.divider()

def render_sidebar():
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/41/Flag_of_India.svg/1200px-Flag_of_India.svg.png", width=50)
        st.title("📊 Navigation")
        
        st.subheader("🔍 Search Stock")
        symbol = st.text_input("Enter Stock Symbol", value="RELIANCE", placeholder="e.g., RELIANCE, TCS, INFY").upper().strip()
        
        # --- 🔄 REFRESH BUTTON ---
        if st.button("🔄 Refresh Live Data", use_container_width=True):
            st.rerun()
            
        st.subheader("🔥 Trending Today")
        trending = get_trending_stocks()
        gainers = trending.get("gainers", [])
        losers = trending.get("losers", [])

        if gainers or losers:
            trend_tab1, trend_tab2 = st.tabs(["Top Gainers", "Top Losers"])
            with trend_tab1:
                for g in gainers[:5]:
                    st.markdown(f"**{g['symbol']}** :green[+{g['net_price']}%]")
            with trend_tab2:
                for ls in losers[:5]:
                    st.markdown(f"**{ls['symbol']}** :red[{ls['net_price']}%]")
        
        st.divider()
        now = datetime.now()
        status = "🟢 Market Open" if (9 <= now.hour < 15 or (now.hour == 15 and now.minute <= 30)) and now.weekday() < 5 else "🔴 Market Closed"
        st.markdown(f"**Market Status:** {status}")
        return symbol

        with tab2:
            st.subheader(f"📊 {symbol} Fundamentals")
            try:
                with st.spinner("Fetching fundamentals..."):
                    info = yf.Ticker(f"{symbol}.NS").info
                    
                    f_col1, f_col2, f_col3 = st.columns(3)
                    mcap = info.get('marketCap')
                    f_col1.metric("Market Cap", f"₹{mcap/10000000:,.2f} Cr" if mcap else "N/A")
                    f_col2.metric("P/E Ratio", round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else "N/A")
                    roe = info.get('returnOnEquity')
                    f_col3.metric("ROE", f"{roe*100:.2f}%" if roe else "N/A")
                    
                    st.divider()
                    
                    f_col4, f_col5, f_col6 = st.columns(3)
                    f_col4.metric("Book Value", f"₹{info.get('bookValue', 'N/A')}")
                    f_col5.metric("Debt to Equity", info.get('debtToEquity', 'N/A'))
                    div = info.get('dividendYield')
                    f_col6.metric("Dividend Yield", f"{div*100:.2f}%" if div else "N/A")
            except Exception:
                st.warning("⚠️ इस स्टॉक का फंडामेंटल डेटा अभी उपलब्ध नहीं है।")

        index_cols = [("NIFTY50", "NIFTY 50", col1), ("SENSEX", "SENSEX", col2), ("BANKNIFTY", "BANK NIFTY", col3), ("NIFTYIT", "NIFTY IT", col4)]
        
        for key, name, col in index_cols:
            if key in indices_data:
                data = indices_data[key]
                col.metric(label=name, value=f"{data['value']:,.2f}", delta=f"{data['change']:+,.2f} ({data['change_percent']:.2f}%)")
    except Exception as e:
        st.warning(f"Could not fetch market data: {e}")

def _fetch_chart_data(symbol: str, period: str) -> pd.DataFrame:
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        df = ticker.history(period="1mo", interval="1d")
        return df
    except Exception:
        return pd.DataFrame()

def render_dashboard():
    render_header()
    render_market_overview()
    st.divider()
    
    symbol = render_sidebar()
    
    if symbol:
        st.header(f"📈 Dashboard Analysis for {symbol}")
        
        # --- 🚨 YESTERDAY HIGH BREAKOUT ALERT 🚨 ---
        try:
            _hist = yf.Ticker(f"{symbol}.NS").history(period="2d")
            if len(_hist) >= 2:
                yesterday_high = _hist['High'].iloc[-2]
                current_price = _hist['Close'].iloc[-1]
                
                if current_price > yesterday_high:
                    st.success(f"🟢 🚨 BREAKOUT: {symbol} कल के High (₹{yesterday_high:,.2f}) को तोड़कर ऊपर चल रहा है! (Current: ₹{current_price:,.2f}) 🚨 🟢")
                else:
                    st.error(f"🔴 🚨 NO BREAKOUT: {symbol} अभी कल के High (₹{yesterday_high:,.2f}) के नीचे है। (Current: ₹{current_price:,.2f}) 🚨 🔴")
        except Exception:
            pass
        # ---------------------------------------------

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("Intraday Session Range")
            _render_range_bar("Today", 2450.00, 2530.00, 2495.50)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("52-Week Structural Range")
            _render_range_bar("52W", 2100.00, 3100.00, 2495.50)
            st.markdown('</div>', unsafe_allow_html=True)

        # Tab layouts
        tab1, tab2, tab3, tab4 = st.tabs(["Technical Analysis", "Fundamental Data", "Institutional Activity", "🚀 52W High Scanner"])
        
        with tab1:
            st.write("Technical indicators configuration dashboard view.")
            df = _fetch_chart_data(symbol, "1M")
            if not df.empty:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(title=f"{symbol} Stock Movement", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                
        with tab2:
            st.write("Fundamental Metrics Overview section.")
            
        with tab3:
            st.write("FII / DII Historical Activity Track.")
            
        with tab4:
            st.subheader("🔥 52-Week High Breakout Scanner (With Volume)")
            st.markdown("यह लिस्ट हर 24 घंटे में **ऑटोमैटिक अपडेट** होती है। इसमें वे स्टॉक्स हैं जो अपने 1 साल के उच्चतम स्तर (High) के बेहद करीब हैं और वॉल्यूम के साथ ब्रेकआउट दे रहे हैं।")
            
            with st.spinner("Scanning top stocks... (दिन में पहली बार लोड होने में 10-15 सेकंड लग सकते हैं)"):
                breakout_df = scan_52w_high_stocks()
                
                if not breakout_df.empty:
                    st.dataframe(breakout_df, use_container_width=True, hide_index=True)
                else:
                    st.info("आज कोई भी स्टॉक अपने 52-Week High के आस-पास नहीं है।")

if __name__ == "__main__":
    render_dashboard()
