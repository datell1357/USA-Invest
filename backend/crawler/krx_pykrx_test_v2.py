
from pykrx import stock
import pandas as pd

def test_pykrx_market_cap():
    target_date = "20251212"
    
    print(f"Fetching Market Cap Data for {target_date}...")
    try:
        # get_market_cap_by_ticker returns:
        # 시가총액, 거래량, 거래대금, 상장주식수
        # But it doesn't have 'Foreign Holding' amount directly?
        # Wait, get_market_cap doesn't return foreign holdings.
        
        # We need BOTH:
        # 1. Foreign Holding Qty (from get_exhaustion_rates... or similar)
        # 2. Current Price (to calculate Foreign Market Cap)
        # OR find a function that gives Foreign Market Cap directly.
        
        # Let's verify get_exhaustion_rates columns again.
        # It has '보유수량' (Foreign Holding Qty).
        # We need Price to get Foreign Market Cap = Holding Qty * Price.
        
        # Step 1: Get Prices
        df_price = stock.get_market_cap_by_ticker(target_date, market="ALL")
        # Columns: 시가총액, 거래량, 거래대금, 상장주식수
        # Note: df_price index is Ticker
        
        # Step 2: Get Foreign Holdings
        df_foreign = stock.get_exhaustion_rates_of_foreign_investment_by_ticker(target_date, market="ALL")
        # Columns: 상장주식수, 보유수량, 지분율, 한도수량, 한도소진률
        
        # Merge
        # df_foreign index is also Ticker.
        
        # Let's join them.
        df = df_price.join(df_foreign[['보유수량']], on='티커', how='inner') # '보유수량' column name check needed
        
        # Calculate Market Caps
        # Price is not directly here? 
        # Market Cap = Price * Shares. 
        # Price = Market Cap / Shares (approx)
        # Or use get_market_ohlcv for Close Price.
        
        # Efficient way:
        # Foreign Market Cap = (Foreign Shares / Total Shares) * Total Market Cap? 
        # No, that assumes uniform distribution? No, that's exact if we do it per ticker.
        # Foreign Market Cap (Ticker) = (Foreign Shares / Total Shares) * Total Market Cap (Ticker)
        
        # Let's try this calculation.
        
        total_mkt_cap_all = df_price['시가총액'].sum()
        
        # Calculate Foreign Market Cap per ticker
        # Foreign Shares from df_foreign
        # Total Shares from df_price (or df_foreign)
        # Total Market Cap from df_price
        
        # Make sure indices match
        # Let's iterate or use pandas vector operation
        
        # We need to ensure we use the same tickers
        common_tickers = df_price.index.intersection(df_foreign.index)
        
        df_p = df_price.loc[common_tickers]
        df_f = df_foreign.loc[common_tickers]
        
        # Foreign Market Cap = (Foreign Holding / Listed Shares) * Market Cap
        # Note: '상장주식수' might differ slightly if data sources differ, but usually same.
        
        foreign_mkt_cap_series = (df_f['보유수량'] / df_f['상장주식수']) * df_p['시가총액']
        
        total_foreign_cap = foreign_mkt_cap_series.sum()
        
        ratio = (total_foreign_cap / total_mkt_cap_all) * 100
        
        print(f"\n[Market Cap Based Result]")
        print(f"Total Market Cap: {total_mkt_cap_all:,}")
        print(f"Foreign Market Cap: {total_foreign_cap:,.0f}")
        print(f"Foreign Ratio (Mkt Cap): {ratio:.2f}%")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_pykrx_market_cap()
