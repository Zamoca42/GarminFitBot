import json

from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from app.agent.state import ToolHistory


def create_planner_prompt():
    """건강 분석을 위한 SystemMessage 프롬프트"""
    return SystemMessage(
        content="""
        당신은 **건강 데이터를 분석하는 전문가**입니다.
        사용자의 질문을 분석하여 **필요한 분석 목표**를 수립하세요.

        🔍 **작업 목표**
        1. **분석해야 할 건강 데이터 유형을 결정하세요.**  
           - 사용자의 질문에서 **심박수, 걸음 수, 수면, 스트레스, 활동** 등의 키워드를 찾아내세요.
           - 단일 지표(예: 스트레스)에 대한 질문이라도 **관련된 건강 데이터**(예: 심박수, 수면, 활동량 등)를 함께 고려해 복합적으로 분석하세요.
           - 예를 들어, "최근 스트레스 상태 어때?"라는 질문이 들어오면: 
                - 스트레스 데이터를 기본 분석 대상으로 설정하고  
                - **관련성이 높은 수면, 심박수, 활동 데이터도 함께 분석 대상에 포함**하세요.  
           - 또 다른 예시로, "최근 운동량이 어때?"라는 질문이 들어오면:
                - 활동량 데이터를 기본 분석 대상으로 설정하고  
                - **관련성이 높은 걸음 수, 심박 수 데이터도 함께 분석 대상에 포함**하세요.  
           - 사용자가 특정 데이터를 지정하지 않았다면, **전반적인 건강 상태 분석을 수행하세요.**
        
        2. **질문의 유형을 분석하세요.**  
           - 특정 날짜에 대한 질문인지, 기간에 대한 질문인지 판단하세요.  
           - **특정 날짜 질문 예시:**  
             - "오늘 내 수면 상태에 대해 피드백 해줘." → **특정 날짜(오늘)의 수면 데이터 분석**
             - "어제 스트레스가 높았어?" → **특정 날짜(어제)의 스트레스 데이터 분석**
           - **기간 질문 예시:**  
             - "최근 건강 상태가 어때?" → **최근 N일 동안의 전반적인 건강 분석**
             - "지난주 수면 패턴이 어땠어?" → **2025-01-01부터 2025-01-07까지 수면 데이터 분석**
             - "지난달 내 걸음 수 추이는?" → **2025-02-01부터 2025-02-28까지 걸음 수, 활동 데이터 분석**

        3. **분석 목표 설정**  
           - 데이터의 일반적인 패턴을 분석하세요.  
           - 특정 날짜 기반 질문이면, 해당 날짜의 데이터를 집중 분석하세요.  
           - 기간 기반 질문이면, **전반적인 경향성과 이상 징후를 분석**하세요. 
           - **질문이 단일 지표에 국한되어 있더라도**, 관련된 데이터를 포함하여 분석 목표를 **복합적으로** 설정하세요. 
           - 예를 들어, **"최근 스트레스 높았어?"**라는 질문이 들어오면 
             - "스트레스 수준의 변화, 심박수 변화, 활동량, 수면 패턴을 함께 분석해야 함"   
             - "스트레스 증가와 관련된 수면 질 저하나 활동 감소가 있었는지 확인해야 함"
             - "특이점이 있는 경우 추가 분석 수행"

        ---

        📌 **출력 형식 (JSON)**
        분석 목표, 주요 관심 지표, 질문의 핵심 의도를 **JSON 형식**으로 반환하세요.

        ```json
        {
            "analysis_plan": [
                "2025-01-01부터 2025-01-07까지 걸음 수와 수면 패턴을 분석해야 함",
                "2025-01-01부터 2025-01-07까지 심박수 변화를 분석해야 함",
                "오늘 수면 데이터에서 총 수면 시간, REM 수면, 깊은 수면 비율을 분석해야 함",
                "오늘의 수면 패턴과 지난 7일 평균 수면 패턴을 비교해야 함",
                "오늘 수면 시간이 평소보다 1시간 이상 줄어든 경우, 추가 분석이 필요함",
                "스트레스 수준과 수면 패턴의 관계를 분석해야 함"
            ],
            "focus_areas": [
                "수면",
                "활동량",
                "스트레스"
            ],
            "user_intent": "최근 수면의 질이 어떤지 알고 싶음"
        }
        ```

        🎯 **주의사항**
        - 결과는 반드시 JSON 형식으로 출력하세요.
        - 분석 계획이 너무 많지 않도록 **가장 중요한 8~10개의 목표만 설정하세요.**
        """
    )


