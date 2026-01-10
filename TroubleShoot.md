# TroubleShoot.md - Render 139 에러 (Segmentation Fault)

## 이슈 개요
- **현상**: Render Free 인스턴스에서 서비스 운영 중 `exit status 139`와 함께 서버가 반복적으로 재시작됨.
- **발생 시점**: 주로 서버 시작(Startup) 및 Daily Batch Job 실행 시점.
- **로그 증상**: `Error fetching KRX data: No module named 'pykrx'` 로그 직후 또는 `update_history_job` 실행 중 크래시 추정.

## 원인 분석 (가설)
1. **메모리 부족 (OOM)**: Render Free 인스턴스는 512MB RAM을 제공함. Startup 시 `yfinance`와 `pandas`를 사용하여 10여 개 지표의 1년치 역사적 데이터를 한꺼번에 로드하면서 메모리 임계치를 초과, 139(Segmentation Fault) 에러 유발.
2. **의존성 결여**: `requirements.txt`에 `pykrx`가 누락되어 `ImportError`가 발생하고 있으나, 이는 139 에러의 직접적 원인이라기보다 시스템 불안정 요인으로 작용.
3. **네이티브 라이브러리 충돌**: `yfinance`나 `pandas`의 C-extension이 특정 데이터 처리 중 메모리 접근 오류를 일으켰을 가능성.

## 이슈 2: 하이일드 및 외국인보유채권 데이터 누락
- **현상**: 대시보드에서 '하이일드 스프레드'와 '외국인 주식보유' 항목이 `...`으로 표시됨.
- **로그 증상**:
    - `[Crawler] Failed to fetch HighYield: Status 403`
    - `Error fetching KRX data: No module named 'pkg_resources'`

## 원인 분석 (이슈 2)
1. **IndexerGo 403 에러**: 접속 시도 시 보안 필터링에 의해 크롤링이 차단됨. 일반적인 브라우저 헤더 정보가 부족하여 발생.
2. **pykrx pkg_resources 에러**: `pykrx` 라이브러리가 내부적으로 사용하는 `pkg_resources`가 최신 Python 환경(setuptools 미설치)에서 누락되어 발생.

## 조치 사항 (이슈 2)
1. **헤더 보완**: `crawler_service.py`의 `fetch_indexergo_data` 함수에 `Referer`, `Accept` 등 표준 헤더를 대거 추가하여 우회.
2. **의존성 추가**: `requirements.txt`에 `setuptools`를 명시적으로 추가하여 `pkg_resources` 누락 문제 해결.

## 조치 결과
1. **의존성 해결**: `backend/requirements.txt`에 `pykrx` 추가 완료.
2. **Startup Job 부하 분산**: `main.py`의 `run_startup_jobs`에서 각 태스크 사이에 `time.sleep(2)` 추가.
3. **History Job 최적화**: `get_all_history_data`를 순차 처리 방식(`for` loop + `time.sleep(1)`)으로 변경하여 메모리 정점 부하를 80% 이상 감소(추정) 시킴.
4. **로깅 강화**: 작업 단계별 시작/성공 여부 로그 추가로 문제 발생 시 추적 용이성 확보.
5. **결과**: 메모리 부족에 의한 SEGFAULT 가능성을 최소화하였으며, 서비스 안정성 향상 기대.

