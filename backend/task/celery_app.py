from celery import Celery
from celery.schedules import crontab

from core.config import BROKER_URL, RESULT_BACKEND

# Celery 앱 생성
celery_app = Celery(
    "garmin_fit_bot",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["task.garmin_collector", "task.partition_manager"]
)

# Celery 설정
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=False,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
    # RabbitMQ 관련 추가 설정
    broker_connection_timeout=30,
    broker_pool_limit=10,
)

# 주기적 작업 스케줄 설정
celery_app.conf.beat_schedule = {
    # 매일 새벽 3시에 전날 데이터 수집
    "collect_yesterday_data": {
        "task": "collect_garmin_data",
        "schedule": crontab(hour=3, minute=0),
        "args": (1,),  # 1일 전 데이터
    },
    # 매일 오전 9시에 당일 데이터 수집
    "collect_today_data": {
        "task": "collect_garmin_data",
        "schedule": crontab(hour=9, minute=0),
        "args": (0,),  # 오늘 데이터
    },
    # 매일 오후 6시에 당일 데이터 다시 수집 (업데이트)
    "update_today_data": {
        "task": "collect_garmin_data",
        "schedule": crontab(hour=18, minute=0),
        "args": (0,),  # 오늘 데이터
    },
    # 매월 20일 오전 2시에 파티션 관리
    "manage_partitions": {
        "task": "manage_partitions",
        "schedule": crontab(day_of_month=20, hour=2, minute=0),
    },
}

if __name__ == "__main__":
    celery_app.start() 