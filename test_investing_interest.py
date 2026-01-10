import requests
from bs4 import BeautifulSoup
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

def test_investing():
    url = "https://kr.investing.com/economic-calendar/interest-rate-decision-168"
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    print(f"Testing URL: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'id': 'eventHistoryTable168'})
            if table:
                print("SUCCESS: Table 'eventHistoryTable168' found!")
                # Print first data row
                rows = table.find('tbody').find_all('tr')
                if rows:
                    print(f"First Row: {rows[0].text.strip().replace('\\n', ' ')}")
            else:
                print("FAILURE: Table 'eventHistoryTable168' NOT found in HTML.")
                # Print a bit of HTML to see what's there
                print("HTML Snippet (first 500 chars):")
                print(response.text[:500])
        else:
            print(f"FAILURE: Received status {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_investing()
