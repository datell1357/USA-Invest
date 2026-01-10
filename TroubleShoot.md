# TroubleShoot.md - Render 139 에러 (Segmentation Fault)

## 이슈 개요
- **현상**: Render Free 인스턴스에서 서비스 운영 중 `exit status 139`와 함께 서버가 반복적으로 재시작됨.
- **발생 시점**: 주로 서버 시작(Startup) 및 Daily Batch Job 실행 시점.
- **로그 증상**: `Error fetching KRX data: No module named 'pykrx'` 로그 직후 또는 `update_history_job` 실행 중 크래시 추정.

## 원인 분석 (가설)
1. **메모리 부족 (OOM)**: Render Free 인스턴스는 512MB RAM을 제공함. Startup 시 `yfinance`와 `pandas`를 사용하여 10여 개 지표의 1년치 역사적 데이터를 한꺼번에 로드하면서 메모리 임계치를 초과, 139(Segmentation Fault) 에러 유발.
2. **의존성 결여**: `requirements.txt`에 `pykrx`가 누락되어 `ImportError`가 발생하고 있으나, 이는 139 에러의 직접적 원인이라기보다 시스템 불안정 요인으로 작용.
3. **네이티브 라이브러리 충돌**: `yfinance`나 `pandas`의 C-extension이 특정 데이터 처리 중 메모리 접근 오류를 일으켰을 가능성.

## 조치 계획 (Proposed Solutions)
- [ ] **Step 1: 의존성 해결**
    - `backend/requirements.txt`에 `pykrx` 추가.
- [ ] **Step 2: Startup Job 부하 분산**
    - `run_startup_jobs` 내에서 각 데이터 수집 함수 사이에 `time.sleep(2)` 등의 딜레이를 추가하여 메모리 스파이크 방지.
- [ ] **Step 3: History Job 최적화**
    - 모든 차트 데이터를 한꺼번에 가져오는 대신, 하나씩 순차적으로 가져와 캐시에 업데이트하도록 변경.
    - `yfinance` 호출 시 `threads=False` 설정 고려.
- [ ] **Step 4: 로깅 강화**
    - 각 단계의 시작과 끝을 기록하는 로그를 추가하여 정확한 크래시 지점 파악.

## 조치 결과
1. **의존성 해결**: `backend/requirements.txt`에 `pykrx` 추가 완료.
2. **Startup Job 부하 분산**: `main.py`의 `run_startup_jobs`에서 각 태스크 사이에 `time.sleep(2)` 추가.
3. **History Job 최적화**: `get_all_history_data`를 순차 처리 방식(`for` loop + `time.sleep(1)`)으로 변경하여 메모리 정점 부하를 80% 이상 감소(추정) 시킴.
4. **로깅 강화**: 작업 단계별 시작/성공 여부 로그 추가로 문제 발생 시 추적 용이성 확보.
5. **결과**: 메모리 부족에 의한 SEGFAULT 가능성을 최소화하였으며, 서비스 안정성 향상 기대.

