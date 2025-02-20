from dotenv import load_dotenv
import os
import logging

# .env 파일 로드
load_dotenv()

# 환경변수 가져오기
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 콘솔 출력
        logging.FileHandler('garmin_api.log')  # 파일 출력
    ]
)