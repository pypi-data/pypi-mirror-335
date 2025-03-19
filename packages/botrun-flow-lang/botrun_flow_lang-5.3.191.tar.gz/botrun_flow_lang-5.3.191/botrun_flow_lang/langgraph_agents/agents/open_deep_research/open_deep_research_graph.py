from datetime import datetime
from typing import Literal

from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

# from langchain_groq import ChatGroq

from langgraph.constants import Send
from langgraph.graph import START, END, StateGraph
from langgraph.types import interrupt, Command
import pytz

from botrun_flow_lang.langgraph_agents.agents.open_deep_research.state import (
    ReportStateInput,
    ReportStateOutput,
    ResearchPlan,
    Sections,
    ReportState,
    SectionState,
    SectionOutputState,
    Queries,
    Feedback,
)
from botrun_flow_lang.langgraph_agents.agents.open_deep_research.prompts import (
    research_and_report_planner_instructions,
    report_planner_query_writer_instructions,
    report_planner_instructions,
    query_writer_instructions,
    section_writer_instructions,
    final_section_writer_instructions,
    section_grader_instructions,
)
from botrun_flow_lang.langgraph_agents.agents.open_deep_research.configuration import (
    Configuration,
)
from botrun_flow_lang.langgraph_agents.agents.open_deep_research.utils import (
    tavily_search_async,
    deduplicate_and_format_sources,
    format_sections,
    perplexity_search,
)

# Set writer model
writer_model = ChatAnthropic(model=Configuration.writer_model, temperature=0)


def current_time():
    try:
        local_tz = pytz.timezone("Asia/Taipei")
        local_time = datetime.now(local_tz)
        print("current_time============>", local_time.strftime("%Y-%m-%d %H:%M %Z"))
        return local_time.strftime("%Y-%m-%d %H:%M %Z")
    except Exception as e:
        return f"Error: {e}"


# Nodes
async def generate_report_plan(state: ReportState, config: RunnableConfig):
    """Generate the report plan"""

    # Inputs
    topic = state["topic"]
    feedback = state.get("feedback_on_report_plan", None)

    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    research_plan = configurable.research_plan
    # report_structure = configurable.report_structure
    number_of_queries = configurable.number_of_queries

    # Convert JSON object to string if necessary
    # if isinstance(report_structure, dict):
    # report_structure = str(report_structure)

    # Set the planner provider
    if isinstance(configurable.planner_provider, str):
        planner_provider = configurable.planner_provider
    else:
        planner_provider = configurable.planner_provider.value

    # Set the planner model
    if planner_provider == "gemini":
        planner_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-thinking-exp")
    elif planner_provider == "openai":
        planner_llm = ChatOpenAI(
            model=configurable.planner_model, reasoning_effort="high"
        )
    # elif planner_provider == "groq":
    #     planner_llm = ChatGroq(model=configurable.planner_model)
    else:
        raise ValueError(f"Unsupported search API: {configurable.search_api}")

    research_plan_llm = planner_llm.with_structured_output(ResearchPlan)
    research_plan_instructions_query = research_and_report_planner_instructions.format(
        topic=topic,
        research_plan=research_plan,
    )
    research_plan_results = research_plan_llm.invoke(
        [SystemMessage(content=research_plan_instructions_query)]
        + [
            HumanMessage(
                content="產生研究方法與策略以及報告架構。您的回應必須包含一個 'research_plan' 欄位，其中包含一個研究方法與策略，以及一個 'report_structure' 欄位，其中包含一個報告架構。"
            )
        ]
    )
    generated_research_plan = research_plan_results.research_plan
    generated_report_structure = research_plan_results.report_structure

    # Generate search query
    structured_llm = writer_model.with_structured_output(Queries)

    # Format system instructions
    system_instructions_query = report_planner_query_writer_instructions.format(
        topic=topic,
        research_plan=generated_research_plan,
        report_organization=generated_report_structure,
        number_of_queries=number_of_queries,
        current_time=current_time(),
    )

    # Generate queries
    results = structured_llm.invoke(
        [SystemMessage(content=system_instructions_query)]
        + [
            HumanMessage(
                content="產生要去搜尋的關鍵字，這些關鍵字將幫助規劃報告的章節。"
            )
        ]
    )

    # Web search
    query_list = [query.search_query for query in results.queries]

    # Handle both cases for search_api:
    # 1. When selected in Studio UI -> returns a string (e.g. "tavily")
    # 2. When using default -> returns an Enum (e.g. SearchAPI.TAVILY)
    if isinstance(configurable.search_api, str):
        search_api = configurable.search_api
    else:
        search_api = configurable.search_api.value

    # Search the web
    # if search_api == "tavily":
    #     search_results = await tavily_search_async(query_list)
    #     print(
    #         f"[generate_report_plan] tavily_search_results==========>: {search_results}"
    #     )
    #     source_str = deduplicate_and_format_sources(
    #         search_results, max_tokens_per_source=1000, include_raw_content=False
    #     )
    # elif search_api == "perplexity":
    #     search_results = perplexity_search(query_list)
    #     source_str = deduplicate_and_format_sources(
    #         search_results, max_tokens_per_source=1000, include_raw_content=False
    #     )
    # else:
    #     raise ValueError(f"Unsupported search API: {configurable.search_api}")

    # Format system instructions
    system_instructions_sections = report_planner_instructions.format(
        topic=topic,
        report_organization=generated_report_structure,
        # context=source_str,
        feedback=feedback,
        current_time=current_time(),
    )

    # Generate sections
    structured_llm = planner_llm.with_structured_output(Sections)
    report_sections = structured_llm.invoke(
        [SystemMessage(content=system_instructions_sections)]
        + [
            HumanMessage(
                content="產生報告的章節。您的回應必須包含一個 'sections' 欄位，其中包含一個章節列表。每個章節必須具有：name、description、plan、research 和 content 欄位。"
            )
        ]
    )

    # Get sections
    sections = report_sections.sections

    return {"sections": sections}


