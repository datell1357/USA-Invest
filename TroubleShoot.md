# TroubleShoot.md - Render 139 에러 (Segmentation Fault)

## 이슈 개요
- **현상**: Render Free 인스턴스에서 서비스 운영 중 `exit status 139`와 함께 서버가 반복적으로 재시작됨.
- **발생 시점**: 주로 서버 시작(Startup) 및 Daily Batch Job 실행 시점.
- **로그 증상**: `Error fetching KRX data: No module named 'pykrx'` 로그 직후 또는 `update_history_job` 실행 중 크래시 추정.

## 원인 분석 (가설)
1. **메모리 부족 (OOM)**: Render Free 인스턴스는 512MB RAM을 제공함. Startup 시 `yfinance`와 `pandas`를 사용하여 10여 개 지표의 1년치 역사적 데이터를 한꺼번에 로드하면서 메모리 임계치를 초과, 139(Segmentation Fault) 에러 유발.
2. **의존성 결여**: `requirements.txt`에 `pykrx`가 누락되어 `ImportError`가 발생하고 있으나, 이는 139 에러의 직접적 원인이라기보다 시스템 불안정 요인으로 작용.
3. **네이티브 라이브러리 충돌**: `yfinance`나 `pandas`의 C-extension이 특정 데이터 처리 중 메모리 접근 오류를 일으켰을 가능성.


## 이슈 3: 미국 기준금리(Fed Rate) 데이터 누락
- **현상**: 대시보드 내 '기준금리' 항목이 `...`으로 표시됨.
- **분석 및 재검증**: 
    - 사용자의 의견에 따라 Investing.com URL(`...-168`)을 브라우저로 재직접 확인한 결과, 페이지와 데이터 ID(`eventHistoryTable168`)는 모두 정상임을 확인했습니다.
    - 하지만 백엔드(Python)에서 접근 시 Cloudflare의 보안 차단(403) 또는 동적 렌더링 요소로 인해 데이터 수집이 안정적이지 못할 가능성이 큽니다.
- **조치 사항**: 
    - **크롤러 강화**: `fetch_investing_calendar_actual`의 헤더를 브라우저 수준으로 강화하고 타임아웃을 늘려 성공률을 높였습니다.
    - **하이브리드 전략**: Investing.com 크롤링을 우선 시도하되, 실패할 경우 자동으로 **FRED API**(`FEDFUNDS`)에서 데이터를 가져오도록 **폴백(Fallback) 로직**을 구현했습니다.


## 이슈 4: Render 배포 지연 ("Deploying..." 상태 지속)
- **현상**: 빌드 성공 후 배포 단계에서 상태 업데이트가 지연됨.
- **원인 분석**: Render Free 인스턴스는 배포 시 이전 인스턴스와 새로운 인스턴스의 교체 과정에서 헬스체크(`/health`) 성공을 기다림. 서버 시작 시 실행되는 `run_startup_jobs`가 비동기로 동작하지만, 초기 네트워크 부하 등으로 인해 헬스체크 응답이 아주 짧은 시간 지연될 수 있음.
- **조치 사항**: 이미 부하 분산(sleep 추가)을 적용하였으므로, 배포 시 약 1~2분 정도 충분히 대기하면 정상적으로 Live 상태로 전환됨을 확인.

## 조치 결과 (최종)
1. **메모리 최적화 (139 에러)**: Startup Job 딜레이 및 History 수집 순차화 완료.
2. **의존성 해결**: `pykrx`, `setuptools` 추가 완료.
3. **데이터 소스 안정화**: 
    - 하이일드 스프레드: IndexerGo 헤더 보완 완료.
    - 미국 기준금리: FRED API 방식으로 전환 완료.
4. **결과**: 주요 지표 데이터 누락 해결 및 인프라 안정성 확보.


