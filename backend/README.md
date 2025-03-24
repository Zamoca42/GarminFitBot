# Garmin Fit Bot Backend

## 애플리케이션 구조

본 애플리케이션은 FastAPI와 Celery 서비스로 구성되어 있으며, 서로 다른 서버에 배포할 수 있도록 도커 컴포즈 파일이 분리되어 있습니다.

- `docker-compose.yml`: FastAPI 서버 및 Redis (API 서버 전용)
- `docker-compose.celery.yml`: Celery worker, beat, flower 및 Redis (Celery 워커 전용)

## 로컬 개발 환경 설정

```bash
# 개발 환경 시작
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Celery 작업 실행 방법

### 필요 조건

- RabbitMQ 서버 연결 (메시지 브로커로 사용)
  - 로컬 RabbitMQ 또는 CloudAMQP와 같은 클라우드 서비스
- Python 환경 설정 완료

### 환경 변수 설정

`.env` 파일에 RabbitMQ 연결 정보 설정:

```
BROKER_URL=amqps://username:password@hostname/vhost
RESULT_BACKEND=rpc://
```

### Celery 작업자 실행

```bash
# Celery 작업자 실행
python run_celery.py worker

# Celery 스케줄러 실행 (주기적 작업)
python run_celery.py beat

# Celery 모니터링 도구 실행 (선택사항)
python run_celery.py flower
```

### 수동으로 작업 실행

```bash
# 오늘 데이터 수집
python run_celery.py collect 0

# 어제 데이터 수집
python run_celery.py collect 1

# 파티션 관리 작업 실행
python run_celery.py partition
```

## 배포 구조

시스템은 두 개의 서버로 분리되어 배포됩니다:

1. **API 서버**: FastAPI 애플리케이션 실행
2. **Celery 서버**: Celery 작업자, 스케줄러, Flower 대시보드 실행

### API 서버 배포

GitHub Actions 워크플로우 `.github/workflows/deploy-fastapi.yml`을 통해 자동으로 배포됩니다.

### Celery 서버 배포 (GCP VM)

GitHub Actions 워크플로우 `.github/workflows/deploy-celery-gcp.yml`을 통해 GCP VM에 자동으로 배포됩니다.

특징:

- 시스템 재부팅 시 자동 시작 (systemd 서비스 등록)
- Docker Compose 컨테이너 restart always 설정

## 도커 명령어

```bash
# FastAPI 서버 시작
docker-compose -f docker-compose.fastapi.yml up -d

# Celery 서비스 시작
docker-compose -f docker-compose.celery.yml up -d

# 서비스 상태 확인
docker-compose -f docker-compose.fastapi.yml ps
docker-compose -f docker-compose.celery.yml ps

# 서비스 중지
docker-compose -f docker-compose.fastapi.yml down
docker-compose -f docker-compose.celery.yml down
```

## 주기적 작업 일정

- 매일 새벽 3시: 전날 데이터 수집
- 매일 오전 9시: 당일 데이터 수집
- 매일 오후 6시: 당일 데이터 업데이트
- 매월 20일 오전 2시: 데이터베이스 파티션 관리

## 클라우드 RabbitMQ 설정

### CloudAMQP 사용하기

1. [CloudAMQP](https://www.cloudamqp.com/)에서 계정 생성
2. 새 인스턴스 생성 (무료 또는 유료 플랜)
3. 인스턴스 생성 후 AMQP URL 복사
4. `.env` 파일에 BROKER_URL 설정

### 다른 클라우드 RabbitMQ 서비스

- AWS의 Amazon MQ
- Azure의 Service Bus
- Google Cloud의 Pub/Sub + RabbitMQ 어댑터

## 개발 환경 설정

(기존 내용 유지)
