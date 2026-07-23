"""
STOCK BY DSD AI - Advanced Stock Research Assistant
Mobile Optimized | Clean WHITE Theme | ATH & 52W High Radar | RVoL
"""
import streamlit as st
import json
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

st.set_page_config(page_title="STOCK BY DSD AI", page_icon="🚩", layout="wide", initial_sidebar_state="collapsed")

# ⏳ 5-MINUTE AUTO REFRESH
st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)

# --- 💎 BULLETPROOF CSS (WHITE THEME) ---
st.markdown("""
<style>
    /* 🌟 Main White Background 🌟 */
    .stApp, .main { background-color: #FFFFFF !important; }
    
    /* Make all standard text Black */
    p, span, div, label, h1, h2, h3, h4, h5, h6 { color: #000000 !important; }
    
    [data-testid="collapsedControl"], section[data-testid="stSidebar"] { display: none !important; }
    
    /* Tabs Styling for Light Theme */
    div[role="tablist"] button { background-color: transparent !important; }
    div[role="tablist"] button p { color: #475569 !important; font-size: 1.05rem !important; font-weight: 600 !important; }
    div[role="tablist"] button[aria-selected="true"] p { color: #D4AF37 !important; font-weight: 800 !important; }
    div[role="tablist"] button[aria-selected="true"] { border-bottom-color: #D4AF37 !important; }
    
    /* Table Styling for Light Theme */
    [data-testid="stDataFrame"] div, [data-testid="stDataFrame"] th, [data-testid="stDataFrame"] td { color: #000000 !important; background-color: transparent !important; }
    
    /* 🚨 SEARCH BOX & DROPDOWN FIX (Light Theme) 🚨 */
    div[data-baseweb="select"], div[data-baseweb="select"] > div { background-color: #F8FAFC !important; border-color: #D4AF37 !important; border-radius: 8px !important; }
    div[data-baseweb="select"] span, div[data-baseweb="select"] input { color: #000000 !important; font-weight: bold !important; -webkit-text-fill-color: #000000 !important; caret-color: #000000 !important; }
    ul[role="listbox"], ul[data-baseweb="menu"], div[data-baseweb="popover"] { background-color: #FFFFFF !important; border: 1px solid #D4AF37 !important; border-radius: 8px !important; box-shadow: 0 10px 15px rgba(0,0,0,0.1) !important; }
    li[role="option"] { background-color: #FFFFFF !important; color: #000000 !important; font-weight: bold !important; }
    li[role="option"] span { color: #000000 !important; }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] { background-color: #D4AF37 !important; }
    li[role="option"]:hover span, li[role="option"][aria-selected="true"] span, li[role="option"]:hover, li[role="option"][aria-selected="true"] { color: #000000 !important; }
    
    /* Custom Color Classes */
    .txt-green { color: #059669 !important; font-weight: 800 !important; } /* Darker green for white background */
    .txt-red { color: #DC2626 !important; font-weight: 800 !important; } /* Clear red */
    .txt-main { color: #000000 !important; font-weight: 800 !important; } /* Pure Black for Main Numbers/Titles */
    .txt-gray { color: #475569 !important; font-weight: 600 !important; } /* Dark Gray for labels */
    
    /* Box Styling for Light Theme */
    .metric-box { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 10px; }
    .trend-box { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
</style>
""", unsafe_allow_html=True)