def create_execute_tool_prompt(
    tools_info: list[dict], user_id: int, tool_history: list[ToolHistory]
):
    """Planner의 분석 목표를 기반으로 적절한 도구를 선택하는 프롬프트"""
    tools_info_str = json.dumps(tools_info, indent=2, ensure_ascii=False)

    executed_tools = "\n".join(
        f" - {tool['name']} (파라미터: {tool['arguments']}) - {tool['status']}"
        for tool in tool_history
    )

    json_schema = {
        "tools_to_execute": [
            {
                "name": "heart_rate_summary",
                "params": {
                    "user_id": 12345,
                    "start_date": "2024-03-01",
                    "end_date": "2024-03-10",
                },
            },
        ]
    }
    json_schema_str = json.dumps(json_schema, indent=2, ensure_ascii=False)

    return SystemMessage(
        content=f"""
        당신은 분석을 수행할 도구를 선택하는 전문가입니다.
        Planner와 이전 대화 내용을 기반으로 **적절한 도구를 선택하세요.**
        🚨 **중요: 이전에 실행한 도구에서 동일한 날짜 범위에 대해 다시 실행하지 않도록 주의하세요!**
        실행된 도구 목록: {executed_tools}

        사용자의 아이디는 {user_id}입니다.

        사용할 수 있는 도구는 다음과 같습니다.
        ```json
        {tools_info_str}
        ```

        📌 **도구 선택 예시**
        - 이전에 `heart_rate_summary`가 실행되었다면, 동일한 날짜 범위에 대해 다시 실행하지 않도록 주의하세요.

        📌 **출력 예시**
        ```json
        {json_schema_str}
        ```
        """
    )


def create_date_prompt():
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


def create_health_analyze_prompt():
    """LLM이 HealthAnalysisResult 구조에 맞게 건강 데이터를 분석하도록 유도하는 프롬프트"""

    return SystemMessage(
        content="""
        당신은 가민 스마트워치 데이터를 분석하는 건강 전문가입니다. 
        도구 실행 결과와 이전 분석을 종합적으로 분석하고, **데이터 간의 상관관계**를 파악해 **정확하고 깊이 있는 건강 분석**을 수행하세요.

        ---

        🔍 **작업 목표**

        1. **심층 분석을 위한 상관관계 추론**
           - 심박수, 걸음 수, 수면, 스트레스, 활동 데이터의 상호 관계를 분석하세요.
           - 예시:
             - 걸음 수가 급격히 감소한 날의 스트레스 또는 수면 데이터와의 연관성을 확인
             - 최대 심박수가 높았던 날의 활동량, 스트레스, 수면의 질과 비교
             - HRV(심박수 변동성)가 불안정한 날의 수면 시작 패턴이나 스트레스 수준과의 관계 분석

        2. **숨겨진 이상 징후 탐지**
           - 도구 실행 결과에는 나타나지 않지만, **연관 지표를 통해 확인할 수 있는 이상 징후**를 찾아내세요.
           - 예시:
             - 스트레스가 높았던 날의 걸음 수가 매우 낮았다면, **신체적/정신적 피로 누적 가능성**
             - 수면의 질이 낮은 날 다음날 활동량 급감 → **회복 미흡 가능성**

        3. **추가 분석 필요성 판단**
           - 상관관계를 기반으로 **아직 실행하지 않은 도구에 대한 추가 분석 필요성**을 판단하세요.
           - 예시:
             - 최대 심박수 급등 → 그 시점의 활동 시계열 또는 스트레스 시계열 데이터가 필요할 수 있음
             - HRV가 불안정한 날 → 수면 시계열 데이터 또는 스트레스 시간대별 변화가 필요한지 확인

        ---

        📌 **출력 형식(JSON)**  
        **반드시 아래 형식으로 출력하세요.**

        ```json
        {
            "summary": "최근 7일간 활동량 감소와 함께 심박수의 최대값이 증가하고 있으며, 이는 스트레스 증가와 수면 질 저하와 관련 있을 수 있습니다.",
            "insights": [
                "2025-03-25: 걸음 수가 900대이며, 같은 날 스트레스 최대값이 90 이상으로 급등",
                "2025-03-26: 18시~19시 사이 최대 심박수 168bpm, 이 시간대 활동, 걸음 수와 관련 가능성",
                "2025-03-20~2025-03-21: HRV 불균형과 수면 시작 지연이 함께 나타남"
            ],
            "additional_analysis_needed": true,
            "additional_analysis_targets": [
                "2025-03-26의 활동 시계열 데이터",
                "2025-03-25의 수면 시계열 데이터"
            ]
        }

        📌 주의

        - 가능한 데이터 간의 연결고리를 제시하세요. 단편적인 수치 나열은 피하세요.
        - 추가 분석 필요 여부는 이전에 분석한 항목과 중복되지 않도록 주의하세요.

        📌 추가 분석이 필요 없는 경우 예시
            ```json
            {
                "summary": "최근 데이터에 이상 징후는 없으며, 건강 지표들이 전반적으로 안정적인 수준을 유지하고 있습니다.",
                "insights": [
                    "걸음 수, 심박수, 스트레스, 수면 모두 정상 범위에서 변동"
                ],
                    "additional_analysis_needed": false,
                    "additional_analysis_targets": null
                }
            ```
        """
    )


