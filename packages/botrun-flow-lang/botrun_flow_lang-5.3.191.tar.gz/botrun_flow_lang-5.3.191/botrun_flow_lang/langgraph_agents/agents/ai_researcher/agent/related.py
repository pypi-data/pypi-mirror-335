from copy import deepcopy
import json
from datetime import datetime
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

# from copilotkit.langchain import copilotkit_customize_config

from botrun_flow_lang.langgraph_agents.agents.ai_researcher.agent.state import (
    AgentState,
)
from botrun_flow_lang.langgraph_agents.agents.search_agent_graph import format_dates


class RelatedQuestionsInstructions(BaseModel):
    """Model for related questions output"""

    related_questions: list[str]


# todo 這個目前改到一半，還沒有做完
# 需要讓 custom research agent 可以產出 related questions
async def related_node(state: AgentState, config: RunnableConfig):
    """
    The related node is responsible for generating related questions.
    """

    # config = copilotkit_customize_config(
    #     config,
    #     emit_intermediate_state=[
    #         {
    #             "state_key": "related_questions",
    #             "tool": "RelatedQuestionsInstructions",
    #         }
    #     ],
    # )

    steps = deepcopy(state["steps"])
    for step in steps:
        step["search_result"] = None

    now = datetime.now()
    dates = format_dates(now)
    western_date = dates["western_date"]
    taiwan_date = dates["taiwan_date"]

    system_message = f"""
現在的西元時間：{western_date}
現在的民國時間：{taiwan_date}

## 系統狀態信息
這個系統已經完成了一連串的研究步驟，來回答使用者的問題。

使用者的問題：
<使用者問題>
{state["messages"][0].content}
</使用者問題>

系統的研究結果：
<所有研究結果>
{json.dumps(steps, ensure_ascii=False)}
</所有研究結果>

你是一個專業的助手，請根據使用者的原始問題以及之前的回答內容，提供 3-5 個相關的後續問題建議。
這些問題應該：
1. 與原始問題和回答內容相關
2. 能夠幫助使用者更深入了解相關的補助或福利
3. 涵蓋不同面向，但都要與福利補助有關
4. 使用繁體中文提問
5. 每個問題都要簡潔明瞭，不超過 30 個字

請使用 RelatedQuestionsInstructions 工具來提供建議的問題清單。
"""

    response = None
    try:
        chat_model = ChatAnthropic(temperature=0.7, model="claude-3-5-sonnet-latest")
        response = await chat_model.bind_tools(
            [RelatedQuestionsInstructions], tool_choice="RelatedQuestionsInstructions"
        ).ainvoke(
            [
                HumanMessage(content=system_message),
            ],
            config,
        )
    except Exception as e:
        print(f"related node Anthropic error: {e}")

    if response is None:
        try:
            chat_model = ChatGoogleGenerativeAI(temperature=0.7, model="gemini-1.5-pro")
            response = await chat_model.bind_tools(
                [RelatedQuestionsInstructions],
                tool_choice="RelatedQuestionsInstructions",
            ).ainvoke([HumanMessage(content=system_message)], config)
        except Exception as e:
            raise f"related node Google Generative AI error: {e}"

    return {
        "related_questions": response.tool_calls[0]["args"]["related_questions"],
    }
