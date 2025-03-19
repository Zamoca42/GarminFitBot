"""ReAct 에이전트 구현"""

from datetime import datetime
from typing import Optional

import pytz
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition, create_react_agent
from langsmith import traceable

from app.agent.state import AgentState, DateRange
from app.agent.tool import (
    HeartRateSummaryTool,
    HeartRateTimeSeriesTool,
    SleepSummaryTool,
    SleepTimeSeriesTool,
    StepsSummaryTool,
    StepsTimeSeriesTool,
    StressSummaryTool,
    StressTimeSeriesTool,
    ActivitySummaryTool,
)
from core.config import GEMINI_API_KEY


class HealthAnalysisAgent:
    """건강 데이터 분석 에이전트"""

    def __init__(self):
        self.tools = self._initialize_tools()
        self.prompt = self._create_health_analyze_prompt()
        self.graph = self._create_graph()

    def _initialize_tools(self):
        """도구 초기화"""
        return [
            # 심박수 도구
            HeartRateSummaryTool(),
            HeartRateTimeSeriesTool(),
            # 걸음수 도구
            StepsSummaryTool(),
            StepsTimeSeriesTool(),
            # 스트레스 도구
            StressSummaryTool(),
            StressTimeSeriesTool(),
            # 수면 도구
            SleepSummaryTool(),
            SleepTimeSeriesTool(),
            # 활동 도구
            ActivitySummaryTool(),
        ]

    def _initialize_llm(self, temperature: float = 0.8):
        """LLM 초기화"""
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=temperature,
        )

    def _create_health_analyze_prompt(self):
        """프롬프트 생성"""
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """당신은 가민 스마트워치 사용자의 건강 데이터를 분석하는 전문가입니다.
사용자의 질문에 답하기 위해 필요한 데이터를 수집하고 분석하세요.

분석 기간: {start_date} ~ {end_date}
사용자 ID: {user_id}
오늘 날짜: {today}

            도구 선택 기준:
            1. 데이터 유형과 파라미터 결정
               - 기간별 요약 데이터 (*_summary):
                 * 추세/패턴 분석이 필요한 경우
                 * "이번 주", "지난 달" 등 기간이 언급된 경우
                 * 평균, 통계, 추이 등의 단어가 포함된 경우
                 * 파라미터: user_id, start_date, end_date
               
               - 상세 시계열 데이터 (*_timeseries):
                 * 특정 시점의 상세 분석이 필요한 경우
                 * "어제", "오늘" 등 특정 날짜가 언급된 경우
                 * 파라미터: user_id, target_date (분석할 날짜)
                 * target_date 선택 기준:
                   - start_date와 end_date가 명시되지 않은 경우 end_date를 오늘로 설정
                   - start_date와 end_date가 명시된 경우 해당 기간 사용
                   - 특이점/문제 분석 시 해당 날짜 선택
            
            2. 건강 지표별 분석 패턴
               - 심박수 (heart_rate_*):
                 * 불규칙/변동 분석: timeseries로 해당 날짜 상세 확인
                   예) "어제 심박수가 불규칙했나요?" → end_date를 어제로 설정
                 * 평균/추이 분석: summary로 전체 기간 확인
                   예) "이번 주 심박수 추이" → start_date, end_date로 기간 설정
               
               - 걸음수 (steps_*):
                 * 특정일 활동: timeseries로 시간대별 확인
                   예) "화요일에 많이 걸었나요?" → end_date를 화요일로 설정
                 * 활동량 추세: summary로 기간 비교
                   예) "이번 주 운동량" → start_date, end_date로 기간 설정
               
               - 스트레스 (stress_*):
                 * 스트레스 피크: timeseries로 해당 시점 분석
                   예) "어제 스트레스가 심했나요?" → end_date를 어제로 설정
                 * 스트레스 관리: summary로 기간 평가
                   예) "이번 달 스트레스 관리" → start_date, end_date로 기간 설정
               
               - 수면 (sleep_*):
                 * 수면 질 분석: timeseries로 상세 단계 확인
                   예) "어젯밤 깊은 수면" → end_date를 어제로 설정
                 * 수면 패턴: summary로 전반적 평가
                   예) "이번 주 수면의 질" → start_date, end_date로 기간 설정

            3. 복합 분석 시나리오
               예시 1) "수면의 질이 좋은가요?"
               1) sleep_summary로 전체 기간 패턴 확인
               2) sleep_timeseries로 가장 대표적인 날짜 상세 분석
                  - 평균적인 날 선택
                  - 또는 특이점이 있는 날 선택
               3) stress_summary로 수면 중 스트레스 확인
               
               예시 2) "운동이 부족한가요?"
               1) steps_summary로 전체 활동량 확인
               2) heart_rate_timeseries로 가장 활동적인 날 상세 분석
               3) stress_summary로 운동 강도 평가

            4. 날짜 선택 전략
               - 시계열 분석 (timeseries):
                 * 특정 날짜 요청: 해당 날짜 선택
                 * 최근 데이터 요청: end_date 선택
                 * 특이점 분석: 해당 특이점의 날짜 선택
                 * 대표값 필요: 기간 내 중간값 또는 평균적인 날짜 선택
               
               - 요약 분석 (summary):
                 * 항상 전체 기간(start_date ~ end_date) 사용
                 * 추세와 패턴을 파악하기 위함

""",
                ),
                ("human", "{input}"),
            ]
        )

    def _create_analyze_health_node(self):
        """건강 분석 노드 생성"""
        llm_with_tools = self._initialize_llm().bind_tools(self.tools)
        prompt = self._create_health_analyze_prompt()

        def analyze_health(state: AgentState):
            prompt_input = prompt.invoke(
                {
                    "input": state["messages"],
                    "user_id": state["user_id"],
                    "start_date": state["start_date"],
                    "end_date": state["end_date"],
                    "today": state["today"],
                }
            )
            response = llm_with_tools.invoke(prompt_input)
            return {
                "messages": [response],
            }
        
        return analyze_health

    
    def _create_date_prompt(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """당신은 쿼리에서 날짜 정보를 파악하는 전문가입니다.
                 오늘 날짜는 {today}입니다.
                
                다음과 같은 규칙을 따르세요:
                1. 쿼리에서 날짜 관련 표현을 찾아내세요 (예: 어제, 이번 주, 지난 달 등)
                2. 해당 표현을 실제 날짜로 변환하세요
                3. 날짜 설정 규칙:
                   - 시계열 분석 필요시 (예: "어제 수면", "오늘 심박수"):
                     * end_date를 해당 날짜로 설정
                     * start_date는 end_date와 동일하게 설정
                   - 기간 분석 필요시 (예: "이번 주 운동량"):
                     * start_date와 end_date를 해당 기간으로 설정
                4. 날짜가 명시되지 않은 경우:
                   - 시계열 분석은 end_date를 오늘로 설정
                   - 기간 분석은 최근 7일로 설정
                
                예시:
                - "어제 수면은 어땠나요?" → start_date와 end_date를 어제로 설정
                - "이번 주 운동량은?" → start_date는 이번 주 월요일, end_date는 오늘로 설정
                - "오늘 심박수가 불규칙한가요?" → start_date와 end_date를 오늘로 설정
                """,
                ),
                ("human", "{query}"),
            ]
        )
        return prompt

    def _create_plan_processor(self):
        """날짜 처리 및 분석 계획 생성 노드"""
        date_llm = self._initialize_llm(temperature=0).with_structured_output(DateRange)

        def plan_processor(state: AgentState):
            query = state["messages"][-1].content

            # 1. 날짜 처리
            dates = self._create_date_prompt().invoke({"today": state["today"].strftime("%Y-%m-%d"), "query": query})
            output = date_llm.invoke(dates)
            
            start_date = datetime.strptime(output.start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(output.end_date, "%Y-%m-%d").date()
            
            # 상세한 분석 계획 생성
            date_message = f"""
            날짜 범위가 설정되었습니다: {start_date} ~ {end_date}.
            
            분석 계획:
            ## 건강 데이터 분석 계획 (사용자 ID: {state["user_id"]}, 기간: {start_date} ~ {end_date})

**사용자 질문:** {query}

**목표:** 제공된 기간 동안 사용자의 심박수, 걸음수/활동량, 스트레스, 수면 데이터를 분석하여 전반적인 건강 상태를 파악하고, 특이점을 식별하여 추가 분석을 수행하고, 건강 지표 간의 상관관계를 분석하여 맞춤형 피드백과 개선 방안을 제시합니다.

**1. 데이터 분석 도구 선택 및 활용 전략**

| 건강 지표 | Summary 도구 | Timeseries 도구 | 활용 목적                                                                                                                                                                                             |
|---|---|---|---|
| 심박수 (heart_rate) | heart_rate_summary | heart_rate_timeseries | - **Summary:** 평균 심박수, 최대/최저 심박수를 확인하여 전반적인 심박수 수준을 파악합니다.  - **Timeseries:** 시간별 심박수 변화를 추적하여 특이 패턴 (급격한 변화, 지속적인 높은/낮은 심박수)을 식별합니다.  특히, 수면 중 심박수 변화와 활동 중 심박수 변화를 비교 분석합니다. |
| 걸음수/활동량 (steps) | steps_summary | steps_timeseries | - **Summary:** 총 걸음수, 평균 걸음수를 확인하여 전반적인 활동량을 파악합니다.  목표 걸음수 달성 여부를 확인합니다. - **Timeseries:** 시간별 걸음수 변화를 추적하여 활동 패턴 (활동 시간대, 활동 강도)을 파악합니다.  주말/주중 활동량 비교 분석을 수행합니다. |
| 스트레스 (stress) | stress_summary | stress_timeseries | - **Summary:** 평균 스트레스 수준, 최고 스트레스 수준을 확인하여 전반적인 스트레스 정도를 파악합니다.  - **Timeseries:** 시간별 스트레스 변화를 추적하여 스트레스 발생 패턴 (특정 시간대, 특정 활동)을 파악합니다.  수면 전 스트레스 수준을 분석하여 수면의 질에 미치는 영향을 파악합니다. |
| 수면 (sleep) | sleep_summary | sleep_timeseries | - **Summary:** 총 수면 시간, 수면 효율, 깊은 수면/얕은 수면 비율을 확인하여 전반적인 수면의 질을 파악합니다.  - **Timeseries:** 수면 단계 변화를 추적하여 수면 패턴 (입면 시간, 각성 횟수)을 파악합니다.  다른 건강 지표와 비교하여 수면의 질에 영향을 미치는 요인을 분석합니다. |

**2. 특이점 식별 방법**

*   **통계적 방법:**
    *   **평균 및 표준편차 활용:** 각 건강 지표의 평균과 표준편차를 계산하고, 평균에서 ± 2 표준편차 이상 벗어나는 값을 특이점으로 간주합니다.
    *   **이동 평균 활용:** 3일 또는 5일 이동 평균을 계산하여, 실제 값과의 차이가 큰 날짜를 특이점으로 식별합니다.
*   **기준값 비교:**
    *   **개인별 목표치 비교:** 사용자가 설정한 목표 걸음수, 수면 시간 등과 비교하여 달성 여부를 확인하고, 크게 미달하거나 초과하는 날짜를 특이점으로 식별합니다.
    *   **과거 데이터 비교 (가능한 경우):** 과거 데이터가 있는 경우, 해당 기간과 비교하여 유의미한 변화가 있는 날짜를 특이점으로 식별합니다.
*   **예외적인 상황 고려:**
    *   **사용자에게 특이한 이벤트 (여행, 행사, 질병 등)가 있었는지 확인:** 특이점이 발생한 날짜에 특별한 이벤트가 있었는지 확인하여 데이터 해석에 반영합니다.

**3. 특이점 발생 시 추가 분석**

특이점이 식별된 경우, 다음과 같은 추가 분석을 수행합니다.

*   **상세 Timeseries 분석:** 해당 날짜의 Timeseries 데이터를 자세히 분석하여 특이점 발생 원인을 추정합니다 (예: 특정 시간대의 심박수 급증 원인 분석).
*   **관련 데이터 교차 분석:** 다른 건강 지표와 교차 분석하여 특이점 발생 원인을 규명합니다 (예: 스트레스 증가와 수면 부족의 연관성 분석).
*   **사용자 추가 정보 확인:** 사용자에게 특이점 발생 원인에 대한 추가 정보를 요청합니다 (예: "해당 날짜에 특별한 일이 있었나요?").

**4. 건강 지표 간 상관관계 분석**

다음과 같은 방법으로 건강 지표 간의 상관관계를 분석합니다.

*   **시각적 분석:** 각 건강 지표의 Timeseries 데이터를 시각적으로 비교하여 패턴의 유사성을 파악합니다 (예: 스트레스 증가와 심박수 증가의 동시 발생).
*   **통계적 분석:** 상관 계수를 계산하여 건강 지표 간의 통계적 연관성을 확인합니다.  피어슨 상관 계수를 사용하여 선형 관계를 분석하고, 스피어만 상관 계수를 사용하여 비선형 관계를 분석합니다.
*   **인과 관계 추론:** 상관관계 분석 결과를 바탕으로 인과 관계를 추론합니다.  하지만, 상관관계가 인과관계를 의미하는 것은 아니므로, 추가적인 정보와 논리적인 추론을 통해 인과 관계를 판단합니다.  예를 들어, 수면 부족이 스트레스 증가를 유발하는지, 또는 스트레스 증가가 수면 부족을 유발하는지 등을 분석합니다.

**5. 피드백 및 개선 방안 제시**

분석 결과를 바탕으로 사용자에게 맞춤형 피드백과 개선 방안을 제시합니다.

*   **긍정적인 부분 강조:** 건강 상태가 좋은 부분 (예: 꾸준한 활동량 유지, 충분한 수면 시간 확보)을 강조하여 동기 부여를 높입니다.
*   **개선 필요한 부분 지적:** 개선이 필요한 부분 (예: 높은 스트레스 수준, 불규칙한 수면 패턴)을 구체적으로 지적하고, 개선 방안을 제시합니다.
*   **맞춤형 개선 방안 제시:** 사용자의 생활 습관, 선호도, 목표 등을 고려하여 맞춤형 개선 방안을 제시합니다.  예를 들어, 스트레스 관리를 위해 명상, 요가, 취미 활동 등의 방법을 제안하고, 수면의 질 개선을 위해 규칙적인 수면 시간, 수면 환경 개선 등을 제안합니다.
*   **구체적인 실행 계획 제시:** 개선 방안을 실천하기 위한 구체적인 실행 계획을 제시합니다.  예를 들어, "매일 30분씩 걷기", "취침 1시간 전에는 스마트폰 사용하지 않기" 등의 구체적인 목표를 설정하도록 돕습니다.
*   **지속적인 모니터링 및 피드백 제공:** 개선 노력을 지속적으로 모니터링하고, 주기적으로 피드백을 제공하여 사용자가 꾸준히 건강 관리를 할 수 있도록 지원합니다.

            """

            return {
                "messages": [SystemMessage(content=date_message)],
                "start_date": start_date,
                "end_date": end_date,
            }

        return plan_processor

    def _create_graph(self):
        """그래프 생성"""
        # 툴 노드 생성
        tools_node = ToolNode(tools=self.tools)
        planner_node_title = "planner"
        analyzer_node_title = "analyze_health"
        tools_node_title = "tools"

        # 그래프 생성
        workflow = StateGraph(AgentState)

        # 노드 추가
        workflow.add_node(planner_node_title, self._create_plan_processor())
        workflow.add_node(analyzer_node_title, self._create_analyze_health_node())
        workflow.add_node(tools_node_title, tools_node)

        # 엣지 추가
        workflow.set_entry_point(planner_node_title)
        workflow.add_edge(planner_node_title, analyzer_node_title)
        workflow.add_conditional_edges(analyzer_node_title, tools_condition)
        workflow.add_edge(tools_node_title, analyzer_node_title)

        return workflow.compile()

    def create_initial_state(
        self,
        query: str,
        user_id: int,
        user_timezone: Optional[str] = None,
    ) -> dict:
        """초기 상태 생성"""
        timezone = pytz.timezone(user_timezone) if user_timezone else pytz.utc
        today = datetime.now(timezone).date()
        
        return {
            "messages": [HumanMessage(content=query)],
            "user_id": user_id,
            "user_timezone": user_timezone,
            "today": today,
        }

    @traceable
    def run(
        self,
        query: str,
        user_id: int,
        user_timezone: Optional[str] = None,
    ) -> str:
        """에이전트 실행"""
        try:
            initial_state = self.create_initial_state(
                query=query,
                user_id=user_id,
                user_timezone=user_timezone,
            )

            graph = self._create_graph()
            final_result = graph.invoke(initial_state)
            
            return final_result

        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"에러가 발생했습니다: {str(e)}"

    def visualize_graph(self, output_path="graph_visualization.png"):
        """그래프를 시각화하고 파일로 저장합니다.

        Args:
            output_path (str): 저장할 파일 경로

        Returns:
            bool: 성공 여부
        """
        try:
            graph = self._create_graph()

            graph_image = graph.get_graph().draw_mermaid_png()
            with open(output_path, "wb") as f:
                f.write(graph_image)
            print(f"그래프 시각화가 '{output_path}' 파일로 저장되었습니다.")
            return True
        except Exception as e:
            print(f"그래프 시각화 중 오류 발생: {str(e)}")
            return False


def create_agent() -> HealthAnalysisAgent:
    """건강 분석 에이전트 생성

    Args:
        session: SQLAlchemy 세션

    Returns:
        HealthAnalysisAgent: 초기화된 건강 분석 에이전트
    """
    return HealthAnalysisAgent()