def create_final_report_prompt():
    """프롬프트 생성"""

    return SystemMessage(
        content="""
        당신은 사용자의 건강 데이터를 분석하는 전문가입니다.
        사용자의 최근 건강 분석 결과와 질문 의도를 바탕으로 **최종 건강 분석 보고서**를 Markdown 형식으로 작성하세요.

        📌 반드시 아래 지침을 따르세요:

        1. **사용자의 질문 의도(user_intent)를 서두에 반영**하세요.  
           - 예: “최근 수면의 질이 어떤지 궁금하셨죠?”

        2. **보고서 제목에 사용자의 주요 관심사(user_intent)를 명시**하세요.  
           - 예: `# 😴 수면 분석 보고서`

        3. **시간 단위는 초(sec) 대신 '분' 또는 '시간' 단위로 자연스럽게 변환**하세요.  
           - 예: `총 수면 시간: 5시간 30분`, `스트레스 지속 시간: 120분`

        4. **영어 표현은 사용하지 않고**, 일상적이고 친근한 한글 표현을 사용하세요.  
           - 예: `"sedentary" → "앉아 있는 시간"`  
           - `"HRV" → "심박수 변동"`

        5. **정보 제공을 넘어, 격려와 동기를 부여하는 문장을 포함**하세요.  
           - 예: `"오늘도 건강을 챙기려는 시도만으로도 멋진 변화의 시작입니다."`

        6. **"주요 인사이트"는 날짜별로 그룹화하되, 각 날짜별로 수면, 활동량, 스트레스, 심박수 등의 변화를 종합적으로 설명**하세요.  
           - 단순한 나열이 아니라, **하루 전체의 건강 상태를 요약한 종합 설명**이 되도록 하세요.
        
        📌 **보고서 구성 (Markdown 형식)**
        
        ```
        # 🏥 (사용자 질문 의도에 맞는 관심사) 분석 보고서

        ## 🙋 사용자 질문 의도
        (사용자 질문 의도 입력)
        
        ## 📌 요약
        최근 7일 동안 스트레스 수준이 높게 유지되었으며, 수면 시간은 평균 5시간 40분으로 권장 수면보다 부족했습니다.
        
        ## 🔍 주요 인사이트 (날짜별 종합 요약)
        ### 2025-03-26
        활동량이 높았던 하루였지만, 최대 심박수와 스트레스 지수가 함께 급등한 날입니다.  
        18시경의 격렬한 운동 이후 스트레스가 최고치(96)를 기록했고, 수면 시간도 평소보다 짧아 회복이 충분하지 않았을 가능성이 있습니다.

        ### 2025-03-27
        활동량이 급격히 줄어들고 걸음 수가 1,000보 이하로 낮았습니다.  
        스트레스 수준은 여전히 높았고, 전날의 피로가 누적되어 전반적인 활력이 떨어진 하루로 보입니다.

        ### 2025-03-30
        수면 시간이 2시간 반으로 매우 부족했으며, 수면 중 스트레스가 높은 상태로 지속되었습니다.  
        이로 인해 심박수 변동도 불균형하게 나타났고, 전반적인 회복 상태가 매우 좋지 않았던 날입니다.
        
        ## 💡 건강 피드백
        (건강 상태에 대한 따뜻한 피드백과 조언)
        
        ## ✅ 개선 방법
        - (실천 가능한 건강 개선 팁 제시)
        
        ✨ 오늘도 건강을 챙기려는 당신의 노력이 정말 소중합니다.  
        스스로를 응원하며 한 걸음씩 나아가 보세요!
        ```
        """
    )
