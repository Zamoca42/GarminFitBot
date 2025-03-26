"""ReAct 에이전트 구현"""

from datetime import datetime
from typing import Optional

import pytz
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from langsmith import traceable

from app.agent.prompt import (
    create_date_prompt,
    create_execute_tool_prompt,
    create_final_report_prompt,
    create_health_analyze_prompt,
    create_planner_prompt,
)
from app.agent.state import (
    AgentState,
    AnalysisPlan,
    DateRange,
    HealthAnalysisResult,
    save_analysis_result,
)
from app.agent.tool import (
    ActivitySummaryTool,
    HeartRateSummaryTool,
    HeartRateTimeSeriesTool,
    SleepSummaryTool,
    SleepTimeSeriesTool,
    StepsSummaryTool,
    StepsTimeSeriesTool,
    StressSummaryTool,
    StressTimeSeriesTool,
)
from core.config import GEMINI_API_KEY


class HealthAnalysisAgent:
    """건강 데이터 분석 에이전트"""

    def __init__(self):
        self.tools = self._initialize_tools()
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

    def _extract_tool_metadata(self):
        """도구 리스트에서 name, description, parameters 추출"""
        tools_info = []

        for tool in self.tools:
            tool_info = {
                "name": tool.name,
                "description": tool.description,
                "parameters": list(tool.args_schema.__annotations__.keys()),
            }
            tools_info.append(tool_info)

        return tools_info

    def _initialize_llm(self, temperature: float = 0.8):
        """LLM 초기화"""
        model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=temperature,
        )
        return model

    def _extract_analysis_dates(self, state: AgentState):
        """사용자 쿼리에서 분석할 날짜 범위를 추출"""
        date_llm = self._initialize_llm(temperature=0).with_structured_output(DateRange)
        dates = create_date_prompt().invoke(
            {
                "today": state["today"].strftime("%Y-%m-%d"),
                "query": state["user_query"],
            }
        )
        return date_llm.invoke(dates)

    def _generate_analysis_plan(self, state: AgentState, start_date, end_date):
        """추출된 날짜 범위를 기반으로 분석 계획을 생성"""
        planner_llm = self._initialize_llm().with_structured_output(AnalysisPlan)
        date_message = SystemMessage(
            content=f"오늘 날짜는 {state['today'].strftime('%Y-%m-%d')}입니다. 분석해야 할 기간은 {start_date}부터 {end_date}까지입니다."
        )
        planner_message = [
            create_planner_prompt(),
            date_message,
            HumanMessage(content=state["user_query"]),
        ]
        return planner_llm.invoke(planner_message)

    def _create_plan_node(self):
        """사용자 질문에 따른 분석 기간과 계획 생성"""

        def plan_processor(state: AgentState):
            output = self._extract_analysis_dates(state)
            start_date = datetime.strptime(output.start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(output.end_date, "%Y-%m-%d").date()
            response = self._generate_analysis_plan(state, start_date, end_date)
            return {
                "analysis_plan": response.analysis_plan,
                "focus_areas": response.focus_areas,
                "user_intent": response.user_intent,
                "start_date": start_date,
                "end_date": end_date,
            }

        return plan_processor

    def _format_tool_execution_message(self, state: AgentState):
        """분석 계획과 추가 분석 요청을 기반으로 실행 메시지 생성"""
        last_analysis = (
            state["analysis_history"][-1] if state["analysis_history"] else None
        )

        additional_analysis_targets = (
            ", ".join(last_analysis.additional_analysis_targets)
            if last_analysis and last_analysis.additional_analysis_targets
            else "없음"
        )
        analysis_plan_string = "\n".join(
            [f"- {plan}" for plan in state["analysis_plan"]]
        )

        messages = [
            HumanMessage(
                content=f"사용자 아이디 {state['user_id']}의 분석 계획:\n{analysis_plan_string}"
            )
        ]

        if last_analysis and last_analysis.additional_analysis_targets:
            messages.append(
                HumanMessage(
                    content=f"추가 분석이 필요한 경우, 조회할 데이터 목록: {additional_analysis_targets}"
                )
            )

        return messages

    def _select_tools_to_execute(self, state: AgentState, messages):
        """AI에게 적절한 도구 실행을 요청"""

        tools_selection_llm = self._initialize_llm().bind_tools(
            self.tools, tool_choice=True
        )
        tools_info = self._extract_tool_metadata()
        system_message = create_execute_tool_prompt(
            tools_info, state["user_id"], state["tool_history"]
        )
        valid_messages = [m for m in messages if m is not None]
        return tools_selection_llm.invoke([system_message] + valid_messages)

    def _create_execute_tool_node(self):
        """계획과 실행 이력을 바탕으로 도구를 실행하는 노드"""

        def execute_tool(state: AgentState):
            messages = self._format_tool_execution_message(state)
            response = self._select_tools_to_execute(state, messages)
            return {"messages": state["messages"] + [response]}

        return execute_tool

    def _extract_tool_execution_results(self, state: AgentState):
        """도구 실행 결과를 수집하여 정리"""
        tool_messages = []
        tool_calls = []
        for message in reversed(state["messages"]):
            if isinstance(message, AIMessage) and message.content != "":
                break
            if isinstance(message, ToolMessage):
                tool_messages.append(message)
            if isinstance(message, AIMessage) and message.content == "":
                tool_calls = message.tool_calls

        for tool_call in tool_calls:
            tool_result = next(
                (
                    msg.status
                    for msg in tool_messages
                    if msg.tool_call_id == tool_call["id"]
                ),
                "error",
            )
            state["tool_history"].append(
                {
                    "name": tool_call["name"],
                    "arguments": tool_call["args"],
                    "status": tool_result,
                }
            )

        return [msg.content for msg in tool_messages]

    def _generate_analysis(self, state: AgentState, parsed_tool_data):
        """AI에게 건강 데이터 분석 요청"""
        analyze_health_llm = self._initialize_llm().with_structured_output(
            HealthAnalysisResult
        )
        system_message = create_health_analyze_prompt()
        human_message = HumanMessage(content=f"도구 실행 결과: {parsed_tool_data}")

        previous_analysis_summaries = (
            "\n\n".join(
                [
                    f"이전 분석 결과 {i+1}:\n{history.summary}\n\n주요 인사이트:\n- "
                    + "\n- ".join(history.insights)
                    for i, history in enumerate(state["analysis_history"][-5:])
                ]
            )
            if state["analysis_history"]
            else "이전 분석 결과 없음."
        )

        plan_items = [f"- {plan}" for plan in state["analysis_plan"]]
        analysis_plan = """
        분석 계획:
        """ + "\n".join(plan_items)

        previous_analysis_message = SystemMessage(
            content=f"""
            사용자 질문의도: {state["user_intent"]}
            
            {analysis_plan}

            이전 분석 결과를 고려하여 새로운 건강 분석을 수행하세요.

            {previous_analysis_summaries}
            """
        )
        response = analyze_health_llm.invoke(
            [system_message, human_message, previous_analysis_message]
        )

        if response is None:
            raise ValueError("Health analysis model returned None!")

        return response

    def _create_analysis_node(self):
        """도구 실행 결과를 분석하고 추가 분석 여부를 판단하는 노드"""

        def analysis(state: AgentState):
            parsed_tool_data = self._extract_tool_execution_results(state)
            response = self._generate_analysis(state, parsed_tool_data)
            if response is None or response.summary is None:
                raise ValueError(
                    "Health analysis response is invalid or missing a summary."
                )
            save_analysis_result(state, response)
            return {
                "messages": state["messages"] + [AIMessage(content=response.summary)]
            }

        return analysis

    def _create_report_node(self):
        """분석 노드의 결과를 최종 보고서로 변환하는 노드"""
        llm = self._initialize_llm()

        def report(state: AgentState):
            past_summaries = [history.summary for history in state["analysis_history"]]

            past_insights = []
            for history in state["analysis_history"]:
                past_insights.extend(history.insights)

            joined_summaries = " ".join(past_summaries)
            joined_insights = "- " + "\n- ".join(past_insights)

            human_message = HumanMessage(
                content=f"""
                # 🏥 ({', '.join(state.get('focus_areas', ['건강']))} 중 사용자 질문 의도에 맞는 단어) 분석 보고서

                ## 🙋 사용자 질문 의도
                {state.get("user_intent", "최근 건강 상태가 어떤지 알고 싶어합니다.")}

                # 📌 요약
                {joined_summaries}

                # 🔍 주요 인사이트
                {joined_insights}

                위 데이터를 기반으로 건강 피드백과 개선 방안을 Markdown 형식으로 작성하세요.
                """
            )
            response = llm.invoke([create_final_report_prompt(), human_message])

            return {
                "messages": state["messages"] + [response],
            }

        return report

    def _create_graph(self):
        """그래프 생성"""

        tools_node = ToolNode(tools=self.tools)
        plan_node_title = "plan"
        execute_tool_node_title = "execute_tool"
        analysis_node_title = "analysis"
        report_node_title = "report"
        tools_node_title = "tools"

        # 그래프 생성
        workflow = StateGraph(AgentState)

        def custom_tool_condition(state: AgentState):
            """도구 선택 조건"""
            last_analysis = (
                state["analysis_history"][-1] if state["analysis_history"] else None
            )

            return (
                "추가 분석 요청"
                if last_analysis and last_analysis.additional_analysis_needed
                else "리포트 생성"
            )

        # 노드 추가
        workflow.add_node(plan_node_title, self._create_plan_node())
        workflow.add_node(analysis_node_title, self._create_analysis_node())
        workflow.add_node(execute_tool_node_title, self._create_execute_tool_node())
        workflow.add_node(report_node_title, self._create_report_node())
        workflow.add_node(tools_node_title, tools_node)

        # 엣지 추가
        workflow.set_entry_point(plan_node_title)
        workflow.add_edge(plan_node_title, execute_tool_node_title)
        workflow.add_edge(execute_tool_node_title, tools_node_title)
        workflow.add_edge(tools_node_title, analysis_node_title)
        workflow.add_edge(report_node_title, END)

        # 조건 엣지 추가
        workflow.add_conditional_edges(
            analysis_node_title,
            custom_tool_condition,
            {
                "추가 분석 요청": execute_tool_node_title,
                "리포트 생성": report_node_title,
            },
        )

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
            "user_query": query,
            "user_id": user_id,
            "user_timezone": user_timezone,
            "today": today,
            "tool_history": [],
            "analysis_history": [],
        }

    @traceable
    def run(
        self,
        query: str,
        user_id: int,
        user_timezone: Optional[str] = None,
    ):
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

    Returns:
        HealthAnalysisAgent: 초기화된 건강 분석 에이전트
    """
    return HealthAnalysisAgent()
