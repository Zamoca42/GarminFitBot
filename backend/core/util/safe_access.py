"""
안전한 데이터 접근을 위한 유틸리티 함수들

외부 API나 불확실한 데이터 소스에서 값을 안전하게 추출하는 데 사용되는
헬퍼 함수들을 제공합니다.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def safe_get(obj: Any, attr_name: str, default: Any = None) -> Any:
    """안전하게 객체의 속성에 접근

    Args:
        obj: 속성을 가져올 객체
        attr_name: 가져올 속성의 이름
        default: 속성이 없거나 접근 실패 시 반환할 기본값

    Returns:
        속성 값 또는 기본값
    """
    if obj is None:
        return default
    try:
        return getattr(obj, attr_name, default)
    except Exception as e:
        logger.debug(f"속성 {attr_name} 접근 실패: {str(e)}")
        return default


def safe_call(obj: Any, method_name: str, *args, default: Any = None, **kwargs) -> Any:
    """안전하게 객체의 메서드 호출

    Args:
        obj: 메서드를 호출할 객체
        method_name: 호출할 메서드 이름
        default: 메서드 호출 실패 시 반환할 기본값
        args, kwargs: 메서드에 전달할 인자들

    Returns:
        메서드 호출 결과 또는 기본값
    """
    if obj is None:
        return default
    method = getattr(obj, method_name, None)
    if callable(method):
        try:
            return method(*args, **kwargs)
        except Exception as e:
            logger.debug(f"{method_name} 메서드 호출 실패: {str(e)}")
            return default
    return default


def safe_int(value: Any, default: int = 0) -> int:
    """안전하게 정수로 변환

    Args:
        value: 변환할 값
        default: 변환 실패 시 반환할 기본값

    Returns:
        변환된 정수 또는 기본값
    """
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """안전하게 실수로 변환

    Args:
        value: 변환할 값
        default: 변환 실패 시 반환할 기본값

    Returns:
        변환된 실수 또는 기본값
    """
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_bool(value: Any, default: bool = False) -> bool:
    """안전하게 불리언으로 변환

    Args:
        value: 변환할 값
        default: 변환 실패 시 반환할 기본값

    Returns:
        변환된 불리언 또는 기본값
    """
    if value is None:
        return default
    try:
        return bool(value)
    except (ValueError, TypeError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """안전하게 문자열로 변환

    Args:
        value: 변환할 값
        default: 변환 실패 시 반환할 기본값

    Returns:
        변환된 문자열 또는 기본값
    """
    if value is None:
        return default
    try:
        return str(value)
    except (ValueError, TypeError):
        return default


def safe_list(value: Any, default: Optional[List] = None) -> List:
    """안전하게 리스트 반환

    Args:
        value: 변환할 값
        default: 변환 실패 시 반환할 기본값

    Returns:
        값을 리스트로 변환한 결과 또는 기본값
    """
    if default is None:
        default = []
    if value is None:
        return default
    if isinstance(value, list):
        return value
    try:
        return list(value)
    except (ValueError, TypeError):
        return default


def safe_dict(value: Any, default: Optional[Dict] = None) -> Dict:
    """안전하게 딕셔너리 반환

    Args:
        value: 변환할 값
        default: 변환 실패 시 반환할 기본값

    Returns:
        딕셔너리 또는 기본값
    """
    if default is None:
        default = {}
    if value is None:
        return default
    if isinstance(value, dict):
        return value
    return default


def safe_datetime(value: Any, default: Optional[datetime] = None) -> Optional[datetime]:
    """안전하게 datetime 객체 반환

    Args:
        value: 변환할 값 (타임스탬프(밀리초) 또는 ISO 형식 문자열)
        default: 변환 실패 시 반환할 기본값

    Returns:
        datetime 객체 또는 기본값
    """
    if value is None:
        return default
    if isinstance(value, datetime):
        return value
    try:
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value / 1000)
        elif isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError, OSError):
        pass
    return default


def safe_timedelta(
    seconds: Any, default: Optional[timedelta] = None
) -> Optional[timedelta]:
    """안전하게 timedelta 객체 반환

    Args:
        seconds: 초 단위 시간
        default: 변환 실패 시 반환할 기본값

    Returns:
        timedelta 객체 또는 기본값
    """
    if default is None:
        default = timedelta(seconds=0)
    if seconds is None:
        return default
    try:
        return timedelta(seconds=float(seconds))
    except (ValueError, TypeError):
        return default


def ensure_type(value: Any, expected_type: Type[T], default: T) -> T:
    """값이 기대하는 타입인지 확인하고, 아니면 기본값 반환

    Args:
        value: 확인할 값
        expected_type: 기대하는 타입
        default: 타입이 일치하지 않을 때 반환할 기본값

    Returns:
        값 또는 기본값
    """
    if isinstance(value, expected_type):
        return value
    return default


def safe_get_item(obj: Any, key: Any, default: Any = None) -> Any:
    """안전하게 컨테이너의 아이템에 접근

    Args:
        obj: 아이템을 가져올 컨테이너 (딕셔너리, 리스트 등)
        key: 가져올 아이템의 키 또는 인덱스
        default: 아이템이 없거나 접근 실패 시 반환할 기본값

    Returns:
        아이템 또는 기본값
    """
    if obj is None:
        return default
    try:
        return obj[key]
    except (KeyError, TypeError, IndexError):
        return default


def log_exception(
    action: str, error: Exception, context: Dict[str, Any] = None
) -> None:
    """예외 로깅 유틸리티

    Args:
        action: 수행 중이던 작업 설명
        error: 발생한 예외
        context: 추가 컨텍스트 정보
    """
    context_str = ", ".join(f"{k}={v}" for k, v in (context or {}).items())
    logger.error(f"{action} 중 오류 발생: {str(error)} [{context_str}]")
