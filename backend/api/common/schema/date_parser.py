from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    id: str
    type: str


class DateValue(BaseModel):
    origin: str
    resolved: Optional[str] = None


class DateParserRequest(BaseModel):
    isInSlotFilling: bool = Field(default=False)
    utterance: str
    value: Optional[DateValue] = None
    user: User


class DateParserResponse(BaseModel):
    status: str = Field(
        ...,
        description="결과 상태 (SUCCESS/FAIL/ERROR/IGNORE)",
        examples=["SUCCESS", "FAIL", "ERROR", "IGNORE"]
    )
    value: str = Field(
        ..., 
        description="파싱된 날짜값 (YYYY-MM-DD 형식)", 
        examples=["2023-10-15"]
    )
    message: str = Field(
        ...,
        description="사용자 친화적인 메시지",
        examples=["2023년 10월 15일 (일)"]
    ) 

class Date(BaseModel):
    date: str = Field(..., description="분석 대상 날짜 (YYYY-MM-DD 형식)")
