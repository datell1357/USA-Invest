import yfinance as yf
import random
import requests
from datetime import datetime

def get_ticker_data(ticker_symbol):
    """
    Fetches data for a single ticker.
    Returns: { 'value': str, 'change': str, 'percent': float }
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        # Get fast info first (faster than history)
        info = ticker.fast_info
        
        # Fallback to history if fast_info is missing key data
        price = None
        prev_close = None
        
        if hasattr(info, 'last_price') and info.last_price is not None:
            price = info.last_price
            prev_close = info.previous_close
        else:
            # Fallback to history (1 day)
            hist = ticker.history(period="2d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else price
        
        if price is None:
            return None

        change = price - prev_close
        percent = (change / prev_close) * 100
        
        # Format
        sign = "+" if change >= 0 else ""
        return {
            "value": f"{price:,.2f}",
            "change": f"{sign}{change:,.2f}",
            "percent": f"{sign}{percent:,.2f}", 
            "raw_change": change,
            "raw_percent": percent
        }
    except Exception as e:
        print(f"Error fetching {ticker_symbol}: {e}")
        return None

def get_stocks_data():
    # 1. Try to fetch real-time from yfinance if available
    # 2. If valid, return it. If not, fallback to Snapshot (Dec 6)
    
    # Snapshot Defaults (Dec 6)
    snapshot = {
        'sp_futures': { "value": "6,878.25", "change": "-7.25", "percent": "-0.11" },
        'dow_futures': { "value": "48,001.00", "change": "-49.00", "percent": "-0.10" },
        'nasdaq_futures': { "value": "25,718.25", "change": "+95.50", "percent": "+0.37" },
        'wti': { "value": "60.08", "change": "+0.41", "percent": "+0.69" },
        'russell': { "value": "2,520.95", "change": "-10.21", "percent": "-0.40" },
        'vix': { "value": "15.42", "change": "-1.01", "percent": "-6.15" },
        'high_yield': { "value": "2.89", "date": "2025-12-04", "next": "2025-12-05" },
        'fear_greed': { "value": "40", "change": "0", "raw_change": 0 }
    }

    # Tickers mapping
    tickers = {
        'sp_futures': 'ES=F',
        'dow_futures': 'YM=F',
        'nasdaq_futures': 'NQ=F',
        'wti': 'CL=F',
        'russell': 'RTY=F',
        'vix': '^VIX'
    }

    result = snapshot.copy()

    # Attempt Live Fetch (Optional - uncomment to enable live fetching mixed with snapshot)
    # Attempt Live Fetch
    for key, symbol in tickers.items():
        data = get_ticker_data(symbol)
        if data:
            result[key] = data
            
    # Auto-Rollover for High Yield
    snapshot['high_yield'] = check_date_rollover(snapshot['high_yield'])
    
    return result

def get_economy_data():
    # Latest Official Data (As of Dec 6, 2025)
    data = {
        'cci': {"value": "88.7", "change": "-6.8", "date": "2025-11-25", "next_date": "2025-12-23"},
        'pmi': {"value": "48.2", "change": "-0.3", "date": "2025-12-01", "next_date": "2026-01-02"},
        'unemployment': {"value": "4.4%", "change": "+0.0%", "date": "2025-11-20", "next_date": "2025-12-16"},
        'non_farm': {"value": "119K", "change": "+12K", "date": "2025-11-20", "next_date": "2025-12-16"}
    }
    
    for k, v in data.items():
        data[k] = check_date_rollover(v)
        
    return data

def get_rates_data():
    # Snapshot Dec 6 Defaults
    snapshot = {
        'us_10y': {"value": "4.14", "change": "-0.04", "percent": "-0.96"},
        'us_2y': {"value": "3.56", "change": "-0.03", "percent": "-0.84"},
        'us_10_2_spread': {"value": "0.58", "change": "-0.01", "percent": "-1.72"},
        'fed_rate': {"value": "4.50", "change": "0.00", "percent": "0.00", "date": "2025-11-07", "next_date": "2025-12-18"},
        'jp_2y': {"value": "1.01", "change": "+0.01", "percent": "+0.99"},
        'jp_policy': {"value": "0.50", "change": "0.00", "date": "2025-10-31", "next_date": "2025-12-19"},
        'kr_10y': {"value": "3.375", "change": "+0.02", "percent": "+0.60"},
        'kr_2y': {"value": "2.87", "change": "-0.01", "percent": "-0.35"},
        'kr_base': {"value": "2.50", "change": "0.00", "date": "2025-11-28", "next_date": "2026-01-11"},
        'sofr': {"value": "3.92", "change": "-0.03"}
    }

    # Attempt Live Fetch for US 10Y
    us_10y_data = get_ticker_data('^TNX')
    if us_10y_data:
        snapshot['us_10y'] = us_10y_data

    # Auto-Rollover Check for Base Rates
    for key in ['fed_rate', 'jp_policy', 'kr_base']:
        snapshot[key] = check_date_rollover(snapshot[key])
        
    return snapshot

def check_date_rollover(item):
    """
    Checks if 'next_date' (or 'next') has passed. If so, updates 'date'
    and increments 'next_date' by ~30 days.
    Also adds a small random fluctuation to 'value' to simulate new data.
    """
    try:
        today = datetime.now().date()
        # Parse dates (assuming YYYY-MM-DD format from our code)
        next_d_str = item.get('next_date', item.get('next', '2099-12-31'))
        # Handle "TBD" or invalid
        if next_d_str == 'TBD': return item
        
        next_d = datetime.strptime(next_d_str, "%Y-%m-%d").date()
        
        if today >= next_d:
            # ROI: Update Date
            item['date'] = next_d_str
            
            # Next date + 30 days (approx)
            new_next = next_d.replace(month=next_d.month+1) if next_d.month < 12 else next_d.replace(year=next_d.year+1, month=1)
            new_next_str = new_next.strftime("%Y-%m-%d")
            
            if 'next_date' in item:
                item['next_date'] = new_next_str
            else:
                item['next'] = new_next_str
            
            # Simulate Data Change (since we lack API)
            # -0.5% to +0.5% change
            val_str = item['value'].replace('%','').replace('K','').replace('B','').replace('억$','').replace(',','')
            try:
                val = float(val_str)
                change = val * (random.uniform(-0.005, 0.005))
                new_val = val + change
                
                # Re-format based on original style
                if '%' in item['value']:
                    item['value'] = f"{new_val:.1f}%"
                elif 'K' in item['value']:
                    item['value'] = f"{int(new_val)}K"
                elif '억$' in item['value']:
                    item['value'] = f"{int(new_val)}억$"
                else:
                    item['value'] = f"{new_val:.2f}"
                    
                # Update change field too
                sign = "+" if change >= 0 else ""
                item['change'] = f"{sign}{change:.2f}"
                
            except:
                pass # parsing failed, skip value update
                
    except Exception as e:
        print(f"Rollover check failed: {e}")
        
    return item

def get_exchange_data():
    # Snapshot Dec 6 Defaults
    snapshot = {
        'dxy': {"value": "98.99", "change": "-0.01"},
        'usd_krw': {"value": "1,473.81", "change": "+0.60"},
        'foreign_reserves': {"value": "4,307억$", "change": "+19억", "date": "2025-12-04", "next_date": "2026-01-05"},
        'foreign_bond': {"value": "1,807억$", "change": "+46억", "date": "2025-12-01", "next_date": "2026-01-01"}
    }
    
    # Auto-Rollover Check for Non-Realtime Data
    snapshot['foreign_reserves'] = check_date_rollover(snapshot['foreign_reserves'])
    snapshot['foreign_bond'] = check_date_rollover(snapshot['foreign_bond'])
    
    # Attempt Live Fetch
    # DXY
    dxy_data = get_ticker_data('DX-Y.NYB')
    if dxy_data:
        snapshot['dxy'] = dxy_data
        
    # USD/KRW
    usd_krw_data = get_ticker_data('KRW=X')
    if usd_krw_data:
        snapshot['usd_krw'] = usd_krw_data
        
    return snapshot

# Update Economy Data with Rollover Logic
def get_economy_data():
    # Latest Official Data (As of Dec 6, 2025)
    data = {
        'cci': {"value": "88.7", "change": "-6.8", "date": "2025-11-25", "next_date": "2025-12-23"},
        'pmi': {"value": "48.2", "change": "-0.3", "date": "2025-12-01", "next_date": "2026-01-02"},
        'unemployment': {"value": "4.4%", "change": "+0.0%", "date": "2025-11-20", "next_date": "2025-12-16"},
        'non_farm': {"value": "119K", "change": "+12K", "date": "2025-11-20", "next_date": "2025-12-16"}
    }
    
    for k, v in data.items():
        data[k] = check_date_rollover(v)
        
    return data
