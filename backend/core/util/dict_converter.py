import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Set, Type, Union, get_type_hints

logger = logging.getLogger(__name__)


def camel_to_snake_case(text: str) -> str:
    """
    camelCase 또는 PascalCase 문자열을 snake_case로 변환합니다.
    HTTP, API와 같은 연속된 대문자도 올바르게 처리합니다.

    Args:
        text: 변환할 문자열

    Returns:
        snake_case로 변환된 문자열
    """
    # 특수 케이스 처리: HTTP, API 등 연속된 대문자 패턴을 먼저 처리
    result = text

    # 연속된 대문자가 단어의 끝이 아닌 경우 - 'HTTPResponse' -> 'HTTP_Response'
    result = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", result)

    # 소문자 다음에 대문자가 오는 경우 - 'getHTTP' -> 'get_HTTP'
    result = re.sub(r"([a-z])([A-Z])", r"\1_\2", result)

    # 모두 소문자로 변환 - 'get_HTTP' -> 'get_http'
    return result.lower()


def get_required_fields(cls: Type) -> Set[str]:
    """
    클래스의 필수 필드 목록을 반환합니다.

    Args:
        cls: 필드를 확인할 클래스

    Returns:
        필수 필드 이름 집합
    """
    try:
        annotations = get_type_hints(cls)
        required_fields = set()

        for field_name, field_type in annotations.items():
            is_optional = (
                hasattr(field_type, "__origin__")
                and field_type.__origin__ is Union
                and type(None) in field_type.__args__
            )

            has_default = False
            if hasattr(cls, "__dataclass_fields__"):
                if field_name in cls.__dataclass_fields__:
                    field_info = cls.__dataclass_fields__[field_name]
                    has_default = field_info.default is not field_info.default_factory
            else:
                has_default = (
                    hasattr(cls, field_name) and getattr(cls, field_name) is not None
                )

            if not is_optional and not has_default:
                required_fields.add(field_name)

        return required_fields
    except Exception as e:
        logger.warning(f"필수 필드 확인 중 오류 발생: {str(e)}")
        return set()


def set_default_values(
    data: Dict[str, Any], missing_fields: List[str], field_defaults: Dict[str, Any]
) -> Dict[str, Any]:
    """
    누락된 필드에 기본값을 설정합니다.

    Args:
        data: 원본 데이터 사전
        missing_fields: 누락된 필드 목록
        field_defaults: 필드별 기본값 사전

    Returns:
        기본값이 설정된 데이터 사전
    """
    for field in missing_fields:
        if field in field_defaults:
            data[field] = field_defaults[field]
    return data


def get_default_value_by_type(field_type: Type) -> Any:
    """
    필드 타입에 따라 적절한 기본값을 반환합니다.

    Args:
        field_type: 필드의 타입

    Returns:
        타입에 맞는 기본값
    """
    # Optional 타입인 경우 내부 타입 추출
    if hasattr(field_type, "__origin__") and field_type.__origin__ is Union:
        for arg in field_type.__args__:
            if arg is not type(None):
                field_type = arg
                break

    # 기본 타입에 따른 기본값 설정
    if field_type is int:
        return 0
    elif field_type is float:
        return 0.0
    elif field_type is str:
        return ""
    elif field_type is bool:
        return False
    elif field_type is list or field_type is List:
        return []
    elif field_type is dict or field_type is Dict:
        return {}
    elif field_type is datetime:
        return datetime.now()
    # 기타 복잡한 타입(클래스)의 경우 None 반환
    else:
        return None


def camel_to_snake_dict_safe(
    data: Dict[str, Any], cls=None, field_defaults: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    camelCase 형식의 키를 snake_case 형식으로 안전하게 변환하고,
    필요한 경우 누락된 필수 필드에 기본값을 설정합니다.

    Args:
        data: 변환할 데이터 딕셔너리
        cls: 필수 필드와 기본값을 결정하는 데 사용할 모델 클래스
        field_defaults: 필드별 기본값 사전

    Returns:
        snake_case 키와 기본값이 설정된 딕셔너리
    """
    result = {}
    if not data or not isinstance(data, dict):
        # 빈 데이터인 경우 모든 필수 필드에 기본값 설정
        if cls is not None and field_defaults:
            required_fields = get_required_fields(cls)
            for field in required_fields:
                if field in field_defaults:
                    result[field] = field_defaults[field]
        return result

    for key, value in data.items():
        try:
            if isinstance(key, str):
                snake_key = camel_to_snake_case(key)
            else:
                snake_key = key

            if isinstance(value, dict):
                result[snake_key] = camel_to_snake_dict_safe(value)
            elif isinstance(value, list):
                new_list = []
                for item in value:
                    if isinstance(item, dict):
                        new_list.append(camel_to_snake_dict_safe(item))
                    else:
                        new_list.append(item)
                result[snake_key] = new_list
            else:
                result[snake_key] = value
        except Exception as e:
            logger.warning(f"키 '{key}' 변환 중 오류 발생: {str(e)}")
            if hasattr(key, "__hash__") and key is not None:
                result[key] = value

    if cls is not None:
        try:
            type_hints = get_type_hints(cls)

            required_fields = get_required_fields(cls)

            missing_fields = [field for field in required_fields if field not in result]

            defaults = field_defaults or {}

            for field in missing_fields:
                if field in defaults:
                    result[field] = defaults[field]
                elif field in type_hints:
                    result[field] = get_default_value_by_type(type_hints[field])

            if field_defaults:
                for field, value in field_defaults.items():
                    if field not in result:
                        result[field] = value
        except Exception as e:
            logger.warning(f"필드 기본값 설정 중 오류 발생: {str(e)}")

    return result
