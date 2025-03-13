import logging
import os
from typing import List

from dotenv import load_dotenv

# .env 파일 로드
load_dotenv(".env", override=True)

# 데이터베이스 설정
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/garmin_db"
)
SYNC_DATABASE_URL = os.getenv(
    "SYNC_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/garmin_db"
)

# RabbitMQ 설정
BROKER_URL = os.getenv("BROKER_URL", "amqp://guest:guest@localhost:5672//")
RESULT_BACKEND = os.getenv("RESULT_BACKEND", "rpc://")

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
