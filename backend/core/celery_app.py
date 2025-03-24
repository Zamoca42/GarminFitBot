from celery import Celery
from celery.schedules import crontab

from core.config import (
    BROKER_URL,
    RESULT_BACKEND,
)

# Celery 앱 생성
celery_app = Celery(
    "garmin_fit_bot",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["task.agent_task", "task.garmin_collector", "task.partition_manager"],
    result_persistent=True,
)

# Celery 설정
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=False,
    worker_max_tasks_per_child=1,
    broker_connection_retry_on_startup=True,
    broker_connection_timeout=30,
    broker_pool_limit=10,
)

# 주기적 작업 스케줄 설정
celery_app.conf.beat_schedule = {
    "manage_partitions": {
        "task": "manage_partitions",
        "schedule": crontab(day_of_month=20, hour=2, minute=0),
    },
}
