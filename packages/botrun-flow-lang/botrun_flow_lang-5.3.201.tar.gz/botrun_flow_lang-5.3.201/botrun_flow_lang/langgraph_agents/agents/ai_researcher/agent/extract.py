"""
The extract node is responsible for extracting information from a tavily search.
"""

import json
import time
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI

from botrun_flow_lang.langgraph_agents.agents.ai_researcher.agent.model import get_model
from botrun_flow_lang.langgraph_agents.agents.ai_researcher.agent.state import (
    AgentState,
    SearchAndExtractState,
)


async def extract_node(state: SearchAndExtractState, config: RunnableConfig):
    """
    Extract information from search results and update overall state.
    """
    system_message = f"""
    妳是臺灣人，回答要用臺灣繁體中文正式用語，需要的時候也可以用英文，可以親切、但不能隨便輕浮。在使用者合理的要求下請盡量配合他的需求，不要隨便拒絕

    這個步驟剛剛被執行，裡面包含有搜尋的結果：{json.dumps(state["current_step"], ensure_ascii=False)}

    請妳只總結搜尋的結果，使用者會想要找貼補助相關的資訊，因此要請盡可能的從搜尋的結果中找到相關的資訊，包含有：
    - 津貼補助項目名稱：瞭解具體的補助計畫名稱。
    - 主辦單位：確認負責該補助計畫的政府部門。
    - 申請對象與資格：明確申請資格，如收入標準、居住地等。
    - 補助金額與費用計算：瞭解補助金額範圍及計算方式。
    - 申請期限：確認申請的開始和截止日期。
    - 申請流程：瞭解申請步驟，包括線上申請或紙本提交等。
    - 準備資料：列出所需的申請文件，如身份證明、收入證明等。
    - 受理申請單位：確認受理申請的具體單位名稱及地址。
    - 資料來源網址：民眾才可以知道是引用哪裡的資料

    如果有多個相關的補助津貼，就都條列出來。

    不要包含任何額外的資訊。妳需要找的資訊都在搜尋的結果裡。

    不要回答使用者的查詢。只要總結搜尋的結果。

    使用markdown格式，並且把參考來源放在句子裡面，並且把連結放在最後面。
    像這樣：
    這是一個句子，裡面有參考來源 [來源1][1] 和另一個參考來源 [來源2][2]。
    [1]: http://example.com/source1 "Title of Source 1"
    [2]: http://example.com/source2 "Title of Source 2"
    """
    # 因為 Claude 的速度比 gemini 快，所以先試試看 Claude
    # 但是 Claude 能夠處理的資料量比較少，所以如果 Claude 失敗，再試試看 gemini
    response = None
    try:
        model = ChatAnthropic(
            temperature=0,
            model="claude-3-5-sonnet-latest",
            max_retries=1,
            default_request_timeout=60,
            disable_streaming=True,
        )
        response = await model.ainvoke(
            [HumanMessage(content=system_message)],
            config,
        )
    except Exception as e:
        print(f"extract node Anthropic error: {e}")
    if response is None:
        try:
            model = ChatGoogleGenerativeAI(
                temperature=0,
                model="gemini-1.5-pro",
                disable_streaming=True,
            )
            response = await model.ainvoke(
                [HumanMessage(content=system_message)],
                config,
            )
        except Exception as e:
            raise f"extract node Google Generative AI error: {e}"

    # 更新當前步驟的結果
    state["current_step"]["result"] = response.content
    state["current_step"]["search_result"] = None
    state["current_step"]["status"] = "complete"
    state["current_step"]["updates"] = [
        *state["current_step"].get("updates", []),
        "Done.",
    ]

    # 只回傳更新的步驟資訊
    return {"steps": [state["current_step"]]}  # 只回傳已更新的步驟
