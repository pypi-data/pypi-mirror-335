"""
This is the state definition for the AI.
It defines the state of the agent and the state of the conversation.
"""

from typing import Annotated, List, Optional
from typing_extensions import TypedDict
import operator
from langgraph.graph import MessagesState


class Step(TypedDict):
    """
    Represents a step taken in the research process.
    """

    id: str
    description: str
    status: str
    type: str
    search_result: Optional[str]
    result: Optional[str]
    updates: Optional[List[str]]


def merge_step_lists(steps1: List[Step], steps2: List[Step]) -> List[Step]:
    """
    Merge two lists of steps, updating existing steps and adding new ones.
    When steps have the same id, use the newer version.
    """
    result = steps1.copy()

    # 更新或添加新的步驟
    for new_step in steps2:
        # 尋找相同 id 的步驟
        for i, existing_step in enumerate(result):
            if existing_step["id"] == new_step["id"]:
                # 找到相同 id，更新該步驟
                result[i] = new_step
                break
        else:
            # 沒找到相同 id，添加新步驟
            result.append(new_step)

    return result


class AgentState(MessagesState):
    """
    This is the state of the agent.
    It is a subclass of the MessagesState class from langgraph.
    """

    model: str = "openai"
    steps: Annotated[List[Step], merge_step_lists]
    answer: Optional[str]
    related_questions: Optional[List[str]]


class SearchAndExtractState(TypedDict):
    """State for search and extract operations"""

    # 當前步驟相關
    current_step: dict
    search_result: list

    # 整體狀態相關
    original_query: str  # 使用者原始問題
    all_steps: list  # 所有子任務列表
