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
            "change": f"{sign}{change:,.2f} ({sign}{percent:,.2f}%)",
            "raw_change": change,
            "raw_percent": percent
        }
    except Exception as e:
        print(f"Error fetching {ticker_symbol}: {e}")
        return None

def get_bithumb_usdc():
    """
    Fetches USDC price from Bithumb API.
    """
    try:
        url = "https://api.bithumb.com/public/ticker/USDC_KRW"
        response = requests.get(url)
        data = response.json()
        
        if data['status'] == '0000':
            price = float(data['data']['closing_price'])
            # Bithumb doesn't give easy daily change in this endpoint, 
            # but user only asked for current price for USDC.
            return {
                "value": f"{price:,.0f}", # KRW usually no decimals for crypto
                "change": "0",
                "raw_change": 0
            }
        return None
    except Exception as e:
        print(f"Error fetching Bithumb USDC: {e}")
        return None

def get_stocks_data():
    # Map: Frontend ID -> Ticker
    tickers = {
        'sp_futures': 'ES=F',
        'dow_futures': 'YM=F',
        'nasdaq_futures': 'NQ=F',
        'vix': '^VIX'
    }
    
    result = {}
    for key, symbol in tickers.items():
        data = get_ticker_data(symbol)
        if data:
            result[key] = data
        else:
            # Fallback Mock
            result[key] = {"value": "N/A", "change": "0.00", "raw_change": 0, "raw_percent": 0}

    # Fear & Greed (Mock - CNN API is private)
    # Randomly fluctuate around 'Neutral' to 'Greed' for demo
    fg_val = random.randint(40, 60)
    result['fear_greed'] = {
        "value": str(fg_val),
        "change": "Neutral",
        "raw_change": 0
    }
    
    return result

def get_economy_data():
    # Real economic data requires specialized APIs (FRED, etc.)
    # Mocking for UI demonstration with Next Release Date
    return {
        'cci': {"value": "102.5", "change": "+1.2", "date": "24/11/26", "next_date": "24/12/20"},
        'pmi': {"value": "48.5", "change": "-0.3", "date": "24/11/01", "next_date": "24/12/02"},
        'unemployment': {"value": "3.9%", "change": "+0.1%", "date": "24/11/03", "next_date": "24/12/08"},
        'non_farm': {"value": "180K", "change": "+10K", "date": "24/11/03", "next_date": "24/12/08"}
    }

def get_rates_data():
    # US 10Y is widely available. Others are harder to get free real-time.
    us_10y = get_ticker_data('^TNX')
    
    # Helper to ensure structure for USA extra column
    def format_us_rate(data, default_val, default_chg, default_pct):
        if data:
            return {
                "value": data['value'], 
                "change": data['raw_change'], 
                "percent": data['raw_percent']
            }
        return {"value": default_val, "change": default_chg, "percent": default_pct}

    us_10y_data = format_us_rate(us_10y, "4.088", -0.01, -0.27)
    
    return {
        # USA: Value (Point), Change (Abs), Percent (Rel)
        'us_10y': us_10y_data,
        'us_2y': {"value": "3.510", "change": -0.03, "percent": -0.88},
        'us_10_2_spread': {"value": "0.570", "change": 0.02, "percent": 3.1},
        'fed_rate': {"value": "4.00", "change": 0.00, "percent": 0.00, "is_percent": True}, # Special flag for % display
        
        # Japan/Korea: Value (Percent)
        'jp_2y': {"value": "1.02", "change": "+0.01"},
        'jp_policy': {"value": "0.50", "change": "0.00"},
        
        'kr_10y': {"value": "3.35", "change": "-0.02"},
        'kr_2y': {"value": "2.87", "change": "-0.01"},
        'kr_base': {"value": "2.50", "change": "0.00"},
        
        'sofr': {"value": "4.12", "change": "+0.01"}
    }

def get_exchange_data():
    tickers = {
        'dxy': 'DX-Y.NYB',
        'usd_krw': 'KRW=X'
    }
    
    result = {}
    for key, symbol in tickers.items():
        data = get_ticker_data(symbol)
        if data:
            result[key] = data
        else:
            result[key] = {"value": "N/A", "change": "0.00"}

    # USDC from Bithumb
    usdc_data = get_bithumb_usdc()
    if usdc_data:
        result['usdc'] = usdc_data
    else:
        # Fallback to Yahoo if Bithumb fails
        y_usdc = get_ticker_data('USDC-USD') # This is usually 1.00 USD, not KRW. 
        # Actually user probably wants KRW price if using Bithumb.
        # Let's try USDC-KRW if available on Yahoo, or just fallback to N/A
        result['usdc'] = {"value": "N/A", "change": "0"}

    # Mocking specialized financial data with dates
    result['cds'] = {"value": "23.05", "change": "-0.5"}
    result['forex_res'] = {
        "value": "428.8B", 
        "change": "+1.2B", 
        "date": "25/11/05", 
        "next_date": "25/12/04"
    }
    result['foreign_bond'] = {
        "value": "307조원", 
        "change": "", 
        "date": "25/11/14", 
        "next_date": "25/12/12"
    }
    
    return result