def human_feedback(
    state: ReportState, config: RunnableConfig
) -> Command[Literal["generate_report_plan", "build_section_with_web_research"]]:
    """Get feedback on the report plan"""

    # Get sections
    sections = state["sections"]
    sections_str = "\n\n".join(
        f"章節: {section.name}\n" f"描述: {section.description}\n"
        # f"內容: {section.content}\n"
        f"需要研究: {'是' if section.research else '否'}\n"
        for section in sections
    )

    # Get feedback on the report plan from interrupt

    feedback = interrupt(
        f"請提供對以下報告計劃的反饋。 \n\n{sections_str}\n\n 報告計劃是否滿足您的需求？ 如果報告計劃符合您的需求，請通過傳遞 'true' 來批准報告計劃，或者提供反饋以重新生成報告計劃："
    )
    print(f"feedback==========>: {feedback}")

    # If the user approves the report plan, kick off section writing
    # if isinstance(feedback, bool) and feedback is True:
    if isinstance(feedback, bool):
        # Treat this as approve and kick off section writing
        return Command(
            goto=[
                Send(
                    "build_section_with_web_research",
                    {"section": s, "search_iterations": 0},
                )
                for s in sections
                if s.research
            ]
        )

    # If the user provides feedback, regenerate the report plan
    elif isinstance(feedback, str):
        # treat this as feedback
        print(f"feedback is a string==========>: {feedback}")
        return Command(
            goto="generate_report_plan", update={"feedback_on_report_plan": feedback}
        )
    else:
        raise TypeError(f"Interrupt value of type {type(feedback)} is not supported.")


def generate_queries(state: SectionState, config: RunnableConfig):
    """Generate search queries for a report section"""

    # Get state
    section = state["section"]

    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    number_of_queries = configurable.number_of_queries

    # Generate queries
    structured_llm = writer_model.with_structured_output(Queries)

    # Format system instructions
    system_instructions = query_writer_instructions.format(
        section_topic=section.name,
        section_description=section.description,
        number_of_queries=number_of_queries,
        current_time=current_time(),
    )

    # Generate queries
    queries = structured_llm.invoke(
        [SystemMessage(content=system_instructions)]
        + [HumanMessage(content="Generate search queries on the provided topic.")]
    )

    return {"search_queries": queries.queries}


async def search_web(state: SectionState, config: RunnableConfig):
    """Search the web for each query, then return a list of raw sources and a formatted string of sources."""

    # Get state
    search_queries = state["search_queries"]

    # Get configuration
    configurable = Configuration.from_runnable_config(config)

    # Web search
    query_list = [query.search_query for query in search_queries]

    # Handle both cases for search_api:
    # 1. When selected in Studio UI -> returns a string (e.g. "tavily")
    # 2. When using default -> returns an Enum (e.g. SearchAPI.TAVILY)
    if isinstance(configurable.search_api, str):
        search_api = configurable.search_api
    else:
        search_api = configurable.search_api.value

    # Search the web
    if search_api == "tavily":
        print(f"[search_web] tavily_search_queries==========>: {query_list}")
        search_results = await tavily_search_async(query_list)
        source_str = deduplicate_and_format_sources(
            search_results, max_tokens_per_source=5000, include_raw_content=True
        )
    elif search_api == "perplexity":
        search_results = perplexity_search(query_list)
        source_str = deduplicate_and_format_sources(
            search_results, max_tokens_per_source=5000, include_raw_content=False
        )
    else:
        raise ValueError(f"Unsupported search API: {configurable.search_api}")

    return {
        "source_str": source_str,
        "search_iterations": state["search_iterations"] + 1,
    }


