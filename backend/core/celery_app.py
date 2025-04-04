import logging
import os

import redis
from celery import Celery, signals

from core.config import (
    BROKER_URL,
    RESULT_BACKEND,
)

logger = logging.getLogger(__name__)

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "log")
os.makedirs(LOG_DIR, exist_ok=True)

CELERY_LOG_FILE = os.path.join(LOG_DIR, f"celery.log")

sync_redis_client = redis.Redis.from_url(RESULT_BACKEND, decode_responses=True)

# Celery 앱 생성
celery_app = Celery(
    "garmin_fit_bot",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["task.agent_task", "task.garmin_collector"],
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


@signals.after_setup_logger.connect
@signals.after_setup_task_logger.connect
def setup_logger(logger, *args, **kwargs):
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler = logging.FileHandler(CELERY_LOG_FILE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)


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


@signals.task_failure.connect
def task_failure_handler(
    task_id=None, exception=None, traceback=None, einfo=None, *args, **kwargs
):
    logger.error(f"Task failed: {task_id}, error: {exception}")
    if traceback:
        logger.error(f"Detailed error: {traceback}")