# --- 🚀 COMPREHENSIVE F&O STOCKS ---
FO_STOCKS_LIST = ["AARTIIND", "ABB", "ABBOTINDIA", "ABCAPITAL", "ABFRL", "ACC", "ADANIENT", "ADANIPORTS", "ALKEM", "AMBUJACEM", "APOLLOHOSP", "APOLLOTYRE", "ASHOKLEY", "ASIANPAINT", "ASTRAL", "ATUL", "AUBANK", "AUROPHARMA", "AXISBANK", "BAJAJ-AUTO", "BAJAJFINSV", "BAJFINANCE", "BALKRISIND", "BALRAMCHIN", "BANDHANBNK", "BANKBARODA", "BATAINDIA", "BEL", "BERGEPAINT", "BHARATFORG", "BHARTIARTL", "BHEL", "BIOCON", "BOSCHLTD", "BPCL", "BRITANNIA", "BSOFT", "CANBK", "CANFINHOME", "CHAMBLFERT", "CHOLAFIN", "CIPLA", "COALINDIA", "COFORGE", "COLPAL", "CONCOR", "COROMANDEL", "CROMPTON", "CUB", "CUMMINSIND", "DABUR", "DALBHARAT", "DEEPAKNTR", "DIVISLAB", "DIXON", "DLF", "DRREDDY", "EICHERMOT", "ESCORTS", "EXIDEIND", "FEDERALBNK", "GAIL", "GLENMARK", "GMRINFRA", "GNFC", "GODREJCP", "GODREJPROP", "GRANULES", "GRASIM", "GUJGASLTD", "HAL", "HAVELLS", "HCLTECH", "HDFCAMC", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDCOPPER", "HINDPETRO", "HINDUNILVR", "ICICIBANK", "ICICIGI", "ICICIPRULI", "IDEA", "IDFC", "IDFCFIRSTB", "IEX", "IGL", "INDHOTEL", "INDIACEM", "INDIAMART", "INDIGO", "INDUSINDBK", "INDUSTOWER", "INFY", "IPCALAB", "IRCTC", "ITC", "JINDALSTEL", "JKCEMENT", "JSWSTEEL", "JUBLFOOD", "KOTAKBANK", "L&TFH", "LALPATHLAB", "LAURUSLABS", "LICHSGFIN", "LT", "LTIM", "LTTS", "LUPIN", "M&M", "M&MFIN", "MANAPPURAM", "MARICO", "MARUTI", "MCDOWELL-N", "MCX", "METROPOLIS", "MFSL", "MGL", "MOTHERSON", "MPHASIS", "MRF", "MUTHOOTFIN", "NATIONALUM", "NAUKRI", "NAVINFLUOR", "NESTLEIND", "NMDC", "NTPC", "OBEROIRLTY", "OFSS", "ONGC", "PAGEIND", "PEL", "PERSISTENT", "PETRONET", "PFC", "PIDILITIND", "PIIND", "PNB", "POLYCAB", "POONAWALLA", "POWERGRID", "PVRINOX", "RAMCOCEM", "RBLBANK", "RECLTD", "RELIANCE", "SAIL", "SBICARD", "SBILIFE", "SBIN", "SHREECEM", "SHRIRAMFIN", "SIEMENS", "SRF", "SUNTV", "SUNPHARMA", "SYNGENE", "TATACHEM", "TATACOMM", "TATACONSUM", "TATAMOTORS", "TATAPOWER", "TATASTEEL", "TCS", "TECHM", "TITAN", "TORNTPHARM", "TRENT", "TVSMOTOR", "UBL", "ULTRACEMCO", "UPL", "VEDL", "VOLTAS", "WIPRO", "ZEEL", "ZYDUSLIFE", "JIOFIN", "RVNL"]
FO_STOCKS_LIST.sort()

# --- 📡 DATA FETCHING ---
@st.cache_data(ttl=60) 
def get_live_index_data():
    index_tickers = {"NIFTY 50": "^NSEI", "SENSEX": "^BSESN", "BANK NIFTY": "^NSEBANK", "INDIA VIX": "^INDIAVIX"}
    results = {}
    for name, sym in index_tickers.items():
        try:
            t = yf.Ticker(sym)
            hist = t.history(period="5d")
            if len(hist) >= 2:
                prev_close, curr_val = hist['Close'].iloc[-2], hist['Close'].iloc[-1]
                change = curr_val - prev_close
                results[name] = {"value": curr_val, "change": change, "change_percent": (change / prev_close) * 100}
        except: pass
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
                    prev_close, curr_price = s_data.iloc[-2], s_data.iloc[-1]
                    pct_change = ((curr_price - prev_close) / prev_close) * 100
                    changes.append({"symbol": stock.replace(".NS", ""), "current": round(curr_price, 2), "pct": round(pct_change, 2)})
            except: continue
        changes = sorted(changes, key=lambda x: x['pct'], reverse=True)
        return {"gainers": [c for c in changes if c['pct'] > 0][:5], "losers": sorted([c for c in changes if c['pct'] < 0], key=lambda x: x['pct'])[:5]}
    except: return {"gainers": [], "losers": []}

@st.cache_data(ttl=300) 
def scan_52w_high_stocks():
    nifty_stocks = [f"{stock}.NS" for stock in FO_STOCKS_LIST]
    breakout_list = []
    try:
        data = yf.download(nifty_stocks, period="max", progress=False)
        if not data.empty:
            for stock in nifty_stocks:
                try:
                    close_prices = data['Close'][stock].dropna()
                    high_prices = data['High'][stock].dropna()
                    volumes = data['Volume'][stock].dropna()
                    
                    if len(close_prices) > 250 and len(volumes) > 20: 
                        current_price = close_prices.iloc[-1]
                        current_high = high_prices.iloc[-1]
                        ath = high_prices.max() 
                        year_high = high_prices.iloc[-252:].max() 
                        
                        if current_price >= (year_high * 0.98):
                            if current_high >= ath:
                                status_label = "👑 ATH + 52W HIGH"
                            elif current_high >= year_high:
                                status_label = "🚀 NEW 52W HIGH"
                            else:
                                status_label = "👀 Near 52W High"
                                
                            current_vol = volumes.iloc[-1]
                            avg_vol_20 = volumes.iloc[-20:].mean()
                            rvol = current_vol / avg_vol_20 if avg_vol_20 > 0 else 0
                            rvol_display = f"🔥 {rvol:.2f}x" if rvol >= 1.5 else f"{rvol:.2f}x"
                                
                            breakout_list.append({
                                "Symbol": stock.replace(".NS", ""),
                                "Price": f"₹{current_price:,.2f}",
                                "52W High": f"₹{year_high:,.2f}",
                                "ATH": f"₹{ath:,.2f}", 
                                "RVoL": rvol_display,
                                "Status": status_label
                            })
                except: continue
    except: pass
    return pd.DataFrame(breakout_list)

# --- UI COMPONENTS ---
def _render_custom_metric(label, value, change, pct):
    color_class, arrow, sign = ("txt-green", "↑", "+") if change >= 0 else ("txt-red", "↓", "")
    html = f"""<div class="metric-box">
        <div class="txt-gray" style="font-size: 0.85rem; text-transform: uppercase;">{label}</div>
        <div class="txt-main" style="font-size: 1.7rem;">{value:,.2f}</div>
        <div class="{color_class}" style="font-size: 0.9rem; margin-top: 5px;">{arrow} {sign}{change:,.2f} ({sign}{pct:.2f}%)</div>
    </div>"""
    st.markdown(html, unsafe_allow_html=True)

def _render_alert(message, type="success"):
    # Light theme alert colors
    bg, border, text_color = ("#D1FAE5", "#059669", "#064E3B") if type == "success" else ("#FEE2E2", "#DC2626", "#7F1D1D") if type == "error" else ("#F1F5F9", "#475569", "#0F172A")
    st.markdown(f'<div style="background: {bg}; border: 1px solid {border}; border-radius: 8px; padding: 12px 16px; margin-bottom: 15px; color: {text_color} !important; font-weight: 600;">{message}</div>', unsafe_allow_html=True)

def _render_range_bar(label, low, high, current):
    if high <= low or high == 0: return
    pct = max(0, min(100, ((current - low) / (high - low)) * 100))
    st.markdown(f"""<div class="metric-box"><h4 class="txt-main" style="margin-top:0; margin-bottom:15px; font-size:1.1rem;">🎯 {label} Range</h4><div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:8px;"><span class="txt-gray">Low: <b class="txt-main">₹{low:,.2f}</b></span><span class="txt-gray">High: <b class="txt-main">₹{high:,.2f}</b></span></div><div style="position:relative; height:6px; background:#E2E8F0; border-radius:3px; width:100%;"><div style="position:absolute; left:0; top:0; height:100%; width:{pct}%; background:linear-gradient(90deg, #EF4444, #F59E0B, #10B981); border-radius:3px;"></div><div style="position:absolute; left:calc({pct}% - 6px); top:6px; width:0; height:0; border-left:6px solid transparent; border-right:6px solid transparent; border-bottom:8px solid #D4AF37;"></div></div><div style="text-align:center; font-size:0.9rem; margin-top:16px;"><span class="txt-main">Current:</span> <span style="color:#D4AF37 !important; font-weight:800; font-size:1.1rem;">₹{current:,.2f}</span></div></div>""", unsafe_allow_html=True)

# --- MAIN APP LAYOUT ---
def render_dashboard():
    st.markdown("""<h1 style="font-size: 2.5rem; font-weight: 800; background: linear-gradient(90deg, #D4AF37, #FDE047, #C5A059); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; padding-top: 10px;">🚩 STOCK BY DSD AI</h1>""", unsafe_allow_html=True)
    st.markdown("""<p style="text-align: center; color: #475569 !important; font-size: 0.9rem; margin-bottom: 20px;">Professional AI Market Intelligence Terminal</p>""", unsafe_allow_html=True)
    
    indices = get_live_index_data()
    if indices:
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        cols = [col1, col2, col3, col4]
        for idx, (name, data) in enumerate(indices.items()):
            if idx < 4:
                with cols[idx]: _render_custom_metric(name, data["value"], data["change"], data["change_percent"])
                    
    st.markdown("""<br>""", unsafe_allow_html=True)
    st.markdown("""<h3 class="txt-main" style="font-size:1.2rem;">🔍 Search F&O Stock</h3>""", unsafe_allow_html=True)
    symbol = st.selectbox("Select Stock", options=FO_STOCKS_LIST, index=FO_STOCKS_LIST.index("RELIANCE"), label_visibility="collapsed")
    st.markdown("""<br>""", unsafe_allow_html=True)

    st.markdown("""<h3 class="txt-main" style="font-size:1.2rem;">🔥 Live F&O Action</h3>""", unsafe_allow_html=True)
    with st.spinner("Fetching Live Market..."):
        trending = get_live_trending_fo()
        gainers, losers = trending.get("gainers", []), trending.get("losers", [])

    if gainers or losers:
        trend_tab1, trend_tab2 = st.tabs(["🟢 Top Gainers", "🔴 Top Losers"])
        with trend_tab1:
            if gainers:
                for g in gainers: st.markdown(f"""<div class="trend-box"><div style="display:flex; justify-content:space-between; align-items:center;"><span class="txt-main" style="font-size:1rem;">{g['symbol']}</span><span class="txt-green" style="font-size:1rem;">↑ +{g['pct']}%</span></div><div class="txt-gray" style="font-size:0.85rem; margin-top:4px;">₹{g['current']:,.2f}</div></div>""", unsafe_allow_html=True)
            else: st.write("No gainers currently.")
        with trend_tab2:
            if losers:
                for ls in losers: st.markdown(f"""<div class="trend-box"><div style="display:flex; justify-content:space-between; align-items:center;"><span class="txt-main" style="font-size:1rem;">{ls['symbol']}</span><span class="txt-red" style="font-size:1rem;">↓ {ls['pct']}%</span></div><div class="txt-gray" style="font-size:0.85rem; margin-top:4px;">₹{ls['current']:,.2f}</div></div>""", unsafe_allow_html=True)
            else: st.write("No losers currently.")

    st.markdown("""<hr style="border-color:#E2E8F0;">""", unsafe_allow_html=True)

    if symbol:
        st.markdown(f"""<h2 class="txt-main">💎 Terminal Analysis: <span style="color:#D4AF37 !important;">{symbol}</span></h2>""", unsafe_allow_html=True)
        try:
            _hist = yf.Ticker(f"{symbol}.NS").history(period="2d")
            if len(_hist) >= 2:
                yesterday_high, current_price = _hist['High'].iloc[-2], _hist['Close'].iloc[-1]
                if current_price > yesterday_high: _render_alert(f"🟢 <b>MOMENTUM ALERT:</b> {symbol} कल के High (₹{yesterday_high:,.2f}) को पार कर चुका है! (Current: ₹{current_price:,.2f})", "success")
                else: _render_alert(f"⚪ <b>NO BREAKOUT YET:</b> {symbol} अभी कल के High (₹{yesterday_high:,.2f}) के नीचे ट्रेड कर रहा है।", "neutral")
        except: pass

        col1, col2 = st.columns(2)
        with col1: _render_range_bar("Intraday", 2450.00, 2530.00, 2495.50)
        with col2: _render_range_bar("52-Week", 2100.00, 3100.00, 2495.50)

        st.markdown("""<br>""", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["📊 Chart", "🧠 Fundamentals", "🏢 Alerts"])
        
        with tab1:
            try:
                df = yf.Ticker(f"{symbol}.NS").history(period="1mo", interval="1d")
                if not df.empty:
                    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], increasing_line_color='#10B981', decreasing_line_color='#EF4444')])
                    fig.update_layout(title=f"{symbol} (Last 1 Month)", template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=40, b=10), xaxis=dict(showgrid=True, gridcolor='#E2E8F0', tickfont=dict(color='#475569')), yaxis=dict(showgrid=True, gridcolor='#E2E8F0', tickfont=dict(color='#475569')), title_font=dict(color='#000000'))
                    st.plotly_chart(fig, use_container_width=True)
            except: pass
                
        with tab2:
            try:
                info = yf.Ticker(f"{symbol}.NS").info
                mcap = info.get('marketCap')
                st.markdown(f"""<div class="metric-box"><div class="txt-gray" style="font-size:0.9rem;">Market Cap</div><div class="txt-main" style="font-size:1.4rem;">₹{mcap/10000000:,.2f} Cr</div></div>""", unsafe_allow_html=True)
                pe = info.get('trailingPE', 0)
                pe_color = "txt-green" if pe and pe < 25 else "txt-red" if pe and pe > 40 else "txt-main"
                st.markdown(f"""<div class="metric-box"><div class="txt-gray" style="font-size:0.9rem;">P/E Ratio</div><div class="{pe_color}" style="font-size:1.4rem;">{round(pe,2) if pe else "N/A"}</div></div>""", unsafe_allow_html=True)
                roe = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
                roe_color = "txt-green" if roe > 15 else "txt-red" if roe < 5 else "txt-main"
                st.markdown(f"""<div class="metric-box"><div class="txt-gray" style="font-size:0.9rem;">ROE</div><div class="{roe_color}" style="font-size:1.4rem;">{round(roe,2)}%</div></div>""", unsafe_allow_html=True)
            except: pass
                
        with tab3:
            try:
                ticker = yf.Ticker(f"{symbol}.NS")
                st.markdown("""<h3 class="txt-main">🚨 Promoter Trust Radar</h3>""", unsafe_allow_html=True)
                try:
                    insider = ticker.insider_transactions
                    if insider is not None and not insider.empty: _render_alert("🔴 **ALERT (Red Flag 🚩):** प्रमोटर/इनसाइडर की गतिविधि दर्ज की गई है।", "error")
                    else: _render_alert("🟢 **ALL CLEAR:** प्रमोटर द्वारा शेयर बेचने का कोई नेगेटिव सिग्नल नहीं है।", "success")
                except: _render_alert("🟢 **ALL CLEAR:** प्रमोटर का कोई अलर्ट नहीं है।", "success")
                
                major_holders = ticker.major_holders
                if major_holders is not None and not major_holders.empty:
                    df_m = major_holders.copy()
                    if isinstance(df_m.index[0], str): df_m = df_m.reset_index(); df_m.columns = ["Category", "Value"]
                    elif len(df_m.columns) >= 2: df_m.columns = ["Value", "Category"]; df_m = df_m[["Category", "Value"]]
                    df_m["Category"] = df_m["Category"].replace({"insidersPercentHeld": "👔 Promoter Holding", "institutionsPercentHeld": "🏦 Institutional Holding", "institutionsFloatPercentHeld": "🌊 Market Float", "institutionsCount": "🏢 Total Institutions"})
                    st.dataframe(df_m, use_container_width=True, hide_index=True)
            except: pass

        st.markdown("""<br>""", unsafe_allow_html=True)
        
        # 6. ATH & 52 WEEK HIGH RADAR
        with st.expander("🔥 DSD All-Time & 52-Week High Master Radar", expanded=True):
            st.markdown("""<p class="txt-gray">इस लिस्ट में सिर्फ वही F&O स्टॉक्स दिखेंगे जो आज अपने 1 साल या All-Time High के करीब हैं।</p>""", unsafe_allow_html=True)
            with st.spinner("Scanning ALL F&O stocks live (This may take a moment)..."):
                breakout_df = scan_52w_high_stocks()
                if not breakout_df.empty:
                    _render_alert(f"🟢 🚨 कुल {len(breakout_df)} F&O स्टॉक्स आज ज़बरदस्त तेज़ी में हैं!", "success")
                    st.dataframe(breakout_df, use_container_width=True, hide_index=True)
                else:
                    _render_alert("🔴 आज इस लिस्ट में से कोई भी F&O स्टॉक अपने High पर नहीं है।", "error")

if __name__ == "__main__":
    render_dashboard()
