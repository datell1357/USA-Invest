# 미국 주식 & 경제 지표 대시보드 (USA Invest Dashboard)

미국 및 글로벌 주요 경제 지표, 주식, 채권 금리, 환율 정보를 실시간 및 일간 단위로 제공하는 웹 대시보드입니다.

## 📌 주요 기능

### 1. 실시간/일간 시장 데이터

- **주요 지수**: S&P 500, Dow Jones, Nasdaq 100 선물, Russell 2000
- **원자재 & 변동성**: WTI 원유, VIX 지수
- **심리 지수**: Fear & Greed Index

### 2. 채권 금리 및 스프레드

- **미국 국채**: 10년물, 2년물 금리
- **장단기 금리차 (10Y-2Y Spread)**: **FRED API**를 연동하여 정밀한 데이터 및 변동 추이 제공
- **글로벌 국채**: 한국 10년/2년물, 일본 2년물

### 3. 환율 및 유동성

- **환율**: USD/KRW, 달러 인덱스 (DXY)
- **기타**: 한국 외환보유고, 외국인 국채 보유량

### 4. 경제 지표 (Daily)

- 소비자 신뢰지수 (CCI)
- 실업률 (Unemployment Rate)
- 비농업 고용지수 (Non-Farm Payrolls)
- 제조업 구매관리자지수 (PMI)
- 기준 금리 (Fed, 한국은행, BOJ)

### 5. 차트 시각화

- 주요 지표에 대한 1년치 역사적 데이터를 라인 차트로 시각화
- 모바일 및 데스크탑 반응형 디자인

## 🛠 기술 스택

- **Backend**: Python, FastAPI
- **Frontend**: HTML5, JavaScript (Vanilla), TailwindCSS (CDN)
- **Data Source**:
  - Investing.com Crawling
  - FRED API (Federal Reserve Economic Data)
  - Yahoo Finance (yfinance)
  - IndexerGo, NY Fed API

## 🚀 설치 및 실행

1. **저장소 클론**

   ```bash
   git clone [repository_url]
   cd "USA Invest"
   ```

2. **가상환경 설정 (권장)**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **의존성 설치**

   ```bash
   pip install -r backend/requirements.txt
   ```

4. **환경 변수 설정**
   루트 경로에 `.env` 파일을 생성하고 다음 내용을 추가하세요.

   ```ini
   FRED_API_KEY=your_fred_api_key_here
   ```

5. **서버 실행**

   ```bash
   python backend/main.py
   # 또는
   # uvicorn backend.main:app --reload
   ```

6. **접속**
   브라우저에서 `http://localhost:8000` 접속

## ⚠️ 주의사항

- 이 프로젝트는 학습 및 개인 사용 목적으로 제작되었으며, 크롤링 대상 사이트의 정책에 따라 데이터 수집이 제한될 수 있습니다.
- 상업적 용도로 사용 시 각 데이터 제공자의 사용 약관을 확인하시기 바랍니다.
