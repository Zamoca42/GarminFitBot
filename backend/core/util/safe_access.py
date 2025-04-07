"""
안전한 데이터 접근을 위한 유틸리티 함수들

외부 API나 불확실한 데이터 소스에서 값을 안전하게 추출하는 데 사용되는
헬퍼 함수들을 제공합니다.
"""

import logging
from typing import Any, Dict, List, Optional, TypeVar, cast, overload

logger = logging.getLogger(__name__)

T = TypeVar("T")
K = TypeVar("K")


@overload
def safe_get(obj: Any, attr_name: str) -> Optional[T]:
    pass


@overload
def safe_get(obj: Any, attr_name: str, default: T) -> T:
    pass


def safe_get(obj: Any, attr_name: str, default: Any = None) -> Optional[T]:
    """안전하게 객체의 속성에 접근

    Args:
        obj: 속성을 가져올 객체
        attr_name: 가져올 속성의 이름
        default: 속성이 없거나 접근 실패 시 반환할 기본값

    Returns:
        속성 값 또는 기본값
    """
    if obj is None:
        return cast(Optional[T], default)
    try:
        return cast(T, getattr(obj, attr_name, default))
    except Exception as e:
        logger.info(f"속성 {attr_name} 접근 실패: {str(e)}")
        return cast(Optional[T], default)


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


@overload
def safe_get_item(obj: Any, key: K) -> Optional[T]:
    pass


@overload
def safe_get_item(obj: Any, key: K, default: T) -> T:
    pass


def safe_get_item(obj: Any, key: Any, default: Any = None) -> Optional[T]:
    """안전하게 컨테이너의 아이템에 접근

    Args:
        obj: 아이템을 가져올 컨테이너 (딕셔너리, 리스트 등)
        key: 가져올 아이템의 키 또는 인덱스
        default: 아이템이 없거나 접근 실패 시 반환할 기본값

    Returns:
        아이템 또는 기본값
    """
    if obj is None:
        return cast(Optional[T], default)
    try:
        return cast(T, obj[key])
    except (KeyError, TypeError, IndexError):
        return cast(Optional[T], default)


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
