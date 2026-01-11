import yfinance as yf
import requests
import os
import time
from datetime import datetime, timedelta
import crawler_service
import FinanceDataReader as fdr

# FRED API Key configuration (Restored as requested)
FRED_API_KEY = os.environ.get("FRED_API_KEY", "98f9a9461a5eed275514aad3fb514d53")


def get_ticker_data(ticker_symbol):
    """
    Fetches data for a single ticker using yfinance.
    Returns: { 'value': str, 'change': str, 'percent': float }
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        # Get fast info first
        info = ticker.fast_info
        
        price = None
        prev_close = None
        
        if hasattr(info, 'last_price') and info.last_price is not None:
            price = info.last_price
            prev_close = info.previous_close
        else:
            hist = ticker.history(period="2d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else price
        
        if price is None:
            return None

        change = price - prev_close
        percent = (change / prev_close) * 100
        
        sign = "+" if change >= 0 else ""
        return {
            "value": f"{price:,.2f}",
            "change": f"{sign}{change:,.2f}",
            "percent": f"{sign}{percent:,.2f}", 
            "raw_change": change,
            "raw_percent": percent
        }
    except Exception as e:
        print(f"Error fetching ticker {ticker_symbol}: {e}")
        return None

def get_fred_data(series_id, label_type="value"):
    """
    Fetches latest observation from FRED API.
    Returns dictionary with value, date, change (calculated if possible).
    """
    if not FRED_API_KEY:
        print(f"[FRED] Missing API Key. Skipping {series_id}")
        return None
        
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=2"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        observations = data.get('observations', [])
        
        if not observations:
            return None
            
        latest = observations[0]
        prev = observations[1] if len(observations) > 1 else None
        
        val_str = latest['value']
        date_str = latest['date'] # YYYY-MM-DD
        
        if val_str == '.':
            return None
            
        val = float(val_str)
        
        # Calculate change
        change_str = "0.00"
        percent_str = "0.00%"
        
        if prev and prev['value'] != '.':
            prev_val = float(prev['value'])
            change = val - prev_val
            pct = (change / prev_val) * 100 if prev_val != 0 else 0
            
            sign = "+" if change >= 0 else ""
            change_str = f"{sign}{change:,.2f}"
            percent_str = f"{sign}{pct:,.2f}%"

        # Formatting based on label_type
        formatted_val = f"{val:,.2f}"
        if label_type == "percent":
           formatted_val = f"{val:,.2f}%"
        elif label_type == "int":
           formatted_val = f"{int(val):,}"

        return {
            "value": formatted_val,
            "change": change_str,
            "percent": percent_str,
            "date": date_str,
            "next_date": "TBD" # FRED doesn't provide next release date easily in this endpoint
        }

    except Exception as e:
        print(f"[FRED] Error fetching {series_id}: {e}")
        return None

# --- Stocks ---

import crawler_service

# ... (Previous code)

# --- Stocks ---

def get_realtime_stocks():
    """Fetches stock data via Investing.com Crawling (30s job)"""
    # User requested consistency with Investing.com URLs.
    # Switching from yfinance to direct crawling.
    targets = {
        'sp_futures': 'https://kr.investing.com/indices/us-spx-500-futures',
        'dow_futures': 'https://kr.investing.com/indices/us-30-futures',
        'nasdaq_futures': 'https://kr.investing.com/indices/nq-100-futures',
        'wti': 'https://kr.investing.com/commodities/crude-oil',
        #'russell': 'https://kr.investing.com/indices/smallcap-2000', # 500 Error
        'vix': 'https://kr.investing.com/indices/volatility-s-p-500'
    }
    
    result = {}
    
    # Crawl each target
    for key, url in targets.items():
        # Use existing fetch_investing_price
        # It handles value, change, percent
        data = crawler_service.fetch_investing_price(url, key)
        if data:
            result[key] = data
            
    # Russell 2000 -> yfinance (^RUT)
    # Switched from Google Finance due to crawling instability (NaN% issue)
    russell = get_ticker_data('^RUT')
    if russell:
        result['russell'] = russell
            
    # Fear & Greed (Library or Crawl)
    fg = crawler_service.get_fear_greed_index()
    if fg:
        result['fear_greed'] = {
            "value": fg['value'],
            "change": "0", 
            "percent": fg['description'] 
        }
            
    return result

def get_daily_stocks():
    """Fetches daily stock-related data via Crawler (Daily job)"""
    result = {}
    
    # High Yield Spread (Restore Original: IndexerGo first)
    try:
        # Try IndexerGo (Original primary)
        hy = crawler_service.fetch_indexergo_data(
            'https://www.indexergo.com/series/?frq=M&idxDetail=13404', 'HighYield'
        )
        if hy:
            result['high_yield'] = hy
            print("[JOB] Successfully updated High Yield via IndexerGo")
        else:
            # Fallback to FRED
            print("[JOB] IndexerGo High Yield failed, falling back to FRED")
            fred_hy = get_fred_data('BAMLH0A0HYM2', label_type="value")
            if fred_hy:
                # Add dynamic URL for fallback
                fred_hy['url'] = "https://fred.stlouisfed.org/series/BAMLH0A0HYM2"
                result['high_yield'] = fred_hy
                print("[JOB] Successfully updated High Yield via FRED (Dynamic URL set)")

    except Exception as e:
        print(f"[JOB] Error updating High Yield: {e}")


        
    return result

# --- Rates ---

def get_realtime_rates():
    """Fetches live rates via yfinance & Investing.com (5m job)"""
    result = {}
    
    # 1. US 10Y Yield (yfinance)
    us_10y = get_ticker_data('^TNX')
    if us_10y:
        result['us_10y'] = us_10y
        
    # 2. US 2Y Yield (Investing.com)
    us_2y = crawler_service.fetch_investing_price(
        'https://kr.investing.com/rates-bonds/u.s.-2-year-bond-yield', 'US2Y'
    )
    if us_2y: result['us_2y'] = us_2y
    

    # 3. 10-2Y Spread (FRED API)
    # Changed from Investing.com Crawling to FRED API
    spread = get_fred_latest_two('T10Y2Y', 'US10Y2Y')
    if spread: 
        spread['url'] = 'https://fred.stlouisfed.org/series/T10Y2Y'
        result['us_10_2_spread'] = spread

    
    # 4. Japan 2Y (Investing.com)
    jp_2y = crawler_service.fetch_investing_price(
        'https://kr.investing.com/rates-bonds/japan-2-year-bond-yield', 'JP2Y'
    )
    if jp_2y: result['jp_2y'] = jp_2y
    
    # 5. Korea 10Y (Investing.com)
    kr_10y = crawler_service.fetch_investing_price(
        'https://kr.investing.com/rates-bonds/south-korea-10-year-bond-yield', 'KR10Y'
    )
    if kr_10y: result['kr_10y'] = kr_10y
    
    # 6. Korea 2Y (Investing.com)
    kr_2y = crawler_service.fetch_investing_price(
        'https://kr.investing.com/rates-bonds/south-korea-2-year-bond-yield', 'KR2Y'
    )
    if kr_2y: result['kr_2y'] = kr_2y
        
    return result

def get_daily_rates():
    """Fetches official rates via Investing.com Crawling (Daily job)"""
    result = {}
    
    # 1. Fed Funds Rate (Restore Original Strategy: Investing.com primary)
    try:
        # 1-1. Try Investing.com Crawling (Original)
        fed_inv = crawler_service.fetch_investing_calendar_actual(
            'https://kr.investing.com/economic-calendar/interest-rate-decision-168', 168, 'FedRate'
        )
        if fed_inv and fed_inv.get('value'):
            result['fed_rate'] = fed_inv
            print("[JOB] Successfully updated Fed Rate via Investing.com")
        else:
            # 1-2. Fallback to FRED API (Daily Effective Federal Funds Rate)
            print("[JOB] Investing.com Fed Rate failed, falling back to FRED (DFF)")
            fed_fred = get_fred_data('DFF', label_type="percent")
            if fed_fred:
                # Add dynamic URL for fallback to Daily Series
                fed_fred['url'] = "https://fred.stlouisfed.org/series/DFF"
                # If Investing.com provided next_date but no value, merge them
                if fed_inv and fed_inv.get('next_date'):
                    fed_fred['next_date'] = fed_inv['next_date']
                result['fed_rate'] = fed_fred
                print("[JOB] Successfully updated Fed Rate via FRED DFF (Dynamic URL set)")


    except Exception as e:
        print(f"[JOB] Error during Fed Rate recovery: {e}")





    
    # 2. SOFR (NY Fed API)
    sofr = crawler_service.fetch_ny_fed_sofr()
    if sofr: result['sofr'] = sofr
    
    # 3. Japan Policy Rate (Decision)
    jp_rate = crawler_service.fetch_investing_calendar_actual(
        'https://kr.investing.com/economic-calendar/boj-interest-rate-decision-164', 164, 'BOJRate'
    )
    if jp_rate: result['jp_policy'] = jp_rate
    
    # 4. Korea Base Rate (Decision) - Corrected ID 473
    kr_rate = crawler_service.fetch_investing_calendar_actual(
        'https://kr.investing.com/economic-calendar/south-korea-interest-rate-decision-473', 473, 'BOKRate'
    )
    if kr_rate: result['kr_base'] = kr_rate

    
    return result

# --- Exchange ---

def get_realtime_exchange():
    """Fetches live exchange rates via Investing.com Crawling (5m job)"""
    result = {}
    
    # DXY -> Investing.com
    dxy = crawler_service.fetch_investing_price(
        'https://kr.investing.com/currencies/us-dollar-index', 'DXY'
    )
    if dxy: result['dxy'] = dxy
    
    # USD/KRW -> yfinance (User Request)
    usd_krw = get_ticker_data('KRW=X')
    if usd_krw: result['usd_krw'] = usd_krw
    
    return result

def get_daily_exchange():
    """Fetches reserves etc. via Investing.com Crawling (Daily job)"""
    result = {}
    
    # Korea Reserves
    res = crawler_service.fetch_investing_calendar_actual(
        'https://kr.investing.com/economic-calendar/south-korea-fx-reserves-usd-1889', 1889, 'Reserves'
    )
    if res:
        result['foreign_reserves'] = res
        
    # Foreign Holding (KRX) via Pykrx
    # KRX Foreign Stock Holding (Switched to e-Nara Index Official Monthly Data)
    try:
        # Fetching official stats from Index.go.kr
        enara_data = crawler_service.fetch_enara_foreign_holding()
        if enara_data:
             result['foreign_bond'] = enara_data
             print("[JOB] Successfully updated Foreign Holding via e-Nara Index")
        else:
             print("[JOB] e-Nara Foreign Holding failed, checking fallback...")
             # Legacy Fallback (Likely to fail but kept as last resort)
             import backend.crawler.krx_crawler as krx_crawler
             krx_data = krx_crawler.get_foreign_holding_data()
             if krx_data:
                val_trillion = krx_data['value'] / 1000000000000
                result['foreign_bond'] = {
                    "value": f"{val_trillion:.1f}조",
                    "change": "",
                    "percent": krx_data['percent'],
                    "date": krx_data['date'],
                    "next_date": ""
                }
    except Exception as e:
        print(f"[JOB] Error updating Foreign Bond data: {e}")



    return result

# --- Economy ---

def get_daily_economy():
    """Fetches economic indicators via Investing.com Crawling (Daily job)"""
    result = {}
    
    # CCI (Consumer Confidence)
    cci = crawler_service.fetch_investing_calendar_actual(
        'https://kr.investing.com/economic-calendar/cb-consumer-confidence-48', 48, 'CCI'
    )
    if cci: result['cci'] = cci
    
    # Unemployment
    unemp = crawler_service.fetch_investing_calendar_actual(
        'https://kr.investing.com/economic-calendar/unemployment-rate-300', 300, 'Unemployment'
    )
    if unemp: result['unemployment'] = unemp
    
    # Non-Farm
    nfp = crawler_service.fetch_investing_calendar_actual(
        'https://kr.investing.com/economic-calendar/nonfarm-payrolls-227', 227, 'NFP'
    )
    if nfp: result['non_farm'] = nfp
        
    # PMI
    pmi = crawler_service.fetch_investing_calendar_actual(
        'https://kr.investing.com/economic-calendar/ism-manufacturing-pmi-173', 
        173, 'PMI'
    )
    if pmi: result['pmi'] = pmi
    
    # High Yield Spread
    # User Request: Use IndexerGo URL
    high_yield = crawler_service.fetch_indexergo_data(
        'https://www.indexergo.com/series/?frq=M&idxDetail=13404', 'HighYield'
    )
    if high_yield:
         result['high_yield'] = high_yield
    
    return result


# --- History Data (Charts) ---

def get_history_values_yf(ticker, period="1y"):
    """
    Fetches historical closing prices from yfinance.
    Returns: { 'dates': [str], 'values': [float] }
    """
    try:
        t = yf.Ticker(ticker)
        # Fetch Monthly data
        hist = t.history(period=period, interval="1mo")
        if hist.empty:
            return None
            
        dates = [d.strftime('%Y-%m-%d') for d in hist.index]
        values = [float(v) for v in hist['Close']]
        
        return {'dates': dates, 'values': values}
    except Exception as e:
        print(f"[History] Error fetching {ticker}: {e}")
        return None

def get_history_values_fred(series_id):
    """
    Fetches historical data from FRED API (1 year).
    Returns: { 'dates': [str], 'values': [float] }
    """
    if not FRED_API_KEY:
        return None
        
    try:
        # approx 1 year + buffer
        start_date = (datetime.now() - timedelta(days=400)).strftime('%Y-%m-%d')
        
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "observation_start": start_date,
            "sort_order": "asc",
            "frequency": "m"  # Monthly
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        observations = data.get('observations', [])
        
        dates = []
        values = []
        
        for obs in observations:
            val = obs['value']
            if val == '.': continue
            dates.append(obs['date'])
            values.append(float(val))
            
        return {'dates': dates, 'values': values}
    except Exception as e:
        print(f"[History] Error fetching FRED {series_id}: {e}")
        return None

def get_fred_latest_two(series_id, series_name):
    """Fetches the latest 2 valid data points from FRED to calculate change"""
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        print("FRED_API_KEY missing")
        return None
        
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 10  # Fetch more to handle missing dates ('.')
    }
    
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        observations = data.get("observations", [])
        valid_obs = [obs for obs in observations if obs["value"] != "."]
        
        if len(valid_obs) < 1:
            return None
            
        current_val = float(valid_obs[0]["value"])
        change_val = 0.0
        change_pct = 0.0
        
        if len(valid_obs) >= 2:
            prev_val = float(valid_obs[1]["value"])
            change_val = current_val - prev_val
            if prev_val != 0:
                change_pct = (change_val / prev_val) * 100
                
        # Format
        val_str = f"{current_val:.2f}"
        
        # Determine sign
        sign = ""
        if change_val > 0: sign = "+"
        
        change_str = f"{sign}{change_val:.2f}"
        pct_str = f"{sign}{change_pct:.2f}%"
        
        return {
            "value": val_str,
            "change": change_str,
            "percent": pct_str
        }
        
    except Exception as e:
        print(f"Error fetching FRED {series_id}: {e}")
        return None


def get_all_history_data():
    """
    Fetches 1-year history for all charts sequentially with delays to reduce memory pressure.
    """
    print("[History] Starting sequential fetch of all history data...")
    result = {}
    
    # Define tasks to fetch
    tasks = [
        # 1. Stocks (yfinance)
        ("sp_chart", "ES=F", "yf"),
        ("dow_chart", "YM=F", "yf"),
        ("nasdaq_chart", "NQ=F", "yf"),
        # 2. Economy (FRED)
        ("cci_chart", "UMCSENT", "fred"),
        ("unem_chart", "UNRATE", "fred"),
        # 3. Rates (FRED)
        ("us10_chart", "DGS10", "fred"),
        ("us2_chart", "DGS2", "fred"),
        ("spread_chart", "T10Y2Y", "fred"),
        # 4. Exchange (yfinance)
        ("dxy_chart", "DX-Y.NYB", "yf"),
        ("krw_chart", "KRW=X", "yf"),
    ]
    
    for chart_id, ticker_or_id, source in tasks:
        try:
            print(f"[History] Fetching {chart_id} ({ticker_or_id}) from {source}...")
            if source == "yf":
                data = get_history_values_yf(ticker_or_id)
            else:
                data = get_history_values_fred(ticker_or_id)
                
            if data:
                result[chart_id] = data
                print(f"[History] Success: {chart_id}")
            else:
                print(f"[History] Failed to fetch {chart_id}")
                
            # Memory safety delay
            time.sleep(1)
        except Exception as e:
            print(f"[History] Unexpected error while fetching {chart_id}: {e}")
    
    print(f"[History] Completed. Fetched {len(result)}/{len(tasks)} charts.")
    return result

