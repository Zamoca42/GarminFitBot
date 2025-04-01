# Garmin Fit Bot Backend

## 아키텍쳐

![](https://mermaid.ink/svg/pako:eNqFVm1r01AU_ivhijAhG31J3_JBqJ0VQUGdn0xl3LW3bVialJtUnWOwuaAiyBREN1lFYWwq-zDmJhX8RU36Hzw3N0lvWruVQu495znPec6556ZdR3WrQZCKmob1tN7G1JEe3qiZEnzs3kqL4m5bqqHR1pnX_-v3z_yPg9GbQQ1xBPv0bEI1_8Wx__mH_-Xd47FjFa9iS_P_nLHv7sHo5TfJO3sVAojZ4IupVOV7t6XhL9cfnItZcFfXqth2mNd3971TV8iEe05b8_sD_7AvAWBSwzILjnVMIBrYwQHAe3sC9Y3ckwmAg-3VADDa3vffHIy2jgXA7DKYyD8uBPyvGNC7DG17otdJpDvGT2qLcGN9_4M61ioxY-zo5dfR1jRwtlqAeTt7wwHEnO56h8ei2joxCF3TKsFDSFm3DIPUHYuK0l7v-kfvpbhV4iGZ2Fh7DrNSvi15v13f7U_BLhgKOPVPH_wjN9HGFjEd7Q42W5U21k2pzPaJnliGrYW5vB13eH55onEp08fWWNHm7lm206Jk6f6da0ImShq6rc09YA_R3oGrxSTEpN7P797bweXDszfwfm-Oz09U0cK0o5vareAhVSzThEOYPZJXr0LnToanJ3zLbqs0P3-d3wxuC5aBEcZcjIUtN8O8Ji3xvUqao8uUtEY3KEENlDF3NLfcFZGMGRPuiC1w89mcJI4CeHbxZoQUoikA8aaKPJyZJ4kGfcoTzXToiHAzlEdoHsqGNSGcGULFMLeRUljOoBO6JZbCZ25GM0QnX3PylWRpC2ALZjrRkUR50x1jkwa3eXvT7_8NIwxs24ukKXWp3sFA3NQNQ72Svlks3szJwGdR9Wlbd8gE3CZ1y2yMA6rVUjGVuigAVEH_QrhSKVdzF8HJM4dQOIyIXlGy2fw0XohisyyH3QmLSXjZ2clit-XEucQFiUGNFTnocaRe9PHuxkKRjDqEdrDegB_qdQasIadNOqSGVFiapOdQbLC3xAZAQYe1tGbWkerQHpERtXqtNlKb2LBh1-uCNLKoY3jZdCJIF5uPLCvegizQdJf_MQj-HwQQpK6jZ0hN53IL2UJRyWcz6VQmW1BktIbUbHohk8sUU7mMUirlU-nShoyeB5yphWJRKeXzhWw6VUgrhUxGRi3Kagn1wSuL0IrVMx2kljb-Afk1EIY)

[Mermaid 에디터에서 다이어그램 보기](https://mermaid.live/edit#pako:eNqFVm1r01AU_ivhijAhG31J3_JBqJ0VQUGdn0xl3LW3bVialJtUnWOwuaAiyBREN1lFYWwq-zDmJhX8RU36Hzw3N0lvWruVQu495znPec6556ZdR3WrQZCKmob1tN7G1JEe3qiZEnzs3kqL4m5bqqHR1pnX_-v3z_yPg9GbQQ1xBPv0bEI1_8Wx__mH_-Xd47FjFa9iS_P_nLHv7sHo5TfJO3sVAojZ4IupVOV7t6XhL9cfnItZcFfXqth2mNd3971TV8iEe05b8_sD_7AvAWBSwzILjnVMIBrYwQHAe3sC9Y3ckwmAg-3VADDa3vffHIy2jgXA7DKYyD8uBPyvGNC7DG17otdJpDvGT2qLcGN9_4M61ioxY-zo5dfR1jRwtlqAeTt7wwHEnO56h8ei2joxCF3TKsFDSFm3DIPUHYuK0l7v-kfvpbhV4iGZ2Fh7DrNSvi15v13f7U_BLhgKOPVPH_wjN9HGFjEd7Q42W5U21k2pzPaJnliGrYW5vB13eH55onEp08fWWNHm7lm206Jk6f6da0ImShq6rc09YA_R3oGrxSTEpN7P797bweXDszfwfm-Oz09U0cK0o5vareAhVSzThEOYPZJXr0LnToanJ3zLbqs0P3-d3wxuC5aBEcZcjIUtN8O8Ji3xvUqao8uUtEY3KEENlDF3NLfcFZGMGRPuiC1w89mcJI4CeHbxZoQUoikA8aaKPJyZJ4kGfcoTzXToiHAzlEdoHsqGNSGcGULFMLeRUljOoBO6JZbCZ25GM0QnX3PylWRpC2ALZjrRkUR50x1jkwa3eXvT7_8NIwxs24ukKXWp3sFA3NQNQ72Svlks3szJwGdR9Wlbd8gE3CZ1y2yMA6rVUjGVuigAVEH_QrhSKVdzF8HJM4dQOIyIXlGy2fw0XohisyyH3QmLSXjZ2clit-XEucQFiUGNFTnocaRe9PHuxkKRjDqEdrDegB_qdQasIadNOqSGVFiapOdQbLC3xAZAQYe1tGbWkerQHpERtXqtNlKb2LBh1-uCNLKoY3jZdCJIF5uPLCvegizQdJf_MQj-HwQQpK6jZ0hN53IL2UJRyWcz6VQmW1BktIbUbHohk8sUU7mMUirlU-nShoyeB5yphWJRKeXzhWw6VUgrhUxGRi3Kagn1wSuL0IrVMx2kljb-Afk1EIY)

## 애플리케이션 구조

본 애플리케이션은 FastAPI 서버로 구성되어 있으며, 로컬 개발 환경과 배포 환경이 분리되어 있습니다.

- `docker-compose.local.yml`: 로컬 개발 환경용 (Redis 포함)
- `docker-compose.yml`: 배포 환경용 (Prometheus, Node Exporter 포함)

## 로컬 개발 환경 설정

```bash
# 개발 환경 시작
docker-compose -f docker-compose.local.yml up -d
```

## 배포 구조

시스템은 AWS의 여러 서비스를 활용하여 배포됩니다:

1. **API 서버**: AWS EC2에서 FastAPI 애플리케이션 실행
2. **Redis**: Upstash Redis 사용
3. **모니터링**: Prometheus + Node Exporter

### API 서버 배포

GitHub Actions 워크플로우 `.github/workflows/deploy-fastapi-ec2.yml`을 통해 자동으로 배포됩니다.

특징:

- 시스템 재부팅 시 자동 시작 (systemd 서비스 등록)
- Docker Compose 컨테이너 restart always 설정
- Prometheus + Node Exporter를 통한 모니터링

## 도커 명령어

```bash
# 로컬 개발 환경
docker-compose -f docker-compose.local.yml up -d
docker-compose -f docker-compose.local.yml down

# 배포 환경
docker-compose --profile production up -d
docker-compose --profile production down
```

## 모니터링

### Prometheus + Node Exporter

- Prometheus: `http://your-domain:9090`
- Node Exporter: `http://your-domain:9100`

## 개발 환경 설정

1. Python 3.11+ 설치
2. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 설치

```bash
pip install -r requirements.txt
```

4. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일 수정
```

5. 서버 실행

```bash
uvicorn main:app --reload
```
