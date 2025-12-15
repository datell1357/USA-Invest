# KRX Foreign Holding Crawler

## 개요

이 모듈은 한국거래소(KRX) 정보데이터시스템에서 전체 시장(KOSPI + KOSDAQ)의 외국인 보유 비중(시가총액 기준)을 수집합니다.

## 파일 경로

`backend/crawler/krx_crawler.py`

## 주요 기능

- **`get_foreign_holding_data()`**:
  - **입력**: 없음 (현재 날짜 기준 자동 탐색)
  - **로직**:
    1. `pykrx` 라이브러리를 사용하여 종목별 시가총액(`get_market_cap_by_ticker`)과 외국인 보유량(`get_exhaustion_rates...`)을 가져옵니다.
    2. 두 데이터를 병합하여 **전체 시장 시가총액**과 **외국인 보유 시가총액**을 계산합니다.
    3. `(외국인 보유 시가총액 / 전체 시가총액) * 100`으로 비중을 산출합니다.
    4. 휴장일이나 데이터 미제공일인 경우, 최대 7일 전까지 데이터를 역순으로 탐색합니다.
  - **출력**:
    ```python
    {
        "value": float,   # 외국인 보유 시가총액 (원화)
        "percent": str,   # 비중 (예: "31.82%")
        "date": str,      # 데이터 기준일 (YYYY-MM-DD)
        "total_cap": float # 전체 시가총액 (원화)
    }
    ```

## 의존성

- `pykrx`: KRX 데이터 스크래핑
- `pandas`: 데이터프레임 처리
