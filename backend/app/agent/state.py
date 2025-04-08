from datetime import date
from typing import Annotated, Any, Dict, List, Optional, Tuple, TypedDict, Union

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class AnalysisPlan(BaseModel):
    """분석 계획"""

    analysis_plan: List[str]
    focus_areas: List[str]
    user_intent: str


class DateRange(BaseModel):
    """날짜 범위"""

    start_date: str = Field(..., description="시작일 (YYYY-MM-DD 형식)")
    end_date: str = Field(..., description="종료일 (YYYY-MM-DD 형식)")


class InsightItem(BaseModel):
    comment: str = Field(..., description="날짜별 주요 패턴 및 통찰")


class HealthAnalysisResult(BaseModel):
    """LLM이 반환할 건강 분석 결과의 구조"""

    summary: str = Field(..., description="건강 분석 요약")
    insights: List[InsightItem] = Field(
        ..., description="추출된 건강 상태 관련 주요 패턴 및 통찰"
    )
    additional_analysis_needed: bool = Field(
        ..., description="추가 분석이 필요한지 여부"
    )
    additional_analysis_targets: Optional[List[str]] = Field(
        None, description="추가 분석이 필요한 경우, 어떤 데이터를 조회해야 하는지 목록"
    )


class ToolHistory(TypedDict):
    """도구 사용 이력"""

    name: str
    arguments: Dict[str, Union[int, str, date]]
    status: str


class AgentState(TypedDict):
    """에이전트 상태"""

    user_query: str
    analysis_plan: Optional[List[str]]
    focus_areas: Optional[List[str]]
    user_intent: Optional[str]
    messages: Annotated[list, add_messages]
    tool_needed: bool = True
    user_id: int
    detail_params: Dict[str, Any]
    user_timezone: Optional[str]
    today: Optional[date]
    final_report: str

    loop_count: int
    analysis_history: Optional[List[HealthAnalysisResult]]
    tool_history: Optional[List[ToolHistory]]


def save_analysis_result(state: AgentState, result: HealthAnalysisResult):
    if state.get("analysis_history") is None:
        state["analysis_history"] = []
    state["analysis_history"].append(result)


def determine_date_type_and_origin(
    detail_params: dict, user_query: str
) -> tuple[str, str]:
    if "sys_date_period" in detail_params:
        return "period", detail_params["sys_date_period"]["origin"]
    elif "sys_date" in detail_params:
        return "single", detail_params["sys_date"]["origin"]
    else:
        return "auto", user_query
