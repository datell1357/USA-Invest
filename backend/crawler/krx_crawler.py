
from pykrx import stock
import pandas as pd
from datetime import datetime, timedelta

def get_foreign_holding_data():
    """
    Fetches the Foreign Holding Ratio (Market Cap based) of the entire KRX market (KOSPI+KOSDAQ+KONEX).
    Retries up to 7 days back to find the latest available CLOSE data.
    
    Returns:
        dict: {
            'value': float (Foreign Market Cap in KRW),
            'percent': str (Ratio with %),
            'date': str (YYYY-MM-DD),
            'total_cap': float (Total Market Cap in KRW)
        } or None if failed.
    """
    
    # KRX website 'Foreign Ownership Trend' uses Closing Data.
    # If currently intra-day (before 16:00), use yesterday's data to match the website.
    now = datetime.now()
    if now.hour < 16:
        search_date = now - timedelta(days=1)
    else:
        search_date = now
    
    for _ in range(7): # Retry for a week
        date_str = search_date.strftime("%Y%m%d")
        
        try:
            # 1. Get Market Cap (has Listed Shares, Market Cap) for ALL markets
            # market="ALL" includes KOSPI, KOSDAQ, KONEX
            try:
                df_cap = stock.get_market_cap(date_str, market="ALL")
            except Exception:
                df_cap = pd.DataFrame()

            if df_cap.empty:
                search_date -= timedelta(days=1)
                continue
                
            # 2. Get Foreign Holding Qty for ALL markets
            try:
                df_foreign = stock.get_exhaustion_rates_of_foreign_investment_by_ticker(date_str, market="ALL")
            except Exception:
                df_foreign = pd.DataFrame()
                
            if df_foreign.empty:
                search_date -= timedelta(days=1)
                continue
                
            # 3. Join & Calculate
            # Ensure index intersection (Ticker)
            common_tickers = df_cap.index.intersection(df_foreign.index)
            
            if common_tickers.empty:
                search_date -= timedelta(days=1)
                continue
                
            # Filter dataframes
            df_c = df_cap.loc[common_tickers]
            df_f = df_foreign.loc[common_tickers]
            
            # Calculate Foreign Market Cap per ticker
            # Foreign Mkt Cap = Foreign Holding Shares * Current Price (Close)
            # check column name usually '종가'
            if '종가' in df_c.columns:
                price = df_c['종가']
            else:
                 # Fallback if column name differs
                price = df_c.iloc[:, 0]
            
            foreign_shares = df_f['보유수량']
            
            # Calculate Foreign Market Cap
            foreign_mkt_cap_series = foreign_shares * price
            
            total_foreign_cap = foreign_mkt_cap_series.sum()
            total_mkt_cap_all = df_c['시가총액'].sum()
            
            if total_mkt_cap_all == 0:
                search_date -= timedelta(days=1)
                continue
                
            ratio = (total_foreign_cap / total_mkt_cap_all) * 100
            
            # Formatting
            date_formatted = search_date.strftime("%Y-%m-%d")
            
            return {
                "value": float(total_foreign_cap), # Raw value
                "percent": f"{ratio:.2f}%",
                "date": date_formatted,
                "total_cap": float(total_mkt_cap_all)
            }
            
        except Exception as e:
            print(f"[KRX Crawler] Error on {date_str}: {e}")
            search_date -= timedelta(days=1)
            
    print("[KRX Crawler] Failed to find data within 7 days.")
    return None

if __name__ == "__main__":
    data = get_foreign_holding_data()
    print(data)
