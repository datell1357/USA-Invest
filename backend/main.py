from fastapi import FastAPI
from fastapi import Response
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import uvicorn
import finance_service
from fastapi.staticfiles import StaticFiles
import os
import sys
import time
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Add backend directory and project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

app = FastAPI()

# 글로벌 캐시 추가
CACHE = {
    "stocks": {},
    "economy": {},
    "rates": {},
    "exchange": {},
    # [NEW] History Cache
    "history": {}
}

LAST_UPDATE = { "stocks": None }
NEXT_UPDATE = { "stocks": None }

scheduler = BackgroundScheduler(timezone="Asia/Seoul")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def safe_update_cache(category, new_data):
    """Updates the cache category with new keys, preserving existing ones."""
    if new_data:
        CACHE[category].update(new_data)

# --- Stocks Jobs ---

def update_realtime_stocks_job():
    try:
        # print("[JOB] Updating stocks realtime (30 sec)")
        data = finance_service.get_realtime_stocks()
        safe_update_cache("stocks", data)

        now = datetime.now()
        LAST_UPDATE["stocks"] = now
        NEXT_UPDATE["stocks"] = now + timedelta(seconds=30)
    except Exception as e:
        print("[ERROR] update_realtime_stocks_job:", e)

def update_daily_stocks_job():
    try:
        print("[JOB] Updating stocks daily (High Yield, etc.)")
        data = finance_service.get_daily_stocks()
        safe_update_cache("stocks", data)
    except Exception as e:
        print("[ERROR] update_daily_stocks_job:", e)

# --- Rates Jobs ---

def update_realtime_rates_job():
    # print("[JOB] Updating rates realtime (5 min)")
    data = finance_service.get_realtime_rates()
    safe_update_cache("rates", data)

def update_daily_rates_job():
    print("[JOB] Updating rates daily (Fed Rate, etc.)")
    data = finance_service.get_daily_rates()
    safe_update_cache("rates", data)

# --- Exchange Jobs ---

def update_realtime_exchange_job():
    # print("[JOB] Updating exchange realtime (5 min)")
    data = finance_service.get_realtime_exchange()
    safe_update_cache("exchange", data)

def update_daily_exchange_job():
    print("[JOB] Updating exchange daily (Reserves, etc.)")
    data = finance_service.get_daily_exchange()
    safe_update_cache("exchange", data)

# --- Economy Jobs ---

def update_daily_economy_job():
    print("[JOB] Updating economy daily (00:00, 12:00)")
    data = finance_service.get_daily_economy()
    safe_update_cache("economy", data)

# --- History Jobs (NEW) ---

def update_history_job():
    print("[JOB] Updating history data (Daily)")
    try:
        data = finance_service.get_all_history_data()
        # History replaces entire dict if successful
        if data:
            CACHE["history"] = data
    except Exception as e:
        print(f"[ERROR] update_history_job: {e}")

# --- API Routes ---

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.head("/")
def head_root():
    return Response(status_code=200)

@app.head("/health")
def head_health():
    return Response(status_code=200)

@app.get("/api/finance/stocks")
def api_stocks():
    return CACHE["stocks"]

@app.get("/api/finance/economy")
def api_economy():
    return CACHE["economy"]

@app.get("/api/finance/rates")
def api_rates():
    return CACHE["rates"]

@app.get("/api/finance/exchange")
def api_exchange():
    return CACHE["exchange"]

@app.get("/api/finance/history")
def api_history():
    """Returns 1-year history data for charts."""
    return CACHE["history"]
    
@app.get("/api/timer")
def api_timer():
    if not LAST_UPDATE["stocks"] or not NEXT_UPDATE["stocks"]:
        return {"last_update": None, "next_update": None}

    return {
        "last_update": int(LAST_UPDATE["stocks"].timestamp() * 1000),
        "next_update": int(NEXT_UPDATE["stocks"].timestamp() * 1000)
    }

# Startup Jobs Wrapper
def run_startup_jobs():
    print("[Startup] Executing initial data fetch...")
    start_time = time.time()
    
    def log_category_data(category):
        data = CACHE.get(category, {})
        if data:
            print(f"  [Data] {category.capitalize()}:")
            for key, val in data.items():
                if isinstance(val, dict):
                    v = val.get('value', 'N/A')
                    p = val.get('percent', '')
                    print(f"    - {key}: {v} ({p})")
        else:
            print(f"  [Warn] No data found in category '{category}'")

    try:
        print("[Startup] 1/8: Realtime Stocks...")
        update_realtime_stocks_job()
        log_category_data("stocks")
        time.sleep(2)
        
        print("[Startup] 2/8: Realtime Rates...")
        update_realtime_rates_job()
        log_category_data("rates")
        time.sleep(2)
        
        print("[Startup] 3/8: Realtime Exchange...")
        update_realtime_exchange_job()
        log_category_data("exchange")
        time.sleep(2)
        
        print("[Startup] 4/8: Daily Stocks (High Yield, etc)...")
        update_daily_stocks_job()
        log_category_data("stocks") # Updated again
        time.sleep(2)
        
        print("[Startup] 5/8: Daily Rates (Fed Rate, etc)...")
        update_daily_rates_job()
        log_category_data("rates") # Updated again
        time.sleep(2)
        
        print("[Startup] 6/8: Daily Exchange (Reserves, etc)...")
        update_daily_exchange_job()
        log_category_data("exchange") # Updated again
        time.sleep(2)
        
        print("[Startup] 7/8: Daily Economy...")
        update_daily_economy_job()
        log_category_data("economy")
        # History Data move to separate delayed job to reduce startup load

        if CACHE["history"]:
            print(f"  [Data] History: Loaded {len(CACHE['history'])} indicators.")
        
        elapsed = time.time() - start_time
        print(f"[Startup] Initial data fetch completed in {elapsed:.2f} seconds.")
    except Exception as e:
        print(f"[Startup] Error during initial fetch: {e}")


@app.on_event("startup")
def start_scheduler():
    # Run core data jobs once on startup to populate cache
    scheduler.add_job(run_startup_jobs)
    
    # Run heavy History job with 1 minute delay to avoid startup bottleneck
    scheduler.add_job(update_history_job, next_run_time=datetime.now() + timedelta(minutes=1))

    
    # 30초: Stocks Realtime
    scheduler.add_job(update_realtime_stocks_job, "interval", seconds=30)

    # 5분: Rates & Exchange Realtime
    scheduler.add_job(update_realtime_rates_job, "interval", minutes=5)
    scheduler.add_job(update_realtime_exchange_job, "interval", minutes=5)

    # 하루 2회 (00:00, 12:00): Daily Jobs (Formerly Rollover/Static)
    # Applying strictly to all "daily" fetchers
    daily_jobs = [
        update_daily_stocks_job, 
        update_daily_rates_job, 
        update_daily_exchange_job, 
        update_daily_economy_job
    ]
    
    for job in daily_jobs:
        scheduler.add_job(job, "cron", hour=0, minute=0)
        scheduler.add_job(job, "cron", hour=12, minute=0)

    # History Job (5분 오프셋)
    scheduler.add_job(update_history_job, "cron", hour=0, minute=5)
    scheduler.add_job(update_history_job, "cron", hour=12, minute=5)


    scheduler.start()

# Serve Static Files (Frontend)
try:
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
except Exception as e:
    print(f"Failed to mount static files: {e}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
