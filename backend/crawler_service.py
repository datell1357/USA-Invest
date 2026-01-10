import requests
from bs4 import BeautifulSoup
import fear_and_greed
import random
import time
from datetime import datetime

# User-Agent list to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

def get_fear_greed_index():
    """
    Fetches Fear and Greed Index using 'fear-and-greed' library.
    """
    try:
        index_data = fear_and_greed.get()
        return {
            "value": str(int(index_data.value)),
            "description": index_data.description,
            "last_update": index_data.last_update.isoformat() if hasattr(index_data.last_update, 'isoformat') else str(index_data.last_update)
        }
    except Exception as e:
        print(f"[Crawler] Error fetching Fear & Greed: {e}")
        return None

def fetch_investing_price(url, name="Asset"):
    """
    Crawls Investing.com page to get the main price/yield.
    Targeting 'instrument-price-last' or modern class selectors.
    """
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.google.com/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5) # Reduced timeout to 5s
        if response.status_code != 200:
            print(f"[Crawler] Failed to fetch {name}: Status {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Strategy 1: data-test attribute (Most reliable for legacy/desktop pages)
        price_el = soup.find(attrs={'data-test': 'instrument-price-last'})
        change_el = soup.find(attrs={'data-test': 'instrument-price-change'})
        percent_el = soup.find(attrs={'data-test': 'instrument-price-change-percent'})
        
        # Strategy 2: Specific classes for newer Investing.com layout
        if not price_el:
            # Look for huge text class usually found in header
            # text-5xl/4xl font-bold ...
            price_el = soup.find('div', class_=lambda x: x and 'text-5xl' in x and 'font-bold' in x)
        
        if price_el:
            price = price_el.text.strip()
            change = change_el.text.strip() if change_el else "0.00"
            percent = percent_el.text.strip() if percent_el else "0.00%"
            
            # Clean up parenthesis in percent "(+0.5%)" -> "+0.5%"
            percent = percent.replace('(', '').replace(')', '')

            return {
                "value": price,
                "change": change,
                "percent": percent
            }
        
        print(f"[Crawler] Could not find price element for {name}")
        return None
        
    except Exception as e:
        print(f"[Crawler] Error crawling {name}: {e}")
        return None

def fetch_investing_calendar_actual(url, event_id, name="Event"):
    """
    Crawls Investing.com Economic Calendar for a specific event's latest 'Actual' value.
    Table ID: 'eventHistoryTable{event_id}'
    """
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.google.com/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for the history table
        table = soup.find('table', {'id': f'eventHistoryTable{event_id}'})
        
        if not table:
             print(f"[Crawler] Calendar table not found for {name} (ID: {event_id})")
             return None
             
        # Get tbody rows
        tbody = table.find('tbody')
        if not tbody: return None
        
        rows = tbody.find_all('tr')
        if not rows: return None
        
        # Iterate rows
        # Strategy: 
        # 1. First row with NO Actual value -> Next Release Date (if date is valid)
        # 2. First row WITH Actual value -> Current Release
        
        history = []
        next_date_str = ""
        
        import re
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 3: continue
            
            # Col 0: Date "2025년 12월 24일 (12월)"
            # Col 2: Actual
            raw_date = cols[0].text.strip()
            actual_str = cols[2].text.strip()
            
            # Try parse date YYYY-MM-DD
            parsed_date = ""
            # Regex for "YYYY년 MM월 DD일"
            match = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', raw_date)
            if match:
                y, m, d = match.groups()
                parsed_date = f"{y}-{int(m):02d}-{int(d):02d}"
            else:
                # Fallback or specific format
                parsed_date = raw_date
            
            # Check if this is a future/next event (No Actual Value)
            # Ensure we only grab the *first* such row as the next date
            is_empty_actual = (not actual_str or actual_str == '\xa0')
            
            if is_empty_actual:
                if not next_date_str and parsed_date:
                    next_date_str = parsed_date
                continue
            
            # If has actual value, adds to history
            history.append({
                "date": parsed_date, # Use parsed clean date
                "value_str": actual_str
            })
            if len(history) >= 2: break
            
        if not history: return None
        
        latest = history[0]
        val_str = latest['value_str']
        date_str = latest['date']
        
        change_str = "0.00"
        pct_str = "0.00%"
        
        # Calculate Change if previous data exists
        if len(history) >= 2:
            prev = history[1]
            
            def parse_val(s):
                # Remove common units
                s = s.replace(',', '').replace('B', '').replace('M', '').replace('k', '').replace('%', '')
                try:
                    return float(s)
                except:
                    return None
                    
            curr_float = parse_val(val_str)
            prev_float = parse_val(prev['value_str'])
            
            if curr_float is not None and prev_float is not None:
                change = curr_float - prev_float
                pct = (change / prev_float) * 100 if prev_float != 0 else 0
                
                sign = "+" if change >= 0 else ""
                change_str = f"{sign}{change:,.2f}"
                pct_str = f"{sign}{pct:,.2f}%"
                
        return {
            "value": val_str,
            "date": date_str,
            "change": change_str, 
            "percent": pct_str,
            "next_date": next_date_str 
        }
            
        return None

    except Exception as e:
        print(f"[Crawler] Error crawling calendar {name}: {e}")
        return None

def fetch_indexergo_data(url, name="IndexerGo"):
    """
    Crawls IndexerGo.com for specific index data (e.g. High Yield Spread).
    """
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }


    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"[Crawler] Failed to fetch {name}: Status {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Method 1: Try Table Row (More structured)
        tables = soup.find_all('table')
        if tables:
            # Assuming first table is the data table
            # Rows: Header is usually row 0. Data starts row 1.
            rows = tables[0].find_all('tr')
            if len(rows) > 1:
                row = rows[1] 
                cols = row.find_all(['td', 'th'])
                
                # output: Match verified via test_indexergo.py
                # Cell 0 (th): Date
                # Cell 1 (td): Value (3.08)
                # Cell 2 (td): Change \n Percent (+ 0.16 ...)
                
                if len(cols) >= 3:
                    date_str = cols[0].text.strip()
                    val_str = cols[1].text.strip()
                    
                    # Col 2 has Change AND Percent separated by whitespace/newlines
                    # Text is like "+            0.16 \n 5.48%"
                    # We must remove inner spaces to keep "+0.16" as one token
                    combined_text = cols[2].text.strip().replace(' ', '')
                    # Now it looks like "+0.16\n5.48%"
                    
                    raw_col2 = combined_text.split()
                    
                    change_str = "-"
                    pct_str = "-"
                    
                    if len(raw_col2) >= 1:
                        change_str = raw_col2[0] # +0.16
                    if len(raw_col2) >= 2:
                        pct_str = raw_col2[1] # 5.48% (includes %)
                        
                    # Remove % from pct_str if UI adds it? 
                    # UI updateUI logic: `if (rawPct) disp += ` (${formatNumber(rawPct)}%)`;`
                    # formatNumber handles float.
                    # IndexerGo returns "5.48%". 
                    # If I send "5.48%", formatNumber("5.48%") might fail or result `NaN`.
                    # backend should probably send raw float if possible, or clean string.
                    # Let's clean '%' out of pct_str for safety, or ensure UI handles it.
                    # UI code: `!String(txt).includes('%')` logic exists for VALUE.
                    # For Change/Pct: `rawPct` is used in `formatNumber`.
                    pct_str = pct_str.replace('%', '')

                    if val_str:
                         return {
                             "value": val_str,
                             "date": date_str,
                             "change": change_str,
                             "percent": pct_str
                         }
                elif len(cols) >= 2:
                     # Fallback if change columns missing
                    date_str = cols[0].text.strip()
                    val_str = cols[1].text.strip()
                    if val_str:
                         return {
                             "value": val_str,
                             "date": date_str,
                             "change": "-",
                             "percent": "-"
                         }

        if "(" in title and "%)" in title:
            # Extract "3.08" from "(3.08%)"
            import re
            match = re.search(r'\(([\d\.]+)', title)
            if match:
                return {
                    "value": match.group(1),
                    "change": "-",
                    "percent": "-"
                }
                
        return None

    except Exception as e:
        print(f"[Crawler] Error crawling IndexerGo {name}: {e}")
        return None

