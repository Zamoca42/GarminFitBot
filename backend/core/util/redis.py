import logging
from datetime import timedelta

import redis.asyncio as redis

from core.config import DEFAULT_DEDUP_TTL, RESULT_BACKEND
from core.util.task_id import generate_redis_dedup_key

logger = logging.getLogger(__name__)

redis_client = redis.Redis.from_url(RESULT_BACKEND, decode_responses=True)


async def is_duplicate_request(task_id: str, ttl: int = DEFAULT_DEDUP_TTL) -> bool:
    """
    Redis를 사용하여 중복 요청 여부를 체크하고, 중복이 아니라면 TTL과 함께 키를 저장합니다.

    Args:
        redis_client: Redis 비동기 클라이언트
        dedup_key: 중복 확인용 Redis 키
        ttl: 키의 생존 시간(초), 기본 5분

    Returns:
        bool: 이미 요청이 있었다면 True (중복), 아니라면 False
    """
    dedup_key = generate_redis_dedup_key(task_id)
    was_set = await redis_client.set(dedup_key, "1", ex=ttl, nx=True)
    return not was_set


def format_remaining_time(seconds: int) -> str:
    """남은 초를 'X시간 Y분' 또는 'Y분 Z초' 등으로 변환"""
    if seconds < 0:
        return "잠시 후"
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds_rem = divmod(remainder, 60)

    if hours > 0:
        if minutes > 0:
            return f"약 {hours}시간 {minutes}분"
        else:
            return f"약 {hours}시간"
    elif minutes > 0:
        return f"약 {minutes}분"
    else:
        return f"약 {seconds_rem}초"


async def get_task_result_ttl(celery_task_id: str) -> int:
    """Celery 작업 결과 키의 남은 TTL을 Redis에서 조회합니다."""
    result_key = f"celery-task-meta-{celery_task_id}"
    try:
        ttl = await redis_client.ttl(result_key)
        # ttl: 남은 시간(초), -1: 만료 시간 없음, -2: 키 없음 (만료됨)
        return ttl
    except Exception as e:
        logger.error(f"Redis TTL 조회 오류 for key {result_key}: {e}")
        return -2
