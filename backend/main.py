from fastapi import FastAPI
from fastapi import Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import finance_service

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/")
def read_root():
    return {"status": "USA Invest 백엔드 시스템이 정상 작동 중입니다."}

@app.get("/api/finance/stocks")
def get_stocks():
    return finance_service.get_stocks_data()

@app.get("/api/finance/economy")
def get_economy():
    return finance_service.get_economy_data()

@app.get("/api/finance/rates")
def get_rates():
    return finance_service.get_rates_data()

@app.get("/api/finance/exchange")
def get_exchange():
    return finance_service.get_exchange_data()

if __name__ == "__main__":
    # Run on localhost:8000
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
