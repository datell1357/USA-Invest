# 데이터 수집 명세서 (Data Collection Specification)

본 문서는 대시보드에서 제공하는 모든 금융 및 경제 데이터의 수집 출처, 방법, 크롤링 대상 URL, 그리고 갱신 주기를 정의합니다.

## 1. 개요 및 범례

- **Source Type**:
  - `yfinance`: Yahoo Finance 라이브러리 (Ticker 기반)
  - `FRED API`: 미 연준 경제 데이터 API (Series ID 기반)
  - `Crawling`: 웹페이지 HTML 파싱 (BeautifulSoup)
  - `Library`: Python 전용 라이브러리 사용
- **Frequency**:
  - `Realtime (30s)`: 매 30초마다 갱신
  - `Realtime (5m)`: 매 5분마다 갱신
  - `Daily (2x)`: 매일 00:00, 12:00 (자정 및 정오) 2회 갱신

---

## 2. 항목별 데이터 수집 상세

### 2.1. 주요 지표 (Stocks & Indices)

| 항목 (ID)        | 항목명 (Description) | Source Type | URL / Ticker / ID                                                    | Frequency            | 비고            |
| :--------------- | :------------------- | :---------- | :------------------------------------------------------------------- | :------------------- | :-------------- |
| `sp_futures`     | S&P 500 Futures      | Crawling    | [Investing.com](https://kr.investing.com/indices/us-spx-500-futures) | Realtime (30s)       |                 |
| `dow_futures`    | Dow 30 Futures       | Crawling    | [Investing.com](https://kr.investing.com/indices/us-30-futures)      | Realtime (30s)       |                 |
| `nasdaq_futures` | Nasdaq 100 Futures   | Crawling    | [Investing.com](https://kr.investing.com/indices/nq-100-futures)     | Realtime (30s)       |                 |
| `russell`        | Russell 2000         | yfinance    | `^RUT`                                                               | Realtime (30s)       |                 |
| `wti`            | Crude Oil WTI        | Crawling    | [Investing.com](https://kr.investing.com/commodities/crude-oil)      | Realtime (30s)       |                 |
| `vix`            | VIX Index            | Crawling    | [Investing.com](https://kr.investing.com/indices/volatility-s-p-500) | Realtime (30s)       |                 |
| `fear_greed`     | Fear & Greed Index   | Library     | `fear_and_greed`                                                     | Realtime (30s)       | CNN 데이터 기반 |
| `high_yield`     | High Yield Spread    | Crawling    | [IndexerGo](https://www.indexergo.com/series/?frq=M&idxDetail=13404) | Daily (00:00, 12:00) |                 |

### 2.2. 금리 (Rates & Bonds)

| 항목 (ID)        | 항목명 (Description) | Source Type | URL / Ticker / ID                                                                                  | Frequency            | 비고           |
| :--------------- | :------------------- | :---------- | :------------------------------------------------------------------------------------------------- | :------------------- | :------------- |
| `us_10y`         | US 10Y Yield         | yfinance    | `^TNX`                                                                                             | Realtime (5m)        |                |
| `us_2y`          | US 2Y Yield          | Crawling    | [Investing.com](https://kr.investing.com/rates-bonds/u.s.-2-year-bond-yield)                       | Realtime (5m)        |                |
| `us_10_2_spread` | 10Y-2Y Spread        | Crawling    | [Investing.com](https://kr.investing.com/rates-bonds/10-2-year-treasury-yield-spread)              | Realtime (5m)        |                |
| `jp_2y`          | Japan 2Y Yield       | Crawling    | [Investing.com](https://kr.investing.com/rates-bonds/japan-2-year-bond-yield)                      | Realtime (5m)        |                |
| `kr_10y`         | Korea 10Y Yield      | Crawling    | [Investing.com](https://kr.investing.com/rates-bonds/south-korea-10-year-bond-yield)               | Realtime (5m)        |                |
| `kr_2y`          | Korea 2Y Yield       | Crawling    | [Investing.com](https://kr.investing.com/rates-bonds/south-korea-2-year-bond-yield)                | Realtime (5m)        |                |
| `fed_rate`       | US Fed Rate          | Crawling    | [Investing.com](https://kr.investing.com/economic-calendar/interest-rate-decision-168)             | Daily (00:00, 12:00) | Actual 값 사용 |
| `sofr`           | SOFR                 | API         | [NY Fed API](https://markets.newyorkfed.org/api/rates/secured/sofr/search.json)                    | Daily (00:00, 12:00) |                |
| `jp_policy`      | BOJ Policy Rate      | Crawling    | [Investing.com](https://kr.investing.com/economic-calendar/boj-interest-rate-decision-164)         | Daily (00:00, 12:00) | Actual 값 사용 |
| `kr_base`        | BOK Base Rate        | Crawling    | [Investing.com](https://kr.investing.com/economic-calendar/south-korea-interest-rate-decision-283) | Daily (00:00, 12:00) | Actual 값 사용 |

### 2.3. 환율 및 외환 (Exchange)

| 항목 (ID)          | 항목명 (Description) | Source Type | URL / Ticker / ID                                                                            | Frequency            | 비고                    |
| :----------------- | :------------------- | :---------- | :------------------------------------------------------------------------------------------- | :------------------- | :---------------------- |
| `dxy`              | US Dollar Index      | Crawling    | [Investing.com](https://kr.investing.com/currencies/us-dollar-index)                         | Realtime (5m)        |                         |
| `usd_krw`          | USD/KRW              | yfinance    | `KRW=X`                                                                                      | Realtime (5m)        |                         |
| `foreign_reserves` | KR FX Reserves       | Crawling    | [Investing.com](https://kr.investing.com/economic-calendar/south-korea-fx-reserves-usd-1889) | Daily (00:00, 12:00) |                         |
| `foreign_bond`     | 외국인 주식보유      | Crawling    | KRX 정보데이터시스템 (API-like)                                                              | Daily (00:00, 12:00) | `pykrx` 라이브러리 사용 |

### 2.4. 실물 경제 (Economy)

| 항목 (ID)      | 항목명 (Description)  | Source Type | URL / Ticker / ID                                                                     | Frequency            | 비고             |
| :------------- | :-------------------- | :---------- | :------------------------------------------------------------------------------------ | :------------------- | :--------------- |
| `cci`          | Consumer Confidence   | Crawling    | [Investing.com](https://kr.investing.com/economic-calendar/cb-consumer-confidence-48) | Daily (00:00, 12:00) | 다음 발표일 제공 |
| `unemployment` | Unemployment Rate     | Crawling    | [Investing.com](https://kr.investing.com/economic-calendar/unemployment-rate-300)     | Daily (00:00, 12:00) | 다음 발표일 제공 |
| `non_farm`     | Non-Farm Payrolls     | Crawling    | [Investing.com](https://kr.investing.com/economic-calendar/nonfarm-payrolls-227)      | Daily (00:00, 12:00) | 다음 발표일 제공 |
| `pmi`          | ISM Manufacturing PMI | Crawling    | [Investing.com](https://kr.investing.com/economic-calendar/ism-manufacturing-pmi-173) | Daily (00:00, 12:00) | 다음 발표일 제공 |

---

## 3. 스케줄링 설정 (`backend/main.py`)

- **Realtime (Stocks)**: `interval=30s` (매 30초마다 실행)
- **Realtime (Rates/Exchange)**: `interval=5m` (매 5분마다 실행)
- **Daily Jobs**: `cron` (매일 00:00, 12:00 실행)
  - `update_daily_stocks_job`
  - `update_daily_rates_job`
  - `update_daily_exchange_job`
  - `update_daily_economy_job`

> **Note**: 모든 데이터 수집 작업 시 타임아웃(Timeout) 설정과 예외 처리가 적용되어 있어, 특정 소스의 응답 지연이 전체 서비스 중단을 유발하지 않습니다.
