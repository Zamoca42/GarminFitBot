import redis.asyncio as redis

from core.config import BROKER_URL, DEFAULT_DEDUP_TTL
from core.util.task_id import generate_redis_dedup_key

redis_client = redis.Redis.from_url(BROKER_URL)


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
    return was_set is None  # 이미 존재하면 중복이므로 True
