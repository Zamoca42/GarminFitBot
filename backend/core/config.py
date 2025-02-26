import logging
import os

from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경변수 가져오기
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# 데이터베이스 설정
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "garmin_db")

# 데이터베이스 풀 설정
POOL_SIZE = int(os.getenv("POOL_SIZE", "5"))
MAX_OVERFLOW = int(os.getenv("MAX_OVERFLOW", "10"))
POOL_TIMEOUT = int(os.getenv("POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("POOL_RECYCLE", "1800"))

# 기존 비동기 URL
DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/"
    f"{DB_NAME}"
)

# 마이그레이션용 동기 URL 추가
SYNC_DATABASE_URL = (
    f"postgresql://" f"{DB_USER}:{DB_PASSWORD}@" f"{DB_HOST}:{DB_PORT}/" f"{DB_NAME}"
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # 콘솔 출력
        logging.FileHandler("garmin_api.log"),  # 파일 출력
    ],
)
