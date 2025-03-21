import hashlib

from task import analysis_health_query


def classify_interest(query: str) -> str:
    query = query.lower()
    if "수면" in query or "잠" in query:
        return "sleep"
    elif "스트레스" in query:
        return "stress"
    elif "심박수" in query:
        return "heart-rate"
    elif "걸음" in query or "운동" in query or "활동" in query:
        return "activity"
    else:
        return "general"


def get_query_hash(query: str, length: int = 8) -> str:
    return hashlib.md5(query.strip().lower().encode("utf-8")).hexdigest()[:length]


def generate_task_id(user_id: str, date: str, task_name: str, query: str = "") -> str:
    base = f"{user_id}_{date}_{task_name}"
    if task_name == analysis_health_query.name and query:
        interest = classify_interest(query)
        query_hash = get_query_hash(query)
        return f"{base}_{interest}_{query_hash}"
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
