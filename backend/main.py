from fastapi import FastAPI
from fastapi import Response
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import uvicorn
import finance_service

app = FastAPI()

# 글로벌 캐시 추가
CACHE = {
    "stocks": {},
    "economy": {},
    "rates": {},
    "exchange": {}
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

from fastapi.staticfiles import StaticFiles
import os

# Mount the parent directory to serve index.html
# Careful not to expose sensitive files if meaningful, but for this demo it's fine.
# We mount it at the root.
# Note: Put this AFTER API routes so API takes precedence, OR use a specific path.
# Actually, for 'html=True' at root, it acts as a catch-all.
# Better to explicit API routes first.

def update_stocks_job():
    try:
        print("[JOB] Updating stocks (30 sec)")
        CACHE["stocks"] = finance_service.get_stocks_data()

        now = datetime.now()

        LAST_UPDATE["stocks"] = now
        NEXT_UPDATE["stocks"] = now + timedelta(seconds=30)

    except Exception as e:
        print("[ERROR] update_stocks_job:", e)

def update_rates_job():
    print("[JOB] Updating rates (5 min)")
    CACHE["rates"] = finance_service.get_rates_data()

def update_exchange_job():
    print("[JOB] Updating exchange (5 min)")
    CACHE["exchange"] = finance_service.get_exchange_data()

def update_economy_job():
    print("[JOB] Updating economy (00:00, 12:00)")
    CACHE["economy"] = finance_service.get_economy_data()

# Render Health Check 용도. 항상 200 OK를 리턴합니다.
@app.get("/health")
def health_check():
    return {"status": "ok"}

# UptimeBot Health Check 용도. 항상 200 OK를 리턴합니다.    
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
    
@app.on_event("startup")
def start_scheduler():
    update_stocks_job()
    update_rates_job()
    update_exchange_job()
    update_economy_job()
    
    # 30초 주기: 변동성 큰 데이터
    scheduler.add_job(update_stocks_job, "interval", seconds=30)

    # 5분 주기: 변동성 적은 데이터
    scheduler.add_job(update_rates_job, "interval", minutes=5)
    scheduler.add_job(update_exchange_job, "interval", minutes=5)

    # 하루 2회 실행: 발표일 기반 지표
    scheduler.add_job(update_economy_job, "cron", hour=0, minute=0)
    scheduler.add_job(update_economy_job, "cron", hour=12, minute=0)

    scheduler.start()

@app.get("/api/timer")
def api_timer():
    if not LAST_UPDATE["stocks"] or not NEXT_UPDATE["stocks"]:
        return {"last_update": None, "next_update": None}

    return {
        "last_update": int(LAST_UPDATE["stocks"].timestamp() * 1000),
        "next_update": int(NEXT_UPDATE["stocks"].timestamp() * 1000)
    }


# Serve Static Files (Frontend)
try:
    # Go up one level from 'backend' to 'USA Invest'
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
except Exception as e:
    print(f"Failed to mount static files: {e}")

if __name__ == "__main__":
    # Run on localhost:8000
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
