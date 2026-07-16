"""
All-Time High (ATH) Scanner with Volume Analysis
Identifies stocks at all-time highs with high volume
"""

import json
from datetime import datetime, timedelta
from typing import Optional
import yfinance as yf
import pandas as pd
from crewai.tools import tool


def _get_nse_symbol(symbol: str) -> str:
    """Convert symbol to NSE Yahoo Finance format."""
    symbol = symbol.upper().strip()
    if not symbol.endswith(".NS"):
        return f"{symbol}.NS"
    return symbol


def _get_average_volume(ticker_obj, period: str = "20d") -> float:
    """Get average volume for specified period."""
    try:
        hist = ticker_obj.history(period=period)
        if not hist.empty:
            return hist['Volume'].mean()
        return 0
    except Exception:
        return 0


def _is_high_volume(current_volume: int, avg_volume: float, volume_multiplier: float = 1.5) -> bool:
    """Check if current volume is above average."""
    if avg_volume == 0:
        return False
    return current_volume > (avg_volume * volume_multiplier)


def _get_all_nse_stocks() -> list[str]:
    """Get list of all NSE stocks (popular ones)."""
    nse_stocks = [
        # Nifty 50
        "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "HDFC", "WIPRO", "MARUTI",
        "LT", "ASIANPAINT", "BAJAJFINSV", "BAJAJ-AUTO", "ITC", "SBIN", "AXISBANK",
        "KOTAKBANK", "JSWSTEEL", "HCLTECH", "TECHM", "SBILIFE", "SUNPHARMA",
        "DMART", "TATAMOTORS", "POWERGRID", "BHARTIARTL", "ADANIPORTS", "ADANIGREEN",
        "ADANIENT", "ADANIPOWER", "CEMENT", "HEROMOTOCO", "HINDALCO", "NTPC",
        "TATASTEEL", "ULTRACEMCO", "BPCL", "M&M", "TATACONSUM", "BRITANNIA",
        "CIPLA", "DIVISLAB", "APOLLOHOSP", "SHREECEM", "SIEMENS", "LTIM", "BOSCHLTD",
        "HINDUNILVR", "NESTLEIND",
        # Mid and Small Caps
        "ZOMATO", "PAYTM", "IRCTC", "YESBANK", "PFC", "COAL", "IOC", "GAIL", "BAJAJHLDL",
        "BERGEPAINT", "MRF", "AMBUJACEM", "NMDC", "SAIL", "VEDL", "JIOFIN", "MARICO",
        "COLPAL", "VBL", "MANAPPURAM", "LTTS", "MUTHOOTFIN", "EXIDEIND",
    ]
    return nse_stocks


@tool("Scan All-Time High (ATH)")
def scan_all_time_high(volume_multiplier: float = 1.5, symbols_to_check: Optional[list[str]] = None) -> str:
    """
    Scan for stocks at All-Time High (ATH) with high volume.
    
    Args:
        volume_multiplier: Volume must be above (avg_volume * multiplier). Default: 1.5x
        symbols_to_check: Specific symbols to scan. If None, scans top NSE stocks.
        
    Returns:
        JSON string with ATH stocks list (sorted by volume and strength).
    """
    if symbols_to_check is None:
        symbols_to_check = _get_all_nse_stocks()
    
    ath_stocks = []
    total_checked = 0
    
    for symbol in symbols_to_check:
        total_checked += 1
        try:
            nse_symbol = _get_nse_symbol(symbol)
            ticker = yf.Ticker(nse_symbol)
            info = ticker.info
            
            # Get 5-year historical data to find ATH
            hist = ticker.history(period="5y")
            
            if hist.empty or len(hist) < 2:
                continue
            
            current_price = hist['Close'].iloc[-1]
            current_volume = hist['Volume'].iloc[-1]
            avg_volume = _get_average_volume(ticker, "20d")
            
            # All-time high from historical data
            ath_price = hist['High'].max()
            ath_date = hist['High'].idxmax().strftime("%Y-%m-%d")
            
            # Check ATH condition: price at/near all-time high
            ath_threshold = ath_price * 0.98  # Within 2% of ATH
            is_at_ath = current_price >= ath_threshold
            
            # Check volume condition
            is_high_vol = _is_high_volume(current_volume, avg_volume, volume_multiplier)
            
            if is_at_ath and is_high_vol:
                # Get price change info
                prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                change_pct = ((current_price - prev_close) / prev_close) * 100
                
                # Days since ATH was set
                days_since_ath = (datetime.now().date() - hist['High'].idxmax().date()).days
                
                # Get 1-year return
                one_year_ago = hist[hist.index <= datetime.now() - timedelta(days=365)]
                year_return = 0
                if not one_year_ago.empty:
                    year_return = ((current_price - one_year_ago['Close'].iloc[-1]) / one_year_ago['Close'].iloc[-1] * 100)
                
                ath_stocks.append({
                    "symbol": symbol,
                    "current_price": round(current_price, 2),
                    "ath_price": round(ath_price, 2),
                    "distance_from_ath": round(ath_price - current_price, 2),
                    "percent_from_ath": round(((ath_price - current_price) / ath_price * 100), 2),
                    "ath_date": ath_date,
                    "days_since_ath": days_since_ath,
                    "current_volume": int(current_volume),
                    "avg_volume_20d": round(avg_volume, 0),
                    "volume_multiplier": round(current_volume / avg_volume, 2) if avg_volume > 0 else 0,
                    "change_today_percent": round(change_pct, 2),
                    "one_year_return": round(year_return, 2),
                    "52_week_high": round(info.get("fiftyTwoWeekHigh", 0), 2),
                    "52_week_low": round(info.get("fiftyTwoWeekLow", 0), 2),
                    "ath_strength": "🔥 New ATH" if days_since_ath == 0 else "Strong" if days_since_ath <= 30 else "Moderate",
                })
        
        except Exception as e:
            continue
    
    # Sort by ATH strength (newest first), then by volume multiplier
    ath_stocks.sort(key=lambda x: (x["days_since_ath"], -x["volume_multiplier"]))
    
    result = {
        "scan_status": "complete",
        "timestamp": datetime.now().isoformat(),
        "total_stocks_checked": total_checked,
        "ath_found": len(ath_stocks),
        "criteria": {
            "price_filter": "At/Near All-Time High (within 2%)",
            "volume_filter": f"Volume > {volume_multiplier}x avg volume (20d)",
        },
        "ath_stocks": ath_stocks[:25],  # Top 25
    }
    
    return json.dumps(result, indent=2)


