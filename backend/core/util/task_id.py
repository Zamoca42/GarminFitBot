import hashlib

from task import analysis_health_query


def get_query_hash(query: str, length: int = 8) -> str:
    return hashlib.md5(query.strip().lower().encode("utf-8")).hexdigest()[:length]


def generate_task_id(
    user_id: str,
    date: str,
    task_name: str,
    user_analysis_intent: str,
    query: str = "",
) -> str:
    base = f"{user_id}_{date}_{task_name}"
    if task_name == analysis_health_query.name and query:
        query_hash = get_query_hash(query)
        return f"{base}_{user_analysis_intent}_{query_hash}"
    return base


def generate_redis_dedup_key(task_id: str) -> str:
    return f"dedup:{task_id}"


def generate_celery_task_id(task_id: str) -> str:
    return f"task:{task_id}"


def task_id_to_path(task_id: str) -> str:
    """
    task_id를 URL 경로 문자열로 변환

    예: "kakao_123_2025-03-20_health-analysis_sleep_3a5e7d2f"
    → "kakao_123/2025-03-20/health-analysis/sleep/3a5e7d2f"
    """
    parts = task_id.split("_")
    if len(parts) < 3:
        raise ValueError("Invalid task_id format")

    return "/".join(parts)
