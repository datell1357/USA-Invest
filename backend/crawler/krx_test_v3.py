
import requests
import json

def test_krx_session_crawling():
    target_date = "20251212"
    
    otp_url = "http://data.krx.co.kr/comm/bld/getGenOtp.cmd"
    json_url = "http://data.krx.co.kr/comm/bld/getJsonData.cmd"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020503",
    }
    
    # Session use for Cookie persistence
    session = requests.Session()
    session.headers.update(headers)
    
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
    
    print("[Step 1] Requesting OTP...")
    try:
        otp_res = session.post(otp_url, data=params, timeout=10)
        otp_res.raise_for_status()
        
        otp = otp_res.text.strip() # 중요: 공백 제거
        print(f"OTP Raw Length: {len(otp)}")
        print(f"OTP Content: '{otp}'")
        
        if not otp:
            print("Failed to get OTP (Empty response)")
            return
            
        print("[Step 2] Requesting JSON Data with OTP code...")
        # Only 'code' param is needed usually
        data_params = {
            "code": otp
        }
        
        res = session.post(json_url, data=data_params, timeout=10)
        
        try:
            data = res.json()
            print("Success! JSON Data received.")
            if 'output' in data:
                print(f"Items found: {len(data['output'])}")
                if len(data['output']) > 0:
                    print("Sample Item:", data['output'][0])
            else:
                print("Output key missing. Data:", data)
        except json.JSONDecodeError:
            print("Failed to parse JSON")
            print("Preview:", res.text[:200])
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_krx_session_crawling()
