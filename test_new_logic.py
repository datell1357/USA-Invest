
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from crawler_service import fetch_enara_foreign_holding
from finance_service import get_daily_rates

def test_enara():
    print("--- Testing e-Nara Foreign Holding ---")
    data = fetch_enara_foreign_holding()
    if data:
        print(f"Success: {data}")
    else:
        print("Failed to fetch e-Nara data")

def test_hybrid_fed():
    print("\n--- Testing Hybrid Fed Rate ---")
    # This requires FRED_API_KEY environment variable. 
    # I will mock the API key for local test if needed, but here I want to see if the structure works.
    data = get_daily_rates()
    if data and 'fed_rate' in data:
        print(f"Success: {data['fed_rate']}")
    else:
        print("Failed to fetch Fed Rate (Check API Key)")

if __name__ == "__main__":
    test_enara()
    # test_hybrid_fed() # Skip if key not set in local env
