import logging

import redis
from celery import Celery, signals
from celery.schedules import crontab

from core.config import (
    BROKER_URL,
    RESULT_BACKEND,
)

logger = logging.getLogger(__name__)

sync_redis_client = redis.Redis.from_url(RESULT_BACKEND, decode_responses=True)

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
    task_track_started=True,
)

# 주기적 작업 스케줄 설정
celery_app.conf.beat_schedule = {
    "manage_partitions": {
        "task": "manage_partitions",
        "schedule": crontab(day_of_month=20, hour=2, minute=0),
    },
}


@signals.task_prerun.connect
def on_task_start(*args, **kwargs):
    try:
        sync_redis_client.incr("celery:active_tasks")
        logger.info("Task started, active tasks count increased")
    except Exception as e:
        logger.error(f"Error increasing active tasks count: {e}")


@signals.task_postrun.connect
def on_task_end(*args, **kwargs):
    try:
        sync_redis_client.decr("celery:active_tasks")
        logger.info("Task ended, active tasks count decreased")
    except Exception as e:
        logger.error(f"Error decreasing active tasks count: {e}")
