import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import time
from fastapi.responses import StreamingResponse
import json
from langgraph.errors import GraphRecursionError
import anthropic
import random
from litellm.types.utils import Choices
from botrun_flow_lang.langgraph_agents.agents.agent_runner import (
    OnNodeStreamEvent,
    agent_runner,
    langgraph_runner,
)
from botrun_flow_lang.langgraph_agents.agents.langgraph_react_agent import (
    create_react_agent_graph,
    get_react_agent_model_name,
)

from botrun_flow_lang.langgraph_agents.agents.search_agent_graph import (
    SearchAgentGraph,
    # graph as search_agent_graph,
)

# from botrun_flow_lang.langgraph_agents.agents.ai_researcher.agent.agent import (
#     graph as ai_researcher_graph,
# )
# from botrun_flow_lang.langgraph_agents.agents.open_deep_research.open_deep_research_graph import (
#     graph as deep_research_graph,
# )
from botrun_flow_lang.utils.langchain_utils import (
    langgraph_event_to_json,
    litellm_msgs_to_langchain_msgs,
)

router = APIRouter(prefix="/langgraph")


class LangGraphRequest(BaseModel):
    graph_name: str
    # todo LangGraph 應該要傳 thread_id，但是因為現在是 cloud run 的架構，所以 thread_id 不一定會讀的到 (auto scale)
    thread_id: Optional[str] = None
    user_input: Optional[str] = None
    messages: List[Dict[str, Any]] = []
    config: Optional[Dict[str, Any]] = None
    stream: bool = False


class LangGraphResponse(BaseModel):
    """
    @param content: 這個是給評測用來評估結果用的
    @param state: 這個是graph的 final state，如果需要額外資訊可以使用
    """

    id: str
    object: str = "chat.completion"
    created: int
    model: str
    content: Optional[str] = None
    state: Optional[Dict[str, Any]] = None


class SupportedGraphsResponse(BaseModel):
    """Response model for listing supported graphs"""

    graphs: List[str]


PERPLEXITY_SEARCH_AGENT = "perplexity_search_agent"
CUSTOM_WEB_RESEARCH_AGENT = "custom_web_research_agent"
LANGGRAPH_REACT_AGENT = "langgraph_react_agent"
DEEP_RESEARCH_AGENT = "deep_research_agent"
SUPPORTED_GRAPHS = {
    PERPLEXITY_SEARCH_AGENT: SearchAgentGraph().graph,
    LANGGRAPH_REACT_AGENT: create_react_agent_graph(),
    # CUSTOM_WEB_RESEARCH_AGENT: ai_researcher_graph,
    # DEEP_RESEARCH_AGENT: deep_research_graph,
}


def get_graph(
    graph_name: str,
    config: Optional[Dict[str, Any]] = None,
    stream: bool = False,
    messages: Optional[List[Dict]] = [],
):
    if graph_name not in SUPPORTED_GRAPHS:
        raise ValueError(f"Unsupported graph from get_graph: {graph_name}")
    graph = SUPPORTED_GRAPHS[graph_name]
    if graph_name == PERPLEXITY_SEARCH_AGENT:
        SearchAgentGraph().set_search_prompt(config.get("search_prompt", ""))
        SearchAgentGraph().set_search_vendor(config.get("search_vendor", "perplexity"))
        SearchAgentGraph().set_related_prompt(config.get("related_question_prompt", ""))
        SearchAgentGraph().set_stream(stream)
        SearchAgentGraph().set_user_prompt_prefix(config.get("user_prompt_prefix", ""))
        SearchAgentGraph().set_domain_filter(config.get("domain_filter", []))
        SearchAgentGraph().set_model_name(
            config.get("model_name", "sonar-reasoning-pro")
        )
    elif graph_name == LANGGRAPH_REACT_AGENT:

        system_prompt = config.get("system_prompt", "")
        if messages:
            for message in messages:
                if message.get("role") == "system":
                    system_prompt = message.get("content", "")
        graph = create_react_agent_graph(
            system_prompt=system_prompt,
            botrun_flow_lang_url=config.get("botrun_flow_lang_url", ""),
            user_id=config.get("user_id", ""),
            model_name=config.get("model_name", ""),
        )
    return graph


