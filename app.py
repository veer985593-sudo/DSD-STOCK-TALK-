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
</style>
""", unsafe_allow_html=True)

# --- 🚀 52-WEEK HIGH STRICT SCANNER ---
@st.cache_data(ttl=86400)
def scan_52w_high_stocks():
    nifty_stocks = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", 
        "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "LT.NS", "BAJFINANCE.NS",
        "AXISBANK.NS", "KOTAKBANK.NS", "MARUTI.NS", "SUNPHARMA.NS", "TATAMOTORS.NS",
        "M&M.NS", "ASIANPAINT.NS", "TITAN.NS", "HAL.NS", "ZOMATO.NS", "TRENT.NS",
        "ADANIENT.NS", "NTPC.NS", "POWERGRID.NS", "ULTRACEMCO.NS", "WIPRO.NS"
    ]
    
    breakout_list = []
    try:
        data = yf.download(nifty_stocks, period="1y", progress=False)
        if not data.empty:
            for stock in nifty_stocks:
                try:
                    close_prices = data['Close'][stock].dropna()
                    if len(close_prices) > 200: 
                        current_price = close_prices.iloc[-1]
                        year_high = close_prices.max()
                        
                        if current_price >= (year_high * 0.98): 
                            breakout_list.append({
                                "Symbol": stock.replace(".NS", ""),
                                "Current Price": f"₹{current_price:,.2f}",
                                "52W High": f"₹{year_high:,.2f}",
                                "Status": "🔥 52W High Breakout"
                            })
                except Exception:
                    continue
    except Exception:
        pass
    return pd.DataFrame(breakout_list)

# --- Fallback Functions ---
def get_trending_stocks():
    return {"gainers": [{"symbol": "RELIANCE", "net_price": 2.4}], "losers": [{"symbol": "TCS", "net_price": -1.8}]}

def get_index_data():
    return json.dumps({
        "NIFTY50": {"value": 24330.30, "change": 261.55, "change_percent": 1.05},
        "SENSEX": {"value": 78150.50, "change": 964.59, "change_percent": 1.25},
        "BANKNIFTY": {"value": 58520.10, "change": 939.15, "change_percent": 1.60},
        "NIFTYIT": {"value": 29220.80, "change": 504.00, "change_percent": 1.75}
    })

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
    # 🛠️ यहाँ नाम बदल दिया गया है! 
    st.markdown('<h1 class="main-header">🇮🇳 STOCK BY DSD AI</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>AI-Powered Research for Indian Markets (NSE/BSE)</p>", unsafe_allow_html=True)
    st.divider()

def render_sidebar():
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/41/Flag_of_India.svg/1200px-Flag_of_India.svg.png", width=50)
        st.title("📊 Navigation")
        
        st.subheader("🔍 Search Stock")
        
        POPULAR_STOCKS = [
            "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "SBIN", "BHARTIARTL", 
            "ITC", "LT", "BAJFINANCE", "AXISBANK", "KOTAKBANK", "MARUTI", "SUNPHARMA", 
            "TATAMOTORS", "M&M", "ASIANPAINT", "TITAN", "HAL", "ZOMATO", "TRENT", 
            "ADANIENT", "NTPC", "POWERGRID", "ULTRACEMCO", "WIPRO", "ONGC", "COALINDIA", 
            "HINDALCO", "TATASTEEL", "BAJAJ-AUTO", "RBLBANK", "YESBANK", "PNB", "SUZLON",
            "IRFC", "RVNL", "JIOFIN", "HCLTECH", "ADANIPORTS", "GRASIM", "TECHM", "CIPLA",
            "INDUSINDBK", "EICHERMOT", "DIVISLAB", "DRREDDY", "BAJAJFINSV", "HEROMOTOCO"
        ]
        POPULAR_STOCKS.sort()
        
        symbol = st.selectbox(
            "Enter Stock Symbol", 
            options=POPULAR_STOCKS, 
            index=POPULAR_STOCKS.index("RELIANCE")
        )
        
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

def render_market_overview():
    st.subheader("🏦 Market Overview")
    try:
        indices_data = json.loads(get_index_data())
        col1, col2, col3, col4 = st.columns(4)
        index_cols = [("NIFTY50", "NIFTY 50", col1), ("SENSEX", "SENSEX", col2), ("BANKNIFTY", "BANK NIFTY", col3), ("NIFTYIT", "NIFTY IT", col4)]
        
        for key, name, col in index_cols:
            if key in indices_data:
                data = indices_data[key]
                col.metric(label=name, value=f"{data['value']:,.2f}", delta=f"{data['change']:+,.2f} ({data['change_percent']:.2f}%)")
    except Exception as e:
        st.warning(f"Could not fetch market data: {e}")

def _fetch_chart_data(symbol: str) -> pd.DataFrame:
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

        tab1, tab2, tab3 = st.tabs(["Technical Analysis", "Fundamental Data", "Institutional Activity"])
        
        with tab1:
            df = _fetch_chart_data(symbol)
            if not df.empty:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(title=f"{symbol} 1-Month Candlestick Chart", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("Chart data not available.")
                
        with tab2:
            st.subheader(f"📊 {symbol} Fundamentals")
            try:
                with st.spinner("Fetching live fundamentals..."):
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
                
        with tab3:
            st.subheader(f"🏦 {symbol} Shareholding & Institutional Activity")
            try:
                with st.spinner("Fetching Institutional Data..."):
                    ticker = yf.Ticker(f"{symbol}.NS")
                    major_holders = ticker.major_holders
                    inst_holders = ticker.institutional_holders
                    
                    if major_holders is not None and not major_holders.empty:
                        st.markdown("### 📊 Major Holdings Breakdown")
                        
                        df_m = major_holders.copy()
                        if isinstance(df_m.index[0], str): 
                            df_m = df_m.reset_index()
                            df_m.columns = ["Category", "Value"]
                        elif len(df_m.columns) >= 2:
                            df_m.columns = ["Value", "Category"]
                            df_m = df_m[["Category", "Value"]]
                        
                        rename_dict = {
                            "insidersPercentHeld": "👔 Promoter Holding (प्रमोटर)",
                            "institutionsPercentHeld": "🏦 Institutional Holding (FII/DII)",
                            "institutionsFloatPercentHeld": "🌊 Market Float by Institutions",
                            "institutionsCount": "🏢 Total Institutions (संस्थाएं)"
                        }
                        df_m["Category"] = df_m["Category"].replace(rename_dict)
                        
                        def format_val(x):
                            try:
                                val = float(x)
                                if val <= 1.0 and val > 0:
                                    return f"{val*100:.2f}%"
                                return str(int(val))
                            except:
                                return x
                                
                        df_m["Value"] = df_m["Value"].apply(format_val)
                        
                        st.dataframe(df_m, use_container_width=True, hide_index=True)
                    else:
                        st.info("⚠️ इस स्टॉक का Major Holdings डेटा फ्री API पर उपलब्ध नहीं है।")
                        
                    if inst_holders is not None and not inst_holders.empty:
                        st.markdown("### 🏢 Top Institutional Holders (FII / DII)")
                        st.dataframe(inst_holders, use_container_width=True, hide_index=True)
                        
            except Exception:
                st.warning("⚠️ डेटा लोड करने में समस्या हुई।")
            
        st.divider()
        
        with st.expander("🔥 DSD 52-Week High Radar (Auto-Scanner)", expanded=True):
            st.markdown("इस लिस्ट में **सिर्फ वही** स्टॉक्स दिखेंगे जो आज अपने 1 साल के उच्चतम स्तर (High) पर हैं। बाकी स्टॉक्स फिल्टर कर दिए गए हैं।")
            
            with st.spinner("Scanning top stocks... (पहली बार में 15 सेकंड लग सकते हैं)"):
                breakout_df = scan_52w_high_stocks()
                
                if not breakout_df.empty:
                    st.success("🟢 🚨 ये स्टॉक्स आज ज़बरदस्त तेज़ी में हैं!")
                    st.dataframe(breakout_df, use_container_width=True, hide_index=True)
                else:
                    st.warning("🔴 आज इस लिस्ट में से कोई भी टॉप स्टॉक अपने 52-Week High पर नहीं है।")

if __name__ == "__main__":
    render_dashboard()
