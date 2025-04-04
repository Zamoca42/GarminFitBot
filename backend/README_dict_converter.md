# Dict Converter 유틸리티

camelCase 형식의 키를 snake_case 형식으로 변환하고, 누락된 필수 필드에 자동으로 기본값을 설정하는 유틸리티 함수입니다.

## 기능

- **camel_to_snake_case**: camelCase 또는 PascalCase 문자열을 snake_case로 변환
- **get_required_fields**: 클래스의 필수 필드 목록 반환
- **get_default_value_by_type**: 필드 타입에 따른 기본값 생성
- **camel_to_snake_dict_safe**: 딕셔너리의 모든 키를 snake_case로 변환하고 누락된 필드에 기본값 설정

## 사용 방법

### 기본 사용법

```python
from core.util.dict_converter import camel_to_snake_dict_safe

# API 응답 데이터 (camelCase)
api_response = {
    "userName": "John",
    "userId": 123,
    "isActive": True,
}

# snake_case로 변환
snake_data = camel_to_snake_dict_safe(api_response)
# 결과: {"user_name": "John", "user_id": 123, "is_active": True}
```

### 모델 클래스를 사용한 필수 필드 자동 기본값 설정

```python
from dataclasses import dataclass
from typing import Optional
from core.util.dict_converter import camel_to_snake_dict_safe

@dataclass
class User:
    id: int
    name: str
    is_active: bool
    score: Optional[float] = None

# 일부 필드가 누락된 API 응답
api_response = {
    "userId": 123,
    # name과 isActive 필드 누락
}

# 변환 및 기본값 설정
user_data = camel_to_snake_dict_safe(api_response, cls=User)
# 결과: {"id": 123, "name": "", "is_active": False, "score": None}
```

### 사용자 정의 기본값 설정

```python
from dataclasses import dataclass
from core.util.dict_converter import camel_to_snake_dict_safe

@dataclass
class Config:
    api_key: str
    timeout: int
    host: str

# 필드가 누락된 API 응답
api_response = {
    "apiKey": "abc123",
    # timeout과 host 필드 누락
}

# 사용자 정의 기본값 설정
field_defaults = {
    "timeout": 30,
    "host": "localhost"
}

# 변환 및 사용자 정의 기본값 설정
config_data = camel_to_snake_dict_safe(api_response, cls=Config, field_defaults=field_defaults)
# 결과: {"api_key": "abc123", "timeout": 30, "host": "localhost"}
```

## 컬렉션 처리

- 중첩된 딕셔너리와 리스트도 재귀적으로 처리됩니다.
- 리스트 내의 딕셔너리도 snake_case로 변환됩니다.

```python
api_response = {
    "userName": "John",
    "userPosts": [
        {"postId": 1, "postTitle": "Hello"},
        {"postId": 2, "postTitle": "World"},
    ],
    "userProfile": {
        "firstName": "John",
        "lastName": "Doe",
    }
}

# 변환
snake_data = camel_to_snake_dict_safe(api_response)
# 결과: 모든 키가 snake_case로 변환됨 (중첩 구조 포함)
```

## 오류 처리

- 키 변환 과정에서 오류가 발생해도 가능한 데이터는 계속 처리됩니다.
- 모든 오류는 로그에 기록됩니다.

## 타입별 기본값

필드 타입에 따라 자동으로 설정되는 기본값:

- `int` → 0
- `float` → 0.0
- `str` → ""
- `bool` → False
- `list` → []
- `dict` → {}
- `datetime` → 현재 시간
- 복잡한 객체 타입 → None

## 테스트 실행 방법

unittest를 사용하여 테스트를 실행할 수 있습니다:

```bash
python -m unittest tests/test_dict_converter.py
```

또는 프로젝트의 테스트 스크립트를 사용:

```bash
python run_tests.py tests/test_dict_converter.py
```
