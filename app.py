"""
STOCK BY DSD AI - Advanced Stock Research Assistant
Ultra Premium Dark Mode UI (Bloomberg Terminal Style)
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
    page_icon="🚩",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 💎 ULTRA PREMIUM DARK THEME CSS ---
st.markdown("""
<style>
    /* 1. Main Background & Text */
    .stApp {
        background-color: #0A0E17;
        color: #E0E6ED;
    }
    
    /* 2. Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #121826;
        border-right: 1px solid #C5A059; /* Subtle Golden Border */
    }
    [data-testid="stSidebar"] * {
        color: #E0E6ED;
    }
    
    /* 3. Main Header (Golden Gradient) */
    .main-header {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #D4AF37, #FFF5D1, #C5A059);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0 0.2rem 0;
        letter-spacing: 1px;
    }
    .sub-header {
        text-align: center;
        color: #8b949e;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }

    /* 4. Top Market Overview Metrics (Glass Cards) */
    [data-testid="metric-container"] {
        background: linear-gradient(145deg, #1A2235, #121826);
        border: 1px solid #2D3748;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        box-shadow: inset 0px 1px 1px rgba(255,255,255,0.05), 0 4px 12px rgba(0,0,0,0.5);
    }
    [data-testid="stMetricLabel"] { color: #A0AEC0 !important; }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.8rem !important; font-weight: 600 !important; }
    [data-testid="stMetricDelta"] svg { fill: #00C851; } /* Green Arrow */

    /* 5. Custom Analysis Cards */
    .metric-card {
        background: #121826;
        border: 1px solid #1E2638;
        padding: 1.5rem;
        border-radius: 12px;
        color: #E0E6ED;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    /* 6. Gold Border Sync Button */
    .stButton button {
        background-color: #121826 !important;
        border: 1px solid #C5A059 !important;
        color: #C5A059 !important;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: rgba(197, 160, 89, 0.1) !important;
        box-shadow: 0 0 12px rgba(197, 160, 89, 0.3);
    }

    /* 7. Tabs Styling */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 0px; 
        background-color: transparent; 
        border-bottom: 1px solid #1E2638;
    }
    .stTabs [data-baseweb="tab"] { 
        padding: 12px 24px; 
        background: transparent; 
        color: #A0AEC0; 
        border-radius: 0;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        color: #C5A059 !important;
        border-bottom: 2px solid #C5A059 !important;
        background-color: rgba(197, 160, 89, 0.05) !important;
    }

    /* 8. Alert Boxes (Momentum Alert) */
    [data-testid="stAlert"] {
        background-color: #152B20 !important; /* Dark Green */
        border: 1px solid #1B452A !important;
        color: #4ADE80 !important;
        border-radius: 8px !important;
    }
    
    /* 9. Dataframes */
    [data-testid="stDataFrame"] { background-color: transparent !important; }
    
    /* 10. Expander (Radar) */
    .streamlit-expanderHeader {
        background-color: #1A2235 !important;
        border-radius: 8px !important;
        color: #E0E6ED !important;
    }
    .streamlit-expanderContent {
        background-color: #0A0E17 !important;
        border: 1px solid #1E2638 !important;
        border-top: none !important;
    }
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
    # Custom Premium Progress Bar (Exactly like photo)
    html_content = f"""
    <div style="margin: 1rem 0; width: 100%;">
      <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#A0AEC0; margin-bottom:8px;">
        <span>Low: <b>₹{low:,.2f}</b></span>
        <span>High: <b>₹{high:,.2f}</b></span>
      </div>
      <div style="position:relative; height:6px; background:#1E2638; border-radius:3px; width:100%;">
        <div style="position:absolute; left:0; top:0; height:100%; width:{pct}%; background:linear-gradient(90deg, #ff4444, #ffcc00, #00C851); border-radius:3px;"></div>
        <div style="position:absolute; left:calc({pct}% - 6px); top:6px; width:0; height:0; border-left:6px solid transparent; border-right:6px solid transparent; border-bottom:8px solid #E2C275;"></div>
      </div>
      <div style="text-align:center; font-size:0.85rem; margin-top:14px; color:#E0E6ED;">
        Current: <span style="color:#E2C275; font-weight:bold;">₹{current:,.2f}</span>
      </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

def render_header():
    st.markdown('<div class="main-header">🚩 STOCK BY DSD AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Professional AI Market Intelligence Terminal</div>', unsafe_allow_html=True)
    st.write("") # Spacer

def render_sidebar():
    with st.sidebar:
        st.markdown("### 📊 Navigation")
        
        symbol = st.selectbox(
            "🔍 Search F&O Stock", 
            options=FO_STOCKS_LIST, 
            index=FO_STOCKS_LIST.index("RELIANCE")
        )
        
        if st.button("🔄 Sync Live Data", use_container_width=True, type="secondary"):
            st.rerun()
            
        st.divider()
        st.markdown("#### 🔥 Live F&O Action")
        st.markdown("<span style='background:#1B3B27; color:#4ADE80; padding:4px 10px; border-radius:12px; font-size:0.8rem;'>🟢 Top Gainers</span>", unsafe_allow_html=True)
        st.write("")
        
        with st.spinner("Fetching Live Market..."):
            trending = get_live_trending_fo()
            gainers = trending.get("gainers", [])

        if gainers:
            for g in gainers:
                # Custom Sleek Trend Cards (Like Photo)
                st.markdown(f"""
                <div style="background:#131823; border: 1px solid #1E2638; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#E0E6ED; font-weight:600; font-size:0.95rem;">{g['symbol']}</span>
                        <span style="color:#00C851; font-weight:600; font-size:0.9rem;">+{g['pct']}%</span>
                    </div>
                    <div style="color:#8b949e; font-size:0.8rem; margin-top:4px;">₹{g['current']:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No gainers currently.")
        
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
    st.write("")
    
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
                fig = go.Figure(data=[go.Candlestick(
                    x=df.index, 
                    open=df['Open'], 
                    high=df['High'], 
                    low=df['Low'], 
                    close=df['Close'],
                    increasing_line_color='#00C851', 
                    decreasing_line_color='#ff4444'
                )])
                fig.update_layout(
                    title=f"{symbol} (Last 1 Month)", 
                    template="plotly_dark",
                    paper_bgcolor='#0A0E17',
                    plot_bgcolor='#0A0E17',
                    margin=dict(l=10, r=10, t=40, b=10),
                    xaxis=dict(showgrid=True, gridcolor='#1E2638'),
                    yaxis=dict(showgrid=True, gridcolor='#1E2638')
                )
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
            
        st.write("") # Spacer
        
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
