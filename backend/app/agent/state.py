"""ReAct 에이전트 구현"""

from datetime import date
from typing import Annotated, Optional, TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field


class AgentState(TypedDict):
    """에이전트 상태"""

    messages: Annotated[list, add_messages]
    user_id: int
    start_date: Optional[date]
    end_date: Optional[date]
    user_timezone: Optional[str]
    today: Optional[date]


class DateRange(BaseModel):
    """날짜 범위"""

    start_date: str = Field(..., description="시작일 (YYYY-MM-DD 형식)")
    end_date: str = Field(..., description="종료일 (YYYY-MM-DD 형식)")
