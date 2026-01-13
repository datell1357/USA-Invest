# USA-Invest 환경 변수 설정 가이드

본 프로젝트는 안정성과 보안을 위해 모든 민감한 설정값을 환경 변수(`.env`)로 관리합니다. Render 등 클라우드 배포 환경과 로컬 개발 환경 모두 아래 값을 설정해 주세요.

## 1. 필수 API 키
- `FRED_API_KEY`: FRED(Federal Reserve Economic Data) API 키. [무료 신청](https://fred.stlouisfed.org/docs/api/api_key.html)
    - *예시: 98f9a9461a5eed275514aad3fb514...*

## 2. 운영 모드 설정
- `PROD`: 서버 실행 모드를 결정합니다.
    - `true`: 운영 환경. `uvicorn reload` 비활성화, 메모리 최적화 작동.
    - `false` (기본값): 로컬 개발 환경. `reload` 활성화.

## 3. 데이터 원천 URL (수정 권장하지 않음)
특정 사이트의 주소가 변경되었을 때 코드 수정 없이 환경 변수만으로 대응이 가능합니다.

- `INVESTING_CCI_URL`: `https://kr.investing.com/economic-calendar/cb-consumer-confidence-48`
- `INVESTING_UNEMPLOYMENT_URL`: `https://kr.investing.com/economic-calendar/unemployment-rate-300`
- `INVESTING_NFP_URL`: `https://kr.investing.com/economic-calendar/nonfarm-payrolls-227`
- `INVESTING_PMI_URL`: `https://kr.investing.com/economic-calendar/ism-manufacturing-pmi-173`
- `INVESTING_FED_RATE_URL`: `https://kr.investing.com/economic-calendar/interest-rate-decision-168`
- `INDEXERGO_HIGH_YIELD_URL`: `https://www.indexergo.com/series/?frq=M&idxDetail=13404`
- `ENARA_FOREIGN_BOND_URL`: `https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1086`

## 4. 로컬 환경 적용 방법 (`.env` 파일)
프로젝트 루트 폴더에 `.env` 파일을 생성하고 아래 형식을 복사하여 입력하세요:

```env
PROD=false
FRED_API_KEY=your_actual_api_key_here

# URLs (필요시만 설정, 기본값 내장 지원 예정)
INVESTING_CCI_URL=https://kr.investing.com/economic-calendar/cb-consumer-confidence-48
INVESTING_UNEMPLOYMENT_URL=https://kr.investing.com/economic-calendar/unemployment-rate-300
INVESTING_NFP_URL=https://kr.investing.com/economic-calendar/nonfarm-payrolls-227
INVESTING_PMI_URL=https://kr.investing.com/economic-calendar/ism-manufacturing-pmi-173
INVESTING_FED_RATE_URL=https://kr.investing.com/economic-calendar/interest-rate-decision-168
INDEXERGO_HIGH_YIELD_URL=https://www.indexergo.com/series/?frq=M&idxDetail=13404
ENARA_FOREIGN_BOND_URL=https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1086
```
