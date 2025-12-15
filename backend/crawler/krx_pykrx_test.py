
from pykrx import stock
import pandas as pd
from datetime import datetime, timedelta

def test_pykrx():
    # Target Date: 20251212 (Friday)
    target_date = "20251212"
    
    print(f"Fetching Foreign Investment Data for {target_date}...")
    try:
        # get_exhaustion_rates_of_foreign_investment_by_ticker
        # Returns: 종목코드, 종목명, 상장주식수, 외국인보유수량, 지분율, 한도수량, 소진율
        df = stock.get_exhaustion_rates_of_foreign_investment_by_ticker(target_date, market="ALL")
        
        if df.empty:
            print("Dataframe is empty.")
            return

        print("Data Sample:")
        print(df.head())
        
        # Calculate Total Foreign Holdings for the entire market
        # The user wants "Foreign Bond Buying" replacement.
        # But wait, does the user want specific ticker data or the WHOLE MARKET aggregate?
        # "최근 일자에 대한 외국인 보유현황 과 지분을 크롤링해서... 외국인 채권매수 항목에 포함해줘."
        # The previous item was "Foreign Bond Buying", which is a macro indicator.
        # So likely the user wants the TOTAL Foreign Holding Ratio of the Korean Market (KOSPI + KOSDAQ).
        
        total_shares = df['상장주식수'].sum()
        foreign_shares = df['보유수량'].sum()
        
        if total_shares > 0:
            ratio = (foreign_shares / total_shares) * 100
            print(f"\n[Aggregate Result]")
            print(f"Total Shares: {total_shares:,}")
            print(f"Foreign Shares: {foreign_shares:,}")
            print(f"Foreign Ratio: {ratio:.2f}%")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_pykrx()
