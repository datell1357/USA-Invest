
import requests
import datetime
import json

def test_krx_crawling():
    # Target Date: 20241213 (Friday) or nearest weekday
    # Today is 2025-12-15 (Mon), so let's try 20251212 (Fri)
    target_date = "20251212"
    
    url = "http://data.krx.co.kr/comm/bld/getJsonData.cmd"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020503",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    # Estimated BLD code for '종목별 외국인 보유현황'
    # dbms/MDC/STAT/standard/MDCSTAT03501
    params = {
        "bld": "dbms/MDC/STAT/standard/MDCSTAT03501",
        "mktId": "ALL", # KOSPI + KOSDAQ + KONEX
        "trdDd": target_date,
        "share": "1", # Shares
        "money": "1",
        "csvxls_isNo": "false"
    }
    
    print(f"Requesting KRX data for {target_date}...")
    try:
        res = requests.post(url, data=params, headers=headers, timeout=10)
        res.raise_for_status()
        
        data = res.json()
        print("Response received.")
        
        # Check output structure
        if "output" in data:
            print(f"Items found: {len(data['output'])}")
            if len(data['output']) > 0:
                print("First Item Sample:")
                print(data['output'][0])
                
                # Validation: Look for 'ISU_NM' (Item Name) and 'FORN_HD_QTY' (Foreigner Holding Qty)
                # Note: Keys might be different, let's inspect.
        else:
            print("No 'output' key in response. Raw data:")
            print(data)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_krx_crawling()
