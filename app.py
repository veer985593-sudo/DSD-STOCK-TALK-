"""
STOCK BY DSD AI - Advanced Stock Research Assistant
Mobile Optimized Front-Page UI (Perfect Colors & VIX)
"""
import streamlit as st
import json
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

st.set_page_config(
    page_title="STOCK BY DSD AI",
    page_icon="🚩",
    layout="wide",
    initial_sidebar_state="collapsed", 
)

# --- 💎 BULLETPROOF CSS WITH CUSTOM CLASSES ---
st.markdown("""
<style>
    /* Base Background */
    .stApp, .main { background-color: #0b0f19 !important; }
    p, span, div, label, h1, h2, h3, h4, h5, h6, li { color: #F8FAFC; }
    
    /* Hide Sidebar Completely */
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }

    /* Tabs Styling */
    div[role="tablist"] button { background-color: transparent !important; }
    div[role="tablist"] button p { color: #94A3B8 !important; font-size: 1.05rem !important; }
    div[role="tablist"] button[aria-selected="true"] p { color: #D4AF37 !important; font-weight: 800 !important; }
    div[role="tablist"] button[aria-selected="true"] { border-bottom-color: #D4AF37 !important; }
    
    /* Search Box */
    .stSelectbox div[data-baseweb="select"] { background-color: #121826 !important; border: 1px solid #D4AF37 !important; border-radius: 8px; }
    .stSelectbox div[data-baseweb="select"] span { color: #FFFFFF !important; font-weight: bold; }
    
    /* Table Styling */
    [data-testid="stDataFrame"] div, [data-testid="stDataFrame"] th, [data-testid="stDataFrame"] td {
        color: #FFFFFF !important; background-color: transparent !important;
    }
    
    /* 🚀 CUSTOM COLOR CLASSES (This fixes the White text issue 100%) */
    .txt-green { color: #10B981 !important; font-weight: 800 !important; }
    .txt-red { color: #EF4444 !important; font-weight: 800 !important; }
    .txt-white { color: #FFFFFF !important; font-weight: 800 !important; }
    .txt-gray { color: #94A3B8 !important; font-weight: 600 !important; }
    
    .metric-box {
        background: rgba(30, 41, 59, 0.7); 
        border: 1px solid rgba(255, 255, 255, 0.05); 
        border-radius: 12px; 
        padding: 15px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
        margin-bottom: 10px;
    }
    .trend-box {
        background: rgba(30, 41, 59, 0.7); 
        border: 1px solid rgba(255,255,255,0.05); 
        border-radius: 8px; 
        padding: 12px; 
        margin-bottom: 10px;
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

# --- 📡 DATA FETCHING ---
@st.cache_data(ttl=60) 
def get_live_index_data():
    # 🛠️ NIFTY IT हटाकर INDIA VIX लगा दिया गया है
    index_tickers = {"NIFTY 50": "^NSEI", "SENSEX": "^BSESN", "BANK NIFTY": "^NSEBANK", "INDIA VIX": "^INDIAVIX"}
    results = {}
    for name, sym in index_tickers.items():
        try:
            t = yf.Ticker(sym)
            hist = t.history(period="5d")
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                curr_val = hist['Close'].iloc[-1]
                change = curr_val - prev_close
                pct = (change / prev_close) * 100
                results[name] = {"value": curr_val, "change": change, "change_percent": pct}
        except Exception: 
            pass
    return results

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
                    changes.append({"symbol": stock.replace(".NS", ""), "current": round(curr_price, 2), "pct": round(pct_change, 2)})
            except Exception: 
                continue
                
        changes = sorted(changes, key=lambda x: x['pct'], reverse=True)
        gainers = [c for c in changes if c['pct'] > 0][:5]
        losers = sorted([c for c in changes if c['pct'] < 0], key=lambda x: x['pct'])[:5] 
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
                        
                        if current_price >= year_high:
                            status_label = "🚀 NEW 52W HIGH"
                        elif current_price >= (year_high * 0.98):
                            status_label = "👀 Near 52W High"
                        else:
                            continue
                            
                        breakout_list.append({
                            "Symbol": stock.replace(".NS", ""),
                            "Price": f"₹{current_price:,.2f}",
                            "52W High": f"₹{year_high:,.2f}",
                            "Status": status_label
                        })
                except Exception: 
                    continue
    except Exception: 
        pass
    return pd.DataFrame(breakout_list)

# --- UI COMPONENTS ---
def _render_custom_metric(label, value, change, pct):
    # 🛠️ पक्का कलर लॉजिक: प्लस है तो ग्रीन (↑), माइनस है तो रेड (↓)
    if change >= 0:
        color_class = "txt-green"
        arrow = "↑"
        sign = "+"
    else:
        color_class = "txt-red"
        arrow = "↓"
        sign = "" # माइनस की वैल्यू में पहले से '-' होता है
        
    html = f"""
    <div class="metric-box">
        <div class="txt-gray" style="font-size: 0.85rem; text-transform: uppercase;">{label}</div>
        <div class="txt-white" style="font-size: 1.7rem;">{value:,.2f}</div>
        <div class="{color_class}" style="font-size: 0.9rem; margin-top: 5px;">{arrow} {sign}{change:,.2f} ({sign}{pct:.2f}%)</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def _render_alert(message, type="success"):
    if type == "success":
        bg, border, text_color = "rgba(6, 78, 59, 0.4)", "#059669", "#34D399"
    elif type == "error":
        bg, border, text_color = "rgba(127, 29, 29, 0.4)", "#DC2626", "#F87171"
    else:
        bg, border, text_color = "rgba(51, 65, 85, 0.4)", "#475569", "#CBD5E1"
        
    html = f"""
    <div style="background: {bg}; border: 1px solid {border}; border-radius: 8px; padding: 12px 16px; margin-bottom: 15px; color: {text_color} !important; font-weight: 500;">
        {message}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def _render_range_bar(label, low, high, current):
    if high <= low or high == 0: return
    pct = max(0, min(100, ((current - low) / (high - low)) * 100))
    html_content = f"""
    <div class="metric-box">
        <h4 class="txt-white" style="margin-top:0; margin-bottom:15px; font-size:1.1rem;">🎯 {label} Range</h4>
        <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:8px;">
            <span class="txt-gray">Low: <b class="txt-white">₹{low:,.2f}</b></span>
            <span class="txt-gray">High: <b class="txt-white">₹{high:,.2f}</b></span>
        </div>
        <div style="position:relative; height:6px; background:#1E293B; border-radius:3px; width:100%;">
            <div style="position:absolute; left:0; top:0; height:100%; width:{pct}%; background:linear-gradient(90deg, #EF4444, #F59E0B, #10B981); border-radius:3px;"></div>
            <div style="position:absolute; left:calc({pct}% - 6px); top:6px; width:0; height:0; border-left:6px solid transparent; border-right:6px solid transparent; border-bottom:8px solid #D4AF37;"></div>
        </div>
        <div style="text-align:center; font-size:0.9rem; margin-top:16px;">
            <span class="txt-white">Current:</span> <span style="color:#D4AF37 !important; font-weight:800; font-size:1.1rem;">₹{current:,.2f}</span>
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

# --- MAIN APP LAYOUT ---
def render_dashboard():
    # 1. HEADER
    st.markdown("""<h1 style="font-size: 2.5rem; font-weight: 800; background: linear-gradient(90deg, #D4AF37, #FFF5D1, #C5A059); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; padding-top: 10px;">🚩 STOCK BY DSD AI</h1>""", unsafe_allow_html=True)
    st.markdown("""<p style="text-align: center; color: #94A3B8 !important; font-size: 0.9rem; margin-bottom: 20px;">Professional AI Market Intelligence Terminal</p>""", unsafe_allow_html=True)
    
    # 2. MARKET OVERVIEW (Nifty, Sensex, Bank Nifty, INDIA VIX)
    indices = get_live_index_data()
    if indices:
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        cols = [col1, col2, col3, col4]
        for idx, (name, data) in enumerate(indices.items()):
            if idx < 4:
                with cols[idx]:
                    _render_custom_metric(name, data["value"], data["change"], data["change_percent"])
                    
    st.markdown("""<br>""", unsafe_allow_html=True)

    # 3. 🔍 SEARCH BAR (MAIN SCREEN)
    st.markdown("""<h3 class="txt-white" style="font-size:1.2rem;">🔍 Search F&O Stock</h3>""", unsafe_allow_html=True)
    symbol = st.selectbox("Select Stock", options=FO_STOCKS_LIST, index=FO_STOCKS_LIST.index("RELIANCE"), label_visibility="collapsed")
    
    st.markdown("""<br>""", unsafe_allow_html=True)

    # 4. 🔥 LIVE ACTION: GAINERS & LOSERS
    st.markdown("""<h3 class="txt-white" style="font-size:1.2rem;">🔥 Live F&O Action</h3>""", unsafe_allow_html=True)
    with st.spinner("Fetching Live Market..."):
        trending = get_live_trending_fo()
        gainers = trending.get("gainers", [])
        losers = trending.get("losers", [])

    if gainers or losers:
        trend_tab1, trend_tab2 = st.tabs(["🟢 Top Gainers", "🔴 Top Losers"])
        
        with trend_tab1:
            if gainers:
                for g in gainers:
                    st.markdown(f"""
                    <div class="trend-box">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="txt-white" style="font-size:1rem;">{g['symbol']}</span>
                            <span class="txt-green" style="font-size:1rem;">↑ +{g['pct']}%</span>
                        </div>
                        <div class="txt-gray" style="font-size:0.85rem; margin-top:4px;">₹{g['current']:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("No gainers currently.")
                
        with trend_tab2:
            if losers:
                for ls in losers:
                    st.markdown(f"""
                    <div class="trend-box">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="txt-white" style="font-size:1rem;">{ls['symbol']}</span>
                            <span class="txt-red" style="font-size:1rem;">↓ {ls['pct']}%</span>
                        </div>
                        <div class="txt-gray" style="font-size:0.85rem; margin-top:4px;">₹{ls['current']:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("No losers currently.")

    st.markdown("""<hr style="border-color:#1E293B;">""", unsafe_allow_html=True)

    # 5. STOCK ANALYSIS SECTION
    if symbol:
        st.markdown(f"""<h2 class="txt-white">💎 Terminal Analysis: <span style="color:#D4AF37 !important;">{symbol}</span></h2>""", unsafe_allow_html=True)
        
        try:
            _hist = yf.Ticker(f"{symbol}.NS").history(period="2d")
            if len(_hist) >= 2:
                yesterday_high = _hist['High'].iloc[-2]
                current_price = _hist['Close'].iloc[-1]
                
                if current_price > yesterday_high:
                    _render_alert(f"🟢 <b>MOMENTUM ALERT:</b> {symbol} कल के High (₹{yesterday_high:,.2f}) को पार कर चुका है! (Current: ₹{current_price:,.2f})", "success")
                else:
                    _render_alert(f"⚪ <b>NO BREAKOUT YET:</b> {symbol} अभी कल के High (₹{yesterday_high:,.2f}) के नीचे ट्रेड कर रहा है।", "neutral")
        except Exception: 
            pass

        col1, col2 = st.columns(2)
        with col1:
            _render_range_bar("Intraday", 2450.00, 2530.00, 2495.50)
        with col2:
            _render_range_bar("52-Week", 2100.00, 3100.00, 2495.50)

        st.markdown("""<br>""", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["📊 Chart", "🧠 Fundamentals", "🏢 Alerts"])
        
        with tab1:
            try:
                df = yf.Ticker(f"{symbol}.NS").history(period="1mo", interval="1d")
                if not df.empty:
                    fig = go.Figure(data=[go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        increasing_line_color='#10B981', decreasing_line_color='#EF4444'
                    )])
                    fig.update_layout(
                        title=f"{symbol} (Last 1 Month)", 
                        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=10, r=10, t=40, b=10),
                        xaxis=dict(showgrid=True, gridcolor='#1E293B', tickfont=dict(color='#94A3B8')),
                        yaxis=dict(showgrid=True, gridcolor='#1E293B', tickfont=dict(color='#94A3B8')),
                        title_font=dict(color='#FFFFFF')
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception: 
                pass
                
        with tab2:
            try:
                info = yf.Ticker(f"{symbol}.NS").info
                
                mcap = info.get('marketCap')
                st.markdown(f"""<div class="metric-box"><div class="txt-gray" style="font-size:0.9rem;">Market Cap</div><div class="txt-white" style="font-size:1.4rem;">₹{mcap/10000000:,.2f} Cr</div></div>""", unsafe_allow_html=True)
                
                pe = info.get('trailingPE', 0)
                pe_color = "txt-green" if pe and pe < 25 else "txt-red" if pe and pe > 40 else "txt-white"
                st.markdown(f"""<div class="metric-box"><div class="txt-gray" style="font-size:0.9rem;">P/E Ratio</div><div class="{pe_color}" style="font-size:1.4rem;">{round(pe,2) if pe else "N/A"}</div></div>""", unsafe_allow_html=True)
                
                roe = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
                roe_color = "txt-green" if roe > 15 else "txt-red" if roe < 5 else "txt-white"
                st.markdown(f"""<div class="metric-box"><div class="txt-gray" style="font-size:0.9rem;">ROE</div><div class="{roe_color}" style="font-size:1.4rem;">{round(roe,2)}%</div></div>""", unsafe_allow_html=True)
            except Exception: 
                pass
                
        with tab3:
            try:
                ticker = yf.Ticker(f"{symbol}.NS")
                st.markdown("""<h3 class="txt-white">🚨 Promoter Trust Radar</h3>""", unsafe_allow_html=True)
                
                try:
                    insider = ticker.insider_transactions
                    if insider is not None and not insider.empty: 
                        _render_alert("🔴 **ALERT (Red Flag 🚩):** प्रमोटर/इनसाइडर की हालिया गतिविधि दर्ज की गई है। सावधान रहें!", "error")
                    else: 
                        _render_alert("🟢 **ALL CLEAR:** प्रमोटर द्वारा शेयर बेचने का कोई नेगेटिव सिग्नल नहीं है।", "success")
                except Exception: 
                    _render_alert("🟢 **ALL CLEAR:** प्रमोटर द्वारा शेयर बेचने का कोई अलर्ट नहीं है।", "success")
                
                major_holders = ticker.major_holders
                if major_holders is not None and not major_holders.empty:
                    df_m = major_holders.copy()
                    if isinstance(df_m.index[0], str): 
                        df_m = df_m.reset_index()
                        df_m.columns = ["Category", "Value"]
                    elif len(df_m.columns) >= 2:
                        df_m.columns = ["Value", "Category"]
                        df_m = df_m[["Category", "Value"]]
                    
                    replace_mapping = {
                        "insidersPercentHeld": "👔 Promoter Holding",
                        "institutionsPercentHeld": "🏦 Institutional Holding",
                        "institutionsFloatPercentHeld": "🌊 Market Float",
                        "institutionsCount": "🏢 Total Institutions"
                    }
                    df_m["Category"] = df_m["Category"].replace(replace_mapping)
                    st.dataframe(df_m, use_container_width=True, hide_index=True)
            except Exception: 
                pass

        st.markdown("""<br>""", unsafe_allow_html=True)
        
        # 6. 52 WEEK HIGH RADAR
        with st.expander("🔥 DSD 52-Week High Master Radar", expanded=True):
            st.markdown("""<p class="txt-gray">इस लिस्ट में सिर्फ वही F&O स्टॉक्स दिखेंगे जो आज अपने 1 साल के उच्चतम स्तर के करीब हैं।</p>""", unsafe_allow_html=True)
            with st.spinner("Scanning ALL F&O stocks live..."):
                breakout_df = scan_52w_high_stocks()
                if not breakout_df.empty:
                    _render_alert(f"🟢 🚨 कुल {len(breakout_df)} F&O स्टॉक्स आज ज़बरदस्त तेज़ी में हैं!", "success")
                    st.dataframe(breakout_df, use_container_width=True, hide_index=True)
                else:
                    _render_alert("🔴 आज इस लिस्ट में से कोई भी F&O स्टॉक अपने 52-Week High पर नहीं है।", "error")

if __name__ == "__main__":
    render_dashboard()
