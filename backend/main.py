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

from fastapi.staticfiles import StaticFiles
import os

# Mount the parent directory to serve index.html
# Careful not to expose sensitive files if meaningful, but for this demo it's fine.
# We mount it at the root.
# Note: Put this AFTER API routes so API takes precedence, OR use a specific path.
# Actually, for 'html=True' at root, it acts as a catch-all.
# Better to explicit API routes first.

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