def fetch_ny_fed_sofr():
    """
    Fetches SOFR rate and calculates change from NY Fed API.
    URL: https://markets.newyorkfed.org/api/rates/secured/sofr/search.json
    """
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    url = f"https://markets.newyorkfed.org/api/rates/secured/sofr/search.json?startDate={start_str}&endDate={end_str}&type=sofr"
    
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"[Crawler] NY Fed API failed: {resp.status_code}")
            return None
            
        data = resp.json()
        ref_rates = data.get('refRates', [])
        
        # Ensure sorted by date descending just in case
        ref_rates.sort(key=lambda x: x['effectiveDate'], reverse=True)
        
        # Filter strictly for 'SOFR' type if API returns mixed (though type=sofr param should filter)
        sofr_rates = [r for r in ref_rates if r.get('type') == 'SOFR']
        
        if not sofr_rates:
            print("[Crawler] No SOFR data found in response")
            return None
            
        latest = sofr_rates[0]
        val = latest.get('percentRate')
        date_str = latest.get('effectiveDate')
        
        change_str = "0.00"
        pct_str = "0.00%"
        
        if len(sofr_rates) > 1:
            prev = sofr_rates[1]
            prev_val = prev.get('percentRate')
            
            if val is not None and prev_val is not None:
                 change = val - prev_val
                 pct = (change / prev_val) * 100 if prev_val != 0 else 0
                 
                 sign = "+" if change >= 0 else ""
                 change_str = f"{sign}{change:,.2f}"
                 pct_str = f"{sign}{pct:,.2f}%"
        
        if val is not None:
             # NY Fed Value is percentage (3.66 means 3.66%)
             return {
                 "value": f"{val:.2f}%",
                 "date": date_str,
                 "change": change_str,
                 "percent": pct_str
             }
        
        return None

    except Exception as e:
        print(f"[Crawler] Error fetching NY Fed SOFR: {e}")
        return None