@tool("Get Atomic ATH List")
def get_atomic_ath_list() -> str:
    """
    Get an 'Atomic ATH List' - auto-updated machine-readable format.
    
    Returns:
        JSON string with compact atomic list (easy to parse and integrate).
    """
    try:
        ath_data = json.loads(scan_all_time_high(volume_multiplier=1.5))
        
        # Create atomic list format
        atomic_list = {
            "type": "atomic_ath_list",
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "total_ath": ath_data["ath_found"],
            "stocks": [
                {
                    "s": stock["symbol"],  # s = symbol
                    "p": stock["current_price"],  # p = current price
                    "a": stock["ath_price"],  # a = ath price
                    "d": stock["distance_from_ath"],  # d = distance
                    "v": stock["volume_multiplier"],  # v = volume multiplier
                    "c": stock["change_today_percent"],  # c = change %
                    "1yr": stock["one_year_return"],  # 1yr = 1-year return
                    "dsa": stock["days_since_ath"],  # dsa = days since ath
                    "str": stock["ath_strength"],  # str = strength
                }
                for stock in ath_data["ath_stocks"]
            ],
            "metadata": {
                "volume_threshold": "1.5x average (20 days)",
                "price_threshold": "Within 2% of all-time high",
                "last_updated": datetime.now().isoformat(),
            }
        }
        
        return json.dumps(atomic_list, indent=2)
    
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "type": "atomic_ath_list",
            "stocks": []
        })


@tool("Get Strongest ATH Alerts")
def get_strongest_ath_alerts(min_volume_multiplier: float = 2.0) -> str:
    """
    Get strongest ATH alerts - only recent ATH with massive volume.
    
    Args:
        min_volume_multiplier: Minimum volume multiplier (default 2.0x)
        
    Returns:
        JSON string with high-conviction ATH stocks.
    """
    try:
        ath_data = json.loads(scan_all_time_high(volume_multiplier=min_volume_multiplier))
        
        # Filter for strongest signals (recent ATH + high volume)
        strongest = [
            stock for stock in ath_data["ath_stocks"]
            if stock["volume_multiplier"] >= min_volume_multiplier and stock["days_since_ath"] <= 60
        ]
        
        # Further sort by recency and volume
        strongest.sort(key=lambda x: (x["days_since_ath"], -x["volume_multiplier"]))
        
        result = {
            "alert_type": "strongest_ath_signals",
            "timestamp": datetime.now().isoformat(),
            "criteria": {
                "volume": f"{min_volume_multiplier}x+ average volume",
                "recency": "Within 60 days of ATH",
            },
            "total_alerts": len(strongest),
            "stocks": strongest[:15],
        }
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "alert_type": "strongest_ath_signals",
            "stocks": []
        })