def get_init_state(
    graph_name: str,
    user_input: str,
    config: Optional[Dict[str, Any]] = None,
    messages: Optional[List[Dict]] = [],
    enable_prompt_caching: bool = False,
):
    if graph_name == PERPLEXITY_SEARCH_AGENT:
        if len(messages) > 0:
            return {"messages": litellm_msgs_to_langchain_msgs(messages)}
        if config.get("user_prompt_prefix", ""):
            return {
                "messages": [
                    {
                        "role": "user",
                        "content": config.get("user_prompt_prefix", "")
                        + "\n\n"
                        + user_input,
                    }
                ]
            }

        return {"messages": [user_input]}
    elif graph_name == CUSTOM_WEB_RESEARCH_AGENT:
        if len(messages) > 0:
            return {
                "messages": litellm_msgs_to_langchain_msgs(messages),
                "model": config.get("model", "anthropic"),
            }
        return {
            "messages": [user_input],
            "model": config.get("model", "anthropic"),
        }
    elif graph_name == LANGGRAPH_REACT_AGENT:
        new_messages = []
        for message in messages:
            if message.get("role") != "system":
                new_messages.append(message)
        return {
            "messages": litellm_msgs_to_langchain_msgs(
                new_messages, enable_prompt_caching
            )
        }
    elif graph_name == DEEP_RESEARCH_AGENT:
        if len(messages) > 0:
            return {
                "messages": litellm_msgs_to_langchain_msgs(messages),
                "topic": user_input,
            }
        return {
            "messages": [user_input],
            "topic": user_input,
        }
    raise ValueError(f"Unsupported graph from get_init_state: {graph_name}")


def get_content(graph_name: str, state: Dict[str, Any]):
    if graph_name == PERPLEXITY_SEARCH_AGENT:
        return state["messages"][-3].content
    elif graph_name == CUSTOM_WEB_RESEARCH_AGENT:
        content = state["answer"].get("markdown", "")
        content = content.replace("\\n", "\n")
        if state["answer"].get("references", []):
            references = "\n\n參考資料：\n"
            for reference in state["answer"]["references"]:
                references += f"- [{reference['title']}]({reference['url']})\n"
            content += references
        return content
    elif graph_name == DEEP_RESEARCH_AGENT:
        sections = state["sections"]
        sections_str = "\n\n".join(
            f"章節: {section.name}\n"
            f"描述: {section.description}\n"
            f"需要研究: {'是' if section.research else '否'}\n"
            for section in sections
        )
        sections_str = "預計報告結構：\n\n" + sections_str
        return sections_str
    else:
        messages = state["messages"]
        # Find the last human message
        last_human_idx = -1
        for i, msg in enumerate(messages):
            if msg.type == "human":
                last_human_idx = i

        # Combine all AI messages after the last human message
        ai_contents = ""
        for msg in messages[last_human_idx + 1 :]:
            if msg.type == "ai":
                if isinstance(msg.content, list):
                    ai_contents += msg.content[0].get("text", "")
                else:
                    ai_contents += msg.content

        return ai_contents


class LangGraphStreamChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[Choices]


@router.post("/run")
async def run_langgraph(request: LangGraphRequest):
    """
    執行指定的 LangGraph，支援串流和非串流模式

    Args:
        request: 包含 graph_name 和輸入數據的請求

    Returns:
        串流模式: StreamingResponse
        非串流模式: LangGraphResponse
    """
    try:
        graph = get_graph(request.graph_name, request.config, request.stream)
        init_state = get_init_state(
            request.graph_name, request.user_input, request.config
        )

        if request.stream:
            return StreamingResponse(
                langgraph_stream_response(
                    request.thread_id, init_state, graph, request.graph_name
                ),
                media_type="text/event-stream",
            )

        # 非串流模式的原有邏輯
        async for event in agent_runner(request.thread_id, init_state, graph):
            pass

        config = {"configurable": {"thread_id": request.thread_id}}
        state = graph.get_state(config)
        content = get_content(request.graph_name, state.values)
        return LangGraphResponse(
            id=request.thread_id,
            created=int(time.time()),
            model=request.graph_name,
            content=content,
            state=state.values,
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"執行 LangGraph 時發生錯誤: {str(e)}"
        )


