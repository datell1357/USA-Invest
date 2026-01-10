# RUNNING.md - Execution Guide

## 1. 실행 개요
본 프로젝트는 Python FastAPI 기반의 백엔드와 Vanilla JS 기반의 프런트엔드로 구성되어 있습니다. 로컬 개발 환경 및 Docker를 통한 실행 방법을 제공합니다.

## 2. 필수 프로그램
- Python 3.10 이상
- pip (Python 패키지 관리자)
- Docker (선택 사항)

## 3. 환경 변수 설정
루트 디렉토리에 `.env` 파일을 생성하고 아래 내용을 설정합니다.
```ini
FRED_API_KEY=your_fred_api_key_here
```

## 4. 실행 방법 (로컬)
1. **의존성 설치**
   ```bash
   pip install -r backend/requirements.txt
   ```
2. **서버 실행**
   ```bash
   python backend/main.py
   ```
3. **접속**
   브라우저에서 `http://localhost:8000` 접속

## 5. Docker 실행
1. **이미지 빌드**
   ```bash
   docker build -t usa-invest .
   ```
2. **컨테이너 실행**
   ```bash
   docker run -d -p 8000:8000 --env-file .env usa-invest
   ```

## 6. 정상 동작 확인
- 서버 시작 후 로그에 `[Startup] Initial data fetch completed`가 표시되는지 확인합니다.
- `http://localhost:8000/health` 접속 시 `{"status": "ok"}` 응답이 오는지 확인합니다.

## 7. 테스트 실행
- 현재 단위 테스트는 제공되지 않으며, 서버 실행 후 API 엔드포인트(`http://localhost:8000/api/finance/stocks` 등)를 통해 데이터를 검증합니다.

## 8. 자주 발생하는 오류
- **139 (Segmentation Fault)**: Render와 같은 제한된 메모리 환경에서 발생할 수 있습니다. 이미 최적화가 적용되어 있으나, 발생 시 `finance_service.py` 내의 History 수집 지연 시간을 더 늘려보십시오.
- **ImportError (pykrx)**: `pip install pykrx`가 누락된 경우 발생합니다. 최신 `requirements.txt`를 사용하여 재설치하십시오.
