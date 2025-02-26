from typing import Optional, Type

from pydantic import BaseModel, create_model
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase


def create_pydantic_model(
    db_model: Type[DeclarativeBase],
    name_suffix: str = "",
    exclude_fields: list = None,
    optional_fields: list = None,
) -> Type[BaseModel]:
    """
    SQLAlchemy 모델을 기반으로 Pydantic 모델 생성

    Args:
        db_model: SQLAlchemy 모델
        name_suffix: 모델 이름 접미사 (예: "Create", "Response")
        exclude_fields: 제외할 필드 목록
        optional_fields: Optional로 설정할 필드 목록
    """
    exclude_fields = exclude_fields or []
    optional_fields = optional_fields or []

    # SQLAlchemy 모델의 컬럼 정보 가져오기
    mapper = inspect(db_model)
    fields = {}

    for column in mapper.columns:
        if column.name in exclude_fields:
            continue

        python_type = column.type.python_type

        # Optional 필드 처리
        if column.name in optional_fields or column.nullable:
            python_type = Optional[python_type]

        fields[column.name] = (python_type, ...)

    # Pydantic 모델 생성
    model_name = f"{db_model.__name__}{name_suffix}"

    pydantic_model = create_model(model_name, __base__=BaseModel, **fields)

    # SQLAlchemy 모델 변환 설정 추가
    pydantic_model.Config = type("Config", (), {"from_attributes": True})

    return pydantic_model