def write_section(
    state: SectionState, config: RunnableConfig
) -> Command[Literal[END, "search_web"]]:
    """Write a section of the report"""

    # Get state
    section = state["section"]
    source_str = state["source_str"]

    # Get configuration
    configurable = Configuration.from_runnable_config(config)

    # Format system instructions
    system_instructions = section_writer_instructions.format(
        section_topic=section.name,
        section_description=section.description,
        context=source_str,
        section_content=section.content,
        current_time=current_time(),
    )

    # Generate section
    section_content = writer_model.invoke(
        [SystemMessage(content=system_instructions)]
        + [
            HumanMessage(
                content="Generate a report section based on the provided sources."
            )
        ]
    )

    # Write content to the section object
    section.content = section_content.content

    # Grade prompt
    section_grader_instructions_formatted = section_grader_instructions.format(
        section_topic=section.name,
        section_description=section.description,
        section=section.content,
        current_time=current_time(),
    )

    # Feedback
    structured_llm = writer_model.with_structured_output(Feedback)
    feedback = structured_llm.invoke(
        [SystemMessage(content=section_grader_instructions_formatted)]
        + [
            HumanMessage(
                content="Grade the report and consider follow-up questions for missing information:"
            )
        ]
    )

    if (
        feedback.grade == "pass"
        or state["search_iterations"] >= configurable.max_search_depth
    ):
        # Publish the section to completed sections
        return Command(update={"completed_sections": [section]}, goto=END)
    else:
        # Update the existing section with new content and update search queries
        return Command(
            update={"search_queries": feedback.follow_up_queries, "section": section},
            goto="search_web",
        )


def write_final_sections(state: SectionState):
    """Write final sections of the report, which do not require web search and use the completed sections as context"""

    # Get state
    section = state["section"]
    completed_report_sections = state["report_sections_from_research"]

    # Format system instructions
    system_instructions = final_section_writer_instructions.format(
        section_topic=section.name,
        section_description=section.description,
        context=completed_report_sections,
    )

    # Generate section
    section_content = writer_model.invoke(
        [SystemMessage(content=system_instructions)]
        + [
            HumanMessage(
                content="Generate a report section based on the provided sources."
            )
        ]
    )

    # Write content to section
    section.content = section_content.content

    # Write the updated section to completed sections
    return {"completed_sections": [section]}


def gather_completed_sections(state: ReportState):
    """Gather completed sections from research and format them as context for writing the final sections"""

    # List of completed sections
    completed_sections = state["completed_sections"]

    # Format completed section to str to use as context for final sections
    completed_report_sections = format_sections(completed_sections)

    return {"report_sections_from_research": completed_report_sections}


def initiate_final_section_writing(state: ReportState):
    """Write any final sections using the Send API to parallelize the process"""

    # Kick off section writing in parallel via Send() API for any sections that do not require research
    return [
        Send(
            "write_final_sections",
            {
                "section": s,
                "report_sections_from_research": state["report_sections_from_research"],
            },
        )
        for s in state["sections"]
        if not s.research
    ]


def compile_final_report(state: ReportState):
    """Compile the final report"""

    # Get sections
    sections = state["sections"]
    completed_sections = {s.name: s.content for s in state["completed_sections"]}

    # Update sections with completed content while maintaining original order
    for section in sections:
        section.content = completed_sections[section.name]

    # Compile final report
    all_sections = "\n\n".join([s.content for s in sections])

    return {"final_report": all_sections}


# Report section sub-graph --

# Add nodes
section_builder = StateGraph(SectionState, output=SectionOutputState)
section_builder.add_node("generate_queries", generate_queries)
section_builder.add_node("search_web", search_web)
section_builder.add_node("write_section", write_section)

# Add edges
section_builder.add_edge(START, "generate_queries")
section_builder.add_edge("generate_queries", "search_web")
section_builder.add_edge("search_web", "write_section")

# Outer graph --

# Add nodes
builder = StateGraph(
    ReportState,
    input=ReportStateInput,
    output=ReportStateOutput,
    config_schema=Configuration,
)
builder.add_node("generate_report_plan", generate_report_plan)
builder.add_node("human_feedback", human_feedback)
builder.add_node("build_section_with_web_research", section_builder.compile())
builder.add_node("gather_completed_sections", gather_completed_sections)
builder.add_node("write_final_sections", write_final_sections)
builder.add_node("compile_final_report", compile_final_report)

# Add edges
builder.add_edge(START, "generate_report_plan")
builder.add_edge("generate_report_plan", "human_feedback")
builder.add_edge("build_section_with_web_research", "gather_completed_sections")
builder.add_conditional_edges(
    "gather_completed_sections",
    initiate_final_section_writing,
    ["write_final_sections"],
)
builder.add_edge("write_final_sections", "compile_final_report")
builder.add_edge("compile_final_report", END)

graph = builder.compile(checkpointer=MemorySaver())
