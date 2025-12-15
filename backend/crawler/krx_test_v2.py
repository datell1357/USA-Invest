
import requests
import json
import time

def test_krx_otp_crawling():
    target_date = "20251212" # Friday
    
    # 1. Generate OTP
    otp_url = "http://data.krx.co.kr/comm/bld/getGenOtp.cmd"
    json_url = "http://data.krx.co.kr/comm/bld/getJsonData.cmd"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020503",
    }
    
    # Params for OTP Generation
    # BLD Code: dbms/MDC/STAT/standard/MDCSTAT03501 (종목별 외국인 보유현황)
    params = {
        "bld": "dbms/MDC/STAT/standard/MDCSTAT03501",
        "mktId": "ALL",
        "trdDd": target_date,
        "share": "1",
        "money": "1",
        "csvxls_isNo": "false",
        "name": "form",
        "url": "dbms/MDC/STAT/standard/MDCSTAT03501"
    }
    
    print(f"[Step 1] Requesting OTP for {target_date} with bld={params['bld']}...")
    try:
        otp_res = requests.post(otp_url, data=params, headers=headers, timeout=10)
        otp_res.raise_for_status()
        
        otp = otp_res.text
        print(f"OTP Received: {otp[:20]}...") 
        
        # 2. Get JSON Data using OTP
        # KRX often uses 'code' param for the OTP in getJsonData.cmd or download.cmd
        # But wait, getJsonData.cmd usually takes 'bld' directly WITHOUT OTP if not downloading a file?
        # Let's try sending the OTP as 'code' to getJsonData.cmd as a fallback.
        # Actually, for getJsonData.cmd, usually we just send the params directly.
        # But the previous attempt failed. 
        # Let's try downloading via 'download.cmd' just to see if it works, 
        # OR try getJsonData.cmd with the OTP if the direct param failed.
        
        # Scenario A: The previous failure was due to missing headers? (Referer was present)
        # Scenario B: getGenOtp.cmd is needed for Download, but getJsonData.cmd is for AJAX.
        
        # Let's retry getJsonData.cmd with full headers and maybe slightly different headers.
        # And also print the text response if JSON fails.
        
        print("[Step 2] Retrying getJsonData.cmd directly with full headers...")
        params2 = {
            "bld": "dbms/MDC/STAT/standard/MDCSTAT03501",
            "mktId": "ALL",
            "trdDd": target_date,
            "share": "1",
            "money": "1",
            "csvxls_isNo": "false"
        }
        res = requests.post(json_url, data=params2, headers=headers, timeout=10)
        
        print(f"Status Code: {res.status_code}")
        try:
            data = res.json()
            print("Success! JSON Data received.")
            if 'output' in data and len(data['output']) > 0:
                print(data['output'][0])
                return
        except:
            print("Failed to parse JSON. Response text preview:")
            print(res.text[:500])
            
            # If direct JSON failed, maybe we need to use the OTP to download?
            # But we want JSON for the app.
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_krx_otp_crawling()
