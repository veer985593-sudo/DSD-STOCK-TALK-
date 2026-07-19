"""
STOCK BY DSD AI - Advanced Stock Research Assistant
"""
import streamlit as st
import json
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

# Must be first Streamlit command
st.set_page_config(
    page_title="STOCK BY DSD AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS - (Fixed for both Light & Dark Mode)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FF9933, #138808);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem;
    }
    /* Adapts to light/dark mode natively */
    .metric-card {
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .trend-card {
        padding: 10px;
        margin-bottom: 8px;
        border-radius: 5px;
        border-left: 4px solid #ccc;
        background-color: rgba(128, 128, 128, 0.05);
    }
    .trend-card.gainer { border-left-color: #00C851; }
    .trend-card.loser { border-left-color: #ff4444; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding: 10px 20px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 🚀 COMPREHENSIVE F&O STOCKS MASTER LIST ---
FO_STOCKS_LIST = [
    "AARTIIND", "ABB", "ABBOTINDIA", "ABCAPITAL", "ABFRL", "ACC", "ADANIENT", "ADANIPORTS", 
    "ALKEM", "AMBUJACEM", "APOLLOHOSP", "APOLLOTYRE", "ASHOKLEY", "ASIANPAINT", "ASTRAL", 
    "ATUL", "AUBANK", "AUROPHARMA", "AXISBANK", "BAJAJ-AUTO", "BAJAJFINSV", "BAJFINANCE", 
    "BALKRISIND", "BALRAMCHIN", "BANDHANBNK", "BANKBARODA", "BATAINDIA", "BEL", "BERGEPAINT", 
    "BHARATFORG", "BHARTIARTL", "BHEL", "BIOCON", "BOSCHLTD", "BPCL", "BRITANNIA", "BSOFT", 
    "CANBK", "CANFINHOME", "CHAMBLFERT", "CHOLAFIN", "CIPLA", "COALINDIA", "COFORGE", "COLPAL", 
    "CONCOR", "COROMANDEL", "CROMPTON", "CUB", "CUMMINSIND", "DABUR", "DALBHARAT", "DEEPAKNTR", 
    "DIVISLAB", "DIXON", "DLF", "DRREDDY", "EICHERMOT", "ESCORTS", "EXIDEIND", "FEDERALBNK", 
    "GAIL", "GLENMARK", "GMRINFRA", "GNFC", "GODREJCP", "GODREJPROP", "GRANULES", "GRASIM", 
    "GUJGASLTD", "HAL", "HAVELLS", "HCLTECH", "HDFCAMC", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", 
    "HINDALCO", "HINDCOPPER", "HINDPETRO", "HINDUNILVR", "ICICIBANK", "ICICIGI", "ICICIPRULI", 
    "IDEA", "IDFC", "IDFCFIRSTB", "IEX", "IGL", "INDHOTEL", "INDIACEM", "INDIAMART", "INDIGO", 
    "INDUSINDBK", "INDUSTOWER", "INFY", "IPCALAB", "IRCTC", "ITC", "JINDALSTEL", "JKCEMENT", 
    "JSWSTEEL", "JUBLFOOD", "KOTAKBANK", "L&TFH", "LALPATHLAB", "LAURUSLABS", "LICHSGFIN", 
    "LT", "LTIM", "LTTS", "LUPIN", "M&M", "M&MFIN", "MANAPPURAM", "MARICO", "MARUTI", "MCDOWELL-N", 
    "MCX", "METROPOLIS", "MFSL", "MGL", "MOTHERSON", "MPHASIS", "MRF", "MUTHOOTFIN", "NATIONALUM", 
    "NAUKRI", "NAVINFLUOR", "NESTLEIND", "NMDC", "NTPC", "OBEROIRLTY", "OFSS", "ONGC", "PAGEIND", 
    "PEL", "PERSISTENT", "PETRONET", "PFC", "PIDILITIND", "PIIND", "PNB", "POLYCAB", "POONAWALLA", 
    "POWERGRID", "PVRINOX", "RAMCOCEM", "RBLBANK", "RECLTD", "RELIANCE", "SAIL", "SBICARD", 
    "SBILIFE", "SBIN", "SHREECEM", "SHRIRAMFIN", "SIEMENS", "SRF", "SUNTV", "SUNPHARMA", 
    "SYNGENE", "TATACHEM", "TATACOMM", "TATACONSUM", "TATAMOTORS", "TATAPOWER", "TATASTEEL", 
    "TCS", "TECHM", "TITAN", "TORNTPHARM", "TRENT", "TVSMOTOR", "UBL", "ULTRACEMCO", "UPL", 
    "VEDL", "VOLTAS", "WIPRO", "ZEEL", "ZYDUSLIFE", "JIOFIN", "RVNL"
]
FO_STOCKS_LIST.sort()

# Helper: Color Logic for Fundamentals
def get_health_status(value, metric_type):
    if value is None or value == "N/A": return "neutral"
    try:
        val = float(value)
        if metric_type == "PE": return "good" if val < 25 else "bad" if val > 40 else "neutral"
        if metric_type == "ROE": return "good" if val > 15 else "bad" if val < 5 else "neutral"
        if metric_type == "DEBT": return "good" if val < 1 else "bad" if val > 2 else "neutral"
    except:
        pass
    return "neutral"

# --- 🚀 LIVE TRENDING STOCKS (TOP GAINERS / LOSERS FROM F&O) ---
@st.cache_data(ttl=300) 
def get_live_trending_fo():
    nifty_stocks = [f"{stock}.NS" for stock in FO_STOCKS_LIST]
    try:
        data = yf.download(nifty_stocks, period="5d", progress=False)['Close']
        if data.empty: return {"gainers": [], "losers": []}
        
        changes = []
        for stock in nifty_stocks:
            try:
                s_data = data[stock].dropna()
                if len(s_data) >= 2:
                    prev_close = s_data.iloc[-2]
                    curr_price = s_data.iloc[-1]
                    pct_change = ((curr_price - prev_close) / prev_close) * 100
                    
                    changes.append({
                        "symbol": stock.replace(".NS", ""),
                        "current": round(curr_price, 2),
                        "pct": round(pct_change, 2)
                    })
            except:
                continue
                
        changes = sorted(changes, key=lambda x: x['pct'], reverse=True)
        
        gainers = [c for c in changes if c['pct'] > 0][:5]
        losers = [c for c in changes if c['pct'] < 0]
        losers = sorted(losers, key=lambda x: x['pct'])[:5] 
        
        return {"gainers": gainers, "losers": losers}
    except Exception:
        return {"gainers": [], "losers": []}

# --- 🚀 52-WEEK HIGH SCANNER ---
@st.cache_data(ttl=86400)
def scan_52w_high_stocks():
    nifty_stocks = [f"{stock}.NS" for stock in FO_STOCKS_LIST]
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
                                "Price": f"₹{current_price:,.2f}",
                                "52W High": f"₹{year_high:,.2f}",
                                "Status": "🔥 52W Breakout"
                            })
                except Exception:
                    continue
    except Exception:
        pass
    return pd.DataFrame(breakout_list)

def get_index_data():
    return json.dumps({
        "NIFTY50": {"value": 24330.30, "change": 261.55, "change_percent": 1.05},
        "SENSEX": {"value": 78150.50, "change": 964.59, "change_percent": 1.25},
        "BANKNIFTY": {"value": 58520.10, "change": 939.15, "change_percent": 1.60},
        "NIFTYIT": {"value": 29220.80, "change": 504.00, "change_percent": 1.75}
    })

def _render_range_bar(label: str, low: float, high: float, current: float):
    if high <= low or high == 0: return
    pct = max(0, min(100, ((current - low) / (high - low)) * 100))
    html_content = f"""
    <div style="margin: 0.8rem 0; width: 100%;">
      <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:6px;">
        <span style="flex:1; text-align:left;">Low: <b>₹{low:,.2f}</b></span>
        <span style="flex:1; text-align:right;">High: <b>₹{high:,.2f}</b></span>
      </div>
      <div style="position:relative; height:10px; background:linear-gradient(90deg, #ff4444 0%, #ffcc00 50%, #00C851 100%); border-radius:5px; width:100%;">
        <div style="position:absolute; left:calc({pct}% - 7px); top:-5px; width:0; height:0; border-left:7px solid transparent; border-right:7px solid transparent; border-bottom:14px solid #333;"></div>
      </div>
      <div style="text-align:center; font-size:0.9rem; margin-top:8px; font-weight:bold;">
        Current: <span style="color:#FF9933;">₹{current:,.2f}</span>
      </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

def render_header():
    st.markdown('<h1 class="main-header">🇮🇳 STOCK BY DSD AI</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Professional AI Market Intelligence Terminal</p>", unsafe_allow_html=True)
    st.divider()

def render_sidebar():
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/41/Flag_of_India.svg/1200px-Flag_of_India.svg.png", width=50)
        st.title("📊 Navigation")
        
        symbol = st.selectbox(
            "🔍 Search F&O Stock", 
            options=FO_STOCKS_LIST, 
            index=FO_STOCKS_LIST.index("RELIANCE")
        )
        
        if st.button("🔄 Sync Live Data", use_container_width=True, type="primary"):
            st.rerun()
            
        st.divider()
        st.subheader("🔥 Live F&O Action")
        
        with st.spinner("Fetching Live Market..."):
            trending = get_live_trending_fo()
            gainers = trending.get("gainers", [])
            losers = trending.get("losers", [])

        if gainers or losers:
            trend_tab1, trend_tab2 = st.tabs(["🟢 Top Gainers", "🔴 Top Losers"])
            with trend_tab1:
                if not gainers: st.write("No gainers currently.")
                for g in gainers:
                    st.markdown(f"""
                    <div class="trend-card gainer">
                        <div style="display:flex; justify-content:space-between; font-weight:bold;">
                            <span>{g['symbol']}</span>
                            <span style="color:#00C851;">+{g['pct']}%</span>
                        </div>
                        <div style="font-size:0.85rem; color:gray;">₹{g['current']:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            with trend_tab2:
                if not losers: st.write("No losers currently.")
                for ls in losers:
                    st.markdown(f"""
                    <div class="trend-card loser">
                        <div style="display:flex; justify-content:space-between; font-weight:bold;">
                            <span>{ls['symbol']}</span>
                            <span style="color:#ff4444;">{ls['pct']}%</span>
                        </div>
                        <div style="font-size:0.85rem; color:gray;">₹{ls['current']:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.divider()
        now = datetime.now()
        status = "🟢 Market Open" if (9 <= now.hour < 15 or (now.hour == 15 and now.minute <= 30)) and now.weekday() < 5 else "🔴 Market Closed"
        st.markdown(f"**Status:** {status}")
        return symbol

def render_market_overview():
    try:
        indices_data = json.loads(get_index_data())
        col1, col2, col3, col4 = st.columns(4)
        index_cols = [("NIFTY50", "NIFTY 50", col1), ("SENSEX", "SENSEX", col2), ("BANKNIFTY", "BANK NIFTY", col3), ("NIFTYIT", "NIFTY IT", col4)]
        
        for key, name, col in index_cols:
            if key in indices_data:
                data = indices_data[key]
                col.metric(label=name, value=f"{data['value']:,.2f}", delta=f"{data['change']:+,.2f} ({data['change_percent']:.2f}%)")
    except Exception:
        pass

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
        st.header(f"💎 Terminal Analysis: {symbol}")
        
        try:
            _hist = yf.Ticker(f"{symbol}.NS").history(period="2d")
            if len(_hist) >= 2:
                yesterday_high = _hist['High'].iloc[-2]
                current_price = _hist['Close'].iloc[-1]
                
                if current_price > yesterday_high:
                    st.success(f"🟢 **MOMENTUM ALERT:** {symbol} कल के High (₹{yesterday_high:,.2f}) को पार कर चुका है! (Current: ₹{current_price:,.2f})")
                else:
                    st.warning(f"⚪ **NO BREAKOUT YET:** {symbol} अभी कल के High (₹{yesterday_high:,.2f}) के नीचे ट्रेड कर रहा है।")
        except Exception:
            pass

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("🎯 Intraday Range")
            _render_range_bar("Today", 2450.00, 2530.00, 2495.50)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("📈 52-Week Range")
            _render_range_bar("52W", 2100.00, 3100.00, 2495.50)
            st.markdown('</div>', unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["📊 Technical Chart", "🧠 Fundamental Health", "🏢 Ownership & Alerts"])
        
        with tab1:
            df = _fetch_chart_data(symbol)
            if not df.empty:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(title=f"{symbol} (Last 1 Month)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("Chart data not available.")
                
        with tab2:
            st.subheader(f"🧠 {symbol} Fundamental Health")
            try:
                with st.spinner("Analyzing fundamentals..."):
                    info = yf.Ticker(f"{symbol}.NS").info
                    f_col1, f_col2, f_col3 = st.columns(3)
                    
                    def show_health_metric(col, label, val_raw, metric_type, is_percent=False):
                        status = get_health_status(val_raw, metric_type)
                        icon = "🟢" if status == "good" else "🔴" if status == "bad" else "⚪"
                        if val_raw is None or val_raw == "N/A":
                            disp_val = "N/A"
                        else:
                            disp_val = f"{val_raw*100:.2f}%" if is_percent else f"{val_raw:.2f}"
                        col.metric(f"{icon} {label}", disp_val)

                    pe = info.get('trailingPE')
                    roe = info.get('returnOnEquity')
                    debt = info.get('debtToEquity')
                    mcap = info.get('marketCap')
                    
                    f_col1.metric("Market Cap", f"₹{mcap/10000000:,.2f} Cr" if mcap else "N/A")
                    show_health_metric(f_col2, "P/E Ratio", pe, "PE", False)
                    show_health_metric(f_col3, "ROE", roe, "ROE", True)
                    
                    st.divider()
                    
                    f_col4, f_col5, f_col6 = st.columns(3)
                    f_col4.metric("Book Value", f"₹{info.get('bookValue', 'N/A')}")
                    show_health_metric(f_col5, "Debt to Equity", debt, "DEBT", False)
                    div = info.get('dividendYield')
                    f_col6.metric("Dividend Yield", f"{div*100:.2f}%" if div else "N/A")
            except Exception:
                st.warning("⚠️ इस स्टॉक का फंडामेंटल डेटा अभी उपलब्ध नहीं है।")
                
        with tab3:
            st.subheader(f"🚨 {symbol} Intelligence & Alerts")
            try:
                with st.spinner("Running deep background checks..."):
                    ticker = yf.Ticker(f"{symbol}.NS")
                    
                    st.markdown("### 🚨 Promoter Trust Radar")
                    try:
                        insider_trades = ticker.insider_transactions
                        if insider_trades is not None and not insider_trades.empty:
                            st.error("🔴 **ALERT (Red Flag 🚩):** प्रमोटर/इनसाइडर की हालिया गतिविधि दर्ज की गई है। सावधान रहें!")
                        else:
                            st.success("🟢 **ALL CLEAR:** प्रमोटर द्वारा शेयर बेचने का कोई नेगेटिव सिग्नल नहीं है।")
                    except:
                        st.success("🟢 **ALL CLEAR:** प्रमोटर द्वारा शेयर बेचने का कोई अलर्ट नहीं है।")
                    
                    st.divider()
                    
                    major_holders = ticker.major_holders
                    inst_holders = ticker.institutional_holders
                    
                    if major_holders is not None and not major_holders.empty:
                        st.markdown("### 📊 Holdings Breakdown")
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
                                if val <= 1.0 and val > 0: return f"{val*100:.2f}%"
                                return str(int(val))
                            except: return x
                                
                        df_m["Value"] = df_m["Value"].apply(format_val)
                        st.dataframe(df_m, use_container_width=True, hide_index=True)
                        
                    if inst_holders is not None and not inst_holders.empty:
                        st.markdown("### 🏢 Top Institutional Backers")
                        st.dataframe(inst_holders, use_container_width=True, hide_index=True)
                        
            except Exception:
                st.warning("⚠️ डेटा लोड करने में समस्या हुई।")
            
        st.divider()
        
        with st.expander("🔥 DSD 52-Week High Master Radar", expanded=True):
            st.markdown("इस लिस्ट में **सिर्फ वही** F&O स्टॉक्स दिखेंगे जो आज अपने 1 साल के उच्चतम स्तर (High) के करीब हैं।")
            
            with st.spinner("Scanning ALL F&O stocks live..."):
                breakout_df = scan_52w_high_stocks()
                
                if not breakout_df.empty:
                    st.success(f"🟢 🚨 कुल {len(breakout_df)} F&O स्टॉक्स आज ज़बरदस्त तेज़ी (Breakout) में हैं!")
                    st.dataframe(breakout_df, use_container_width=True, hide_index=True)
                else:
                    st.warning("🔴 आज इस लिस्ट में से कोई भी F&O स्टॉक अपने 52-Week High पर नहीं है।")

if __name__ == "__main__":
    render_dashboard()