@tool("Compare 52W High vs ATH")
def compare_52week_vs_ath(symbol: str) -> str:
    """
    Compare 52-week high vs All-Time High for a stock.
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
        
    Returns:
        JSON string with detailed comparison.
    """
    try:
        nse_symbol = _get_nse_symbol(symbol)
        ticker = yf.Ticker(nse_symbol)
        info = ticker.info
        
        # Get 5-year data for ATH
        hist = ticker.history(period="5y")
        
        if hist.empty:
            return json.dumps({
                "error": f"No data for {symbol}",
                "symbol": symbol,
            })
        
        current_price = hist['Close'].iloc[-1]
        ath_price = hist['High'].max()
        ath_date = hist['High'].idxmax().strftime("%Y-%m-%d")
        
        week_52_high = info.get("fiftyTwoWeekHigh", 0)
        week_52_low = info.get("fiftyTwoWeekLow", 0)
        
        # Calculate percentages
        from_ath_pct = ((ath_price - current_price) / ath_price * 100) if ath_price > 0 else 0
        from_52w_pct = ((week_52_high - current_price) / week_52_high * 100) if week_52_high > 0 else 0
        
        result = {
            "symbol": symbol.upper(),
            "current_price": round(current_price, 2),
            "comparison": {
                "all_time_high": {
                    "price": round(ath_price, 2),
                    "date": ath_date,
                    "distance": round(ath_price - current_price, 2),
                    "percent_below": round(from_ath_pct, 2),
                    "status": "🔥 AT ATH!" if from_ath_pct < 0.5 else "📈 Near ATH" if from_ath_pct < 2 else f"📊 {from_ath_pct}% below ATH",
                },
                "52_week_high": {
                    "price": round(week_52_high, 2),
                    "distance": round(week_52_high - current_price, 2),
                    "percent_below": round(from_52w_pct, 2),
                    "status": "✅ AT 52W HIGH!" if from_52w_pct < 0.5 else "📈 Near 52W high" if from_52w_pct < 2 else f"📊 {from_52w_pct}% below 52W high",
                },
                "52_week_low": round(week_52_low, 2),
                "range_from_low_pct": round(((current_price - week_52_low) / (week_52_high - week_52_low) * 100), 2) if (week_52_high - week_52_low) > 0 else 0,
            },
            "analysis": {
                "ath_premium": round(((ath_price - week_52_high) / week_52_high * 100), 2),
                "gap_to_close": round(ath_price - current_price, 2),
                "potential": "🚀 HIGH" if from_ath_pct > 15 else "🟡 MEDIUM" if from_ath_pct > 5 else "🔥 LOW (Already near ATH)",
            },
            "timestamp": datetime.now().isoformat(),
        }
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "symbol": symbol,
        })


def generate_ath_csv() -> str:
    """Generate CSV format of ATH stocks (for spreadsheet import)."""
    try:
        ath_data = json.loads(scan_all_time_high(volume_multiplier=1.5))
        
        csv_content = "Symbol,Price,ATH,Distance,FromATH(%),ATHDate,DaysSinceATH,Volume,Avg20d,VolMultiplier,Change(%),1YearReturn(%),Strength\n"
        
        for stock in ath_data["ath_stocks"]:
            csv_line = f"{stock['symbol']},{stock['current_price']},{stock['ath_price']},{stock['distance_from_ath']},{stock['percent_from_ath']},{stock['ath_date']},{stock['days_since_ath']},{stock['current_volume']},{int(stock['avg_volume_20d'])},{stock['volume_multiplier']},{stock['change_today_percent']},{stock['one_year_return']},{stock['ath_strength']}\n"
            csv_content += csv_line
        
        return csv_content
    
    except Exception as e:
        return f"Error generating CSV: {str(e)}"


def generate_combined_breakout_ath_list() -> str:
    """
    Generate combined list - stocks that are BOTH near 52W high AND near ATH.
    Super strong signals!
    """
    try:
        breakout_data = json.loads(scan_all_time_high(volume_multiplier=1.5))
        
        # Filter for stocks very close to ATH (within 1%)
        combined = [
            stock for stock in breakout_data["ath_stocks"]
            if stock["percent_from_ath"] < 1.0  # Within 1% of ATH
        ]
        
        result = {
            "type": "combined_52w_ath_list",
            "timestamp": datetime.now().isoformat(),
            "total_signals": len(combined),
            "description": "Stocks at BOTH 52-week high AND all-time high = STRONGEST signals 🔥",
            "stocks": combined[:20],
        }
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return f"Error: {str(e)}"