def fetch_google_finance(url, name="Asset"):
    """
    Crawls Google Finance for Price, Change, Percent.
    URL: https://www.google.com/finance/quote/RUT:INDEXRUSSELL?hl=ko
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code != 200:
            print(f"[Crawler] Google Finance failed {name}: {resp.status_code}")
            return None
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 1. Price
        # Class 'YMlKec fxKbKc' is the standard large price class in Google Finance
        price_el = soup.find(class_="YMlKec fxKbKc")
        if not price_el:
            print(f"[Crawler] Google Finance Price not found for {name}")
            return None
            
        price_str = price_el.text.strip()
        
        # 2. Change & Percent
        # Strategy: Go up to the main container and look for change classes
        # The main header block usually contains the price and the change badge
        container = price_el.parent
        # Traverse up 2-3 levels to find the block containing both Price and Change
        # Usually Price is in a div, Change is in a sibling div or span
        # Typical classes for Change: 'P2Luy' (Green), 'NDrR4' (Red), 'BAftM' (Grey/Zero)
        
        change_str = "-"
        pct_str = "-"
        
        # Strategy: Go up to the header container and search for change classes
        # Based on debug output, the header block is about 6-7 levels up?
        # Let's go up 6 levels and search downwards for known Google Finance change classes.
        # Classes: 'P2Luy' (Green), 'NDrR4' (Red), 'BAftM' (Grey)
        
        found_block = None
        curr = price_el
        
        target_container = None
        # Go up 6 levels to find a common container
        for _ in range(6):
            if curr.parent:
                curr = curr.parent
        target_container = curr
        
        if target_container:
            cands = target_container.find_all(class_=["P2Luy", "NDrR4", "BAftM"])
            
            # Filter candidates that are essentially numeric
            numeric_cands = []
            for c in cands:
                t = c.text.strip()
                # Must contain digits
                if any(k.isdigit() for k in t):
                    numeric_cands.append(t)
            
            # Usually we find [ChangeValue, PercentValue] or sometimes doubled.
            # We need to distinguish Value from Percent.
            val_c = None
            pct_c = None
            
            # Heuristic: Percent has '%', Value usually doesn't (or we prioritize %)
            for t in numeric_cands:
                if '%' in t:
                     if not pct_c: pct_c = t
                else:
                     if not val_c: val_c = t
            
            if val_c: change_str = val_c
            if pct_c: pct_str = pct_c
            
        return {
            "value": price_str,
            "change": change_str,
            "percent": pct_str
        }

    except Exception as e:
        print(f"[Crawler] Error Google Finance {name}: {e}")
        return None

if __name__ == "__main__":
    pass
