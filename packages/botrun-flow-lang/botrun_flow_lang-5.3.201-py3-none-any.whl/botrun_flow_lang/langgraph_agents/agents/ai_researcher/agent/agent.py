"""
This is the main entry point for the AI.
It defines the workflow graph and the entry point for the agent.
"""

from typing import Annotated, TypedDict, List
import operator
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Send
from langchain_core.messages import HumanMessage

from botrun_flow_lang.langgraph_agents.agents.ai_researcher.agent.extract import (
    extract_node,
)
from botrun_flow_lang.langgraph_agents.agents.ai_researcher.agent.search import (
    search_node,
)
from botrun_flow_lang.langgraph_agents.agents.ai_researcher.agent.state import (
    AgentState,
    SearchAndExtractState,
)
from botrun_flow_lang.langgraph_agents.agents.ai_researcher.agent.steps import (
    steps_node,
)
from botrun_flow_lang.langgraph_agents.agents.ai_researcher.agent.summarize import (
    summarize_node,
)


def map_to_searches(state: AgentState):
    """Map state to parallel search operations"""
    if not state.get("steps", None):
        return END

    pending_steps = [
        step
        for step in state["steps"]
        if step["status"] == "pending" and step["type"] == "search"
    ]
    # 取得使用者原始問題
    last_human_message = next(
        (msg for msg in state["messages"] if isinstance(msg, HumanMessage)), None
    )
    original_query = last_human_message.content if last_human_message else ""

    return [
        Send(
            "search_node",
            SearchAndExtractState(
                current_step=step,
                keywords="",
                search_result=[],
                original_query=original_query,
                all_steps=state["steps"],
            ),
        )
        for step in pending_steps
    ]


def map_to_extracts(state: AgentState):
    """Map state to parallel extract operations"""
    if not state.get("steps", None):
        return END
    pending_steps = [
        step
        for step in state["steps"]
        if step["status"] == "pending" and step["type"] == "search"
    ]

    return [
        Send(
            "extract_node",
            SearchAndExtractState(
                current_step=step,
                keywords="",
                search_result=[],
                original_query="",
                all_steps=[],
            ),
        )
        for step in pending_steps
    ]


def collect_search_results(state: AgentState):
    """Collect search results"""
    return state


# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("steps_node", steps_node)
workflow.add_node("search_node", search_node)
workflow.add_node("collect_search_results", collect_search_results)  # 新增收集節點

workflow.add_node("extract_node", extract_node)
workflow.add_node("summarize_node", summarize_node)

# Set entry point
workflow.set_entry_point("steps_node")

# Add edges for parallel processing
workflow.add_conditional_edges("steps_node", map_to_searches, ["search_node", END])
workflow.add_edge("search_node", "collect_search_results")
workflow.add_conditional_edges(
    "collect_search_results", map_to_extracts, ["extract_node", END]
)

# Connect search to extract
# workflow.add_edge("search_node", "extract_node")

# Connect extract to summarize
workflow.add_edge("extract_node", "summarize_node")

# Final edge
workflow.add_edge("summarize_node", END)

# Initialize memory and compile
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)
