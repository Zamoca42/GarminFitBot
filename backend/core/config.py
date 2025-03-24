import logging
import os
from typing import List

from dotenv import load_dotenv
from kombu.utils.url import safequote

# .env 파일 로드
load_dotenv(".env", override=True)

# 데이터베이스 설정
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/garmin_db"
)
SYNC_DATABASE_URL = os.getenv(
    "SYNC_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/garmin_db"
)

# gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# langsmith
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "gramin-fit-bot")

aws_access_key = safequote(os.getenv("AWS_ACCESS_KEY"))
aws_secret_key = safequote(os.getenv("AWS_SECRET_KEY"))

SQS_BROKER_URL = "sqs://{aws_access_key}:{aws_secret_key}@".format(
    aws_access_key=aws_access_key,
    aws_secret_key=aws_secret_key,
)

# Celery 설정
BROKER_URL = os.getenv("BROKER_URL", "redis://redis:6379/0")
BROKER_TRANSPORT_OPTIONS = {
    "region": os.getenv("AWS_REGION", "ap-northeast-2"),
    "visibility_timeout": int(os.getenv("SQS_VISIBILITY_TIMEOUT", "3600")),
    "polling_interval": int(os.getenv("SQS_POLLING_INTERVAL", "1")),
    "predefined_queues": {
        "celery": {
            "url": "https://sqs.ap-northeast-2.amazonaws.com/571600833731/celery",
            "access_key_id": aws_access_key,
            "secret_access_key": aws_secret_key,
        }
    },
}
RESULT_BACKEND = os.getenv("RESULT_BACKEND", "rpc://")
DEFAULT_DEDUP_TTL = int(os.getenv("DEFAULT_DEDUP_TTL", "300"))

# JWT 설정
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# 카카오톡 설정
KAKAO_BOT_ID = os.getenv("KAKAO_BOT_ID", "1234567890")

# 데이터베이스 풀 설정
POOL_SIZE = int(os.getenv("POOL_SIZE", "5"))
MAX_OVERFLOW = int(os.getenv("MAX_OVERFLOW", "10"))
POOL_TIMEOUT = int(os.getenv("POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("POOL_RECYCLE", "1800"))

# 기타 설정
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# 프론트엔드 설정
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# CORS 설정
CORS_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://garmin-fit-bot.vercel.app",
    "https://fit-bot.click",
]

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # 콘솔 출력
        logging.FileHandler("garmin_api.log"),  # 파일 출력
    ],
)