async def process_langgraph_request(request: LangGraphRequest, retry=False):
    """
    處理 LangGraph 請求的核心邏輯，包含錯誤處理和重試機制

    Args:
        request: LangGraph 請求
        retry: 是否為重試請求

    Returns:
        LangGraphResponse 或 StreamingResponse
    """
    try:
        graph = get_graph(
            request.graph_name, request.config, request.stream, request.messages
        )
        # user_input_model_name = request.config.get("model_name", "")
        init_state = get_init_state(
            request.graph_name,
            request.user_input,
            request.config,
            request.messages,
            False,
            # get_react_agent_model_name(user_input_model_name).startswith("claude-"),
        )
        thread_id = str(uuid.uuid4())
        if request.thread_id is not None:
            thread_id = request.thread_id

        if request.stream:
            return StreamingResponse(
                langgraph_stream_response(
                    thread_id, init_state, graph, request.graph_name
                ),
                media_type="text/event-stream",
            )

        # 非串流模式的原有邏輯
        async for event in agent_runner(thread_id, init_state, graph):
            pass

        config = {"configurable": {"thread_id": thread_id}}
        state = graph.get_state(config)
        content = get_content(request.graph_name, state.values)
        return LangGraphResponse(
            id=thread_id,
            created=int(time.time()),
            model=request.graph_name,
            content=content,
            state=state.values,
        )
    except anthropic.RateLimitError as e:
        # 如果是重試之後仍然發生 RateLimitError，則拋出異常
        if retry:
            import traceback

            traceback.print_exc()
            print(f"Retry failed with Anthropic RateLimitError: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"執行 LangGraph 時發生超過速率限制: {str(e)}"
            )
        # 第一次發生 RateLimitError，記錄並重試
        print(f"Rate limit error occurred: {str(e)}")
        # 隨機等待 7-20 秒
        retry_delay = random.randint(7, 20)
        print(f"Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)
        print("Retrying after rate limit error...")
        # 重試
        return await process_langgraph_request(request, retry=True)
    except GraphRecursionError as e:
        raise HTTPException(
            status_code=500, detail=f"執行 LangGraph 時發生超過最大遞迴深度: {str(e)}"
        )
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"執行 LangGraph 時發生錯誤: {str(e)}"
        )


@router.post("/invoke")
async def invoke(request: LangGraphRequest):
    """
    執行指定的 LangGraph，支援串流和非串流模式

    Args:
        request: 包含 graph_name 和輸入數據的請求

    Returns:
        串流模式: StreamingResponse
        非串流模式: LangGraphResponse
    """
    # 執行請求處理
    return await process_langgraph_request(request)


async def langgraph_stream_response(
    thread_id: str, init_state: Dict, graph: Any, model: str
):
    try:
        async for event in langgraph_runner(thread_id, init_state, graph):
            yield f"data: {langgraph_event_to_json(event)}\n\n"
        #     if isinstance(event, OnNodeStreamEvent):
        #         chunk = LangGraphStreamChunk(
        #             id=thread_id,
        #             created=int(time.time()),
        #             model=model,
        #             choices=[
        #                 Choice(
        #                     message=Message(content=event.chunk),
        #                     delta=Delta(content=event.chunk),
        #                 )
        #             ],
        #             finish_reason=None,
        #         )
        #         yield f"data: {chunk.model_dump_json()}\n\n"
        #     await asyncio.sleep(0.1)  # 避免過快發送

        # # 發送結束信號
        # chunk = LangGraphStreamChunk(
        #     id=thread_id,
        #     created=int(time.time()),
        #     model=model,
        #     choices=[
        #         Choice(
        #             message=Message(content=""),
        #             delta=Delta(content=""),
        #             finish_reason="stop",
        #         )
        #     ],
        # )
        # yield f"data: {chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        import traceback

        traceback.print_exc()
        error_response = {"error": str(e)}
        yield f"data: {json.dumps(error_response)}\n\n"


@router.get("/list", response_model=SupportedGraphsResponse)
async def list_supported_graphs():
    """
    列出所有支援的 LangGraph names

    Returns:
        包含所有支援的 graph names 的列表
    """
    return SupportedGraphsResponse(graphs=list(SUPPORTED_GRAPHS.keys()))
