from typing import Annotated, List, TypedDict, Literal
from pydantic import BaseModel, Field
import operator


class ResearchPlan(BaseModel):
    research_plan: str = Field(
        description="研究方法與策略。",
    )
    report_structure: str = Field(
        description="報告架構。",
    )


class Section(BaseModel):
    name: str = Field(
        description="報告裡章節的名稱。",
    )
    description: str = Field(
        description="預計要產出報告裡章節的內容的描述。",
    )
    research: bool = Field(description="是否需要為報告的這個章節進行網路研究。")
    content: str = Field(description="報告裡章節的內容。")


class Sections(BaseModel):
    sections: List[Section] = Field(
        description="報告裡的章節列表。",
    )


class SearchQuery(BaseModel):
    search_query: str = Field(None, description="可以用來搜尋的關鍵字。")


class Queries(BaseModel):
    queries: List[SearchQuery] = Field(
        description="可以用來搜尋的關鍵字列表，是一個 List。",
    )


class Feedback(BaseModel):
    grade: Literal["pass", "fail"] = Field(
        description="評估結果，表示是否符合要求 ('pass') 或需要修改 ('fail')。"
    )
    follow_up_queries: List[SearchQuery] = Field(
        description="可以繼續搜尋的關鍵字列表。",
    )


class ReportStateInput(TypedDict):
    topic: str  # Report topic


class ReportStateOutput(TypedDict):
    final_report: str  # Final report


class ReportState(TypedDict):
    topic: str  # Report topic
    sections: list[Section]  # List of report sections
    completed_sections: Annotated[list, operator.add]  # Send() API key
    report_sections_from_research: (
        str  # String of any completed sections from research to write final sections
    )
    final_report: str  # Final report


class SectionState(TypedDict):
    section: Section  # Report section
    search_iterations: int  # Number of search iterations done
    search_queries: list[SearchQuery]  # List of search queries
    source_str: str  # String of formatted source content from web search
    feedback_on_report_plan: str  # Feedback on the report plan
    report_sections_from_research: (
        str  # String of any completed sections from research to write final sections
    )
    completed_sections: list[
        Section
    ]  # Final key we duplicate in outer state for Send() API


class SectionOutputState(TypedDict):
    completed_sections: list[
        Section
    ]  # Final key we duplicate in outer state for Send() API
