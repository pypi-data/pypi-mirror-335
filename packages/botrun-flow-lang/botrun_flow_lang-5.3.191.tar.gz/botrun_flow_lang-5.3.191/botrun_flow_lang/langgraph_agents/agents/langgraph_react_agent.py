# First we initialize the model we want to use.
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_aws import ChatBedrockConverse
from litellm import image_generation
import random
import os
from langchain_anthropic import convert_to_anthropic_tool
from langchain_core.messages import SystemMessage


from botrun_flow_lang.langgraph_agents.agents.util.img_util import analyze_imgs
from botrun_flow_lang.langgraph_agents.agents.util.local_files import (
    upload_and_get_tmp_public_url,
)
from botrun_flow_lang.langgraph_agents.agents.util.pdf_analyzer import analyze_pdf
from botrun_flow_lang.langgraph_agents.agents.util.perplexity_search import (
    respond_with_perplexity_search,
)
from botrun_flow_lang.models.nodes.utils import scrape_single_url
from botrun_flow_lang.models.nodes.vertex_ai_search_node import VertexAISearch
from datetime import datetime
from botrun_flow_lang.langgraph_agents.agents.search_agent_graph import format_dates
from langgraph.checkpoint.memory import MemorySaver
import pytz
import asyncio
import os
import json
from botrun_flow_lang.langgraph_agents.agents.util.plotly_util import (
    generate_plotly_files,
)
from botrun_flow_lang.langgraph_agents.agents.util.mermaid_util import (
    generate_mermaid_files,
)
from botrun_flow_lang.langgraph_agents.agents.util.html_util import (
    generate_html_file,
)
from botrun_flow_lang.langgraph_agents.agents.util.model_utils import (
    RotatingChatAnthropic,
)
from botrun_flow_lang.langgraph_agents.agents.checkpointer.firestore_checkpointer import (
    FirestoreCheckpointer,
)
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

import boto3
from langchain_aws import ChatBedrock
from dotenv import load_dotenv

load_dotenv()

# Load Anthropic API keys from environment
# anthropic_api_keys_str = os.getenv("ANTHROPIC_API_KEYS", "")
# anthropic_api_keys = [
#     key.strip() for key in anthropic_api_keys_str.split(",") if key.strip()
# ]

# Initialize the model with key rotation if multiple keys are available
# if anthropic_api_keys:
#     model = RotatingChatAnthropic(
#         model_name="claude-3-7-sonnet-latest",
#         keys=anthropic_api_keys,
#         temperature=0,
#         max_tokens=8192,
#     )
# 建立 AWS Session
# session = boto3.Session(
#     aws_access_key_id="",
#     aws_secret_access_key="",
#     region_name="us-west-2",
# )


# # 使用該 Session 初始化 Bedrock 客戶端
# bedrock_runtime = session.client(
#     service_name="bedrock-runtime",
# )
# model = ChatBedrockConverse(
#     model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
#     client=bedrock_runtime,
#     temperature=0,
#     max_tokens=8192,
# )
# else:
# Fallback to traditional initialization if no keys are specified
def get_react_agent_model_name(model_name: str = ""):
    final_model_name = model_name
    if final_model_name == "":
        final_model_name = "claude-3-7-sonnet-latest"
    return final_model_name


def get_react_agent_model(model_name: str = ""):
    final_model_name = get_react_agent_model_name(model_name)
    if final_model_name.startswith("gemini-"):
        model = ChatGoogleGenerativeAI(model=final_model_name, temperature=0)
    elif final_model_name.startswith("claude-"):
        anthropic_api_keys_str = os.getenv("ANTHROPIC_API_KEYS", "")
        anthropic_api_keys = [
            key.strip() for key in anthropic_api_keys_str.split(",") if key.strip()
        ]
        if anthropic_api_keys:
            model = RotatingChatAnthropic(
                model_name=final_model_name,
                keys=anthropic_api_keys,
                temperature=0,
                max_tokens=8192,
            )
        else:
            model = ChatAnthropic(
                model=final_model_name,
                temperature=0,
                max_tokens=8192,
                # model_kwargs={
                #     "extra_headers": {"anthropic-beta": "token-efficient-tools-2025-02-19"}
                # },
            )
    return model


# model = ChatOpenAI(model="gpt-4o", temperature=0)
# model = ChatGoogleGenerativeAI(model="gemini-2.0-pro-exp-02-05", temperature=0)
# model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)


# For this tutorial we will use custom tool that returns pre-defined values for weather in two cities (NYC & SF)

from typing import Literal

from langchain_core.tools import tool


@tool
def scrape(url: str):
    """
    Use this to scrape the web.
    as it provides better results for video content.

    Args:
        url: the url to scrape
    """
    try:
        return asyncio.run(scrape_single_url(url))
    except Exception as e:
        return f"Error: {e}"


@tool
def current_date_time():
    """
    Use this to get the current date and time in local timezone.

    Important: You MUST call this current_date_time function when:
    1. User's query contains time-related words such as:
       - 今天、現在、目前
       - 本週、這週、下週
       - 本月、這個月、上個月
       - 今年、去年、明年
       - 最近、近期
       - 未來、將來
       - 過去、以前
    2. User asks about current events or latest information
    3. User wants to know time-sensitive information
    4. Queries involving relative time expressions

    Examples of when to use current_date_time:
    - "今天的天氣如何？"
    - "本月的股市表現"
    - "最近有什麼新聞？"
    - "去年到現在的經濟成長"
    - "未來一週的活動預告"
    - "這個月的銷售數據"

    Returns:
        str: Current date and time in format "YYYY-MM-DD HH:MM Asia/Taipei"
    """
    try:
        local_tz = pytz.timezone("Asia/Taipei")
        local_time = datetime.now(local_tz)
        print(
            "current_date_time============>", local_time.strftime("%Y-%m-%d %H:%M %Z")
        )
        return local_time.strftime("%Y-%m-%d %H:%M %Z")
    except Exception as e:
        return f"Error: {e}"


@tool
def compare_date_time(user_specified_date_time: str, current_date_time: str):
    """
    比較使用者指定的日期時間與當前時間，判斷是過去還是未來。

    Important: 當使用者想要比較特定日期時間與現在的關係時，請使用此函數。
    適用情境包括：
    1. 使用者提供特定日期時間，想知道與現在的相對關係
    2. 使用者詢問某個日期時間是否已經過去或尚未到來
    3. 使用者需要判斷某個時間點相對於現在的狀態

    Args:
        user_specified_date_time: 使用者指定的日期時間，格式必須為 "YYYY-MM-DD HH:MM Asia/Taipei"
                      例如："2023-12-31 23:59 Asia/Taipei"
        current_date_time: 當前日期時間，通常由 current_date_time() 函數提供
                         格式同樣為 "YYYY-MM-DD HH:MM Asia/Taipei"

    Examples of when to use compare_date_time:
    - "2025-01-01 00:00 是過去還是未來？"
    - "判斷 2023-05-20 15:30 與現在的關係"
    - "2024-12-25 18:00 這個時間點已經過去了嗎？"
    - "比較 2022-10-01 08:00 和現在時間"

    Returns:
        str: 比較結果，格式為 "使用者指定的時間是{過去/未來}"
    """
    try:
        # 解析使用者提供的日期時間
        user_dt = datetime.strptime(
            user_specified_date_time.split(" Asia/Taipei")[0], "%Y-%m-%d %H:%M"
        )
        user_dt = pytz.timezone("Asia/Taipei").localize(user_dt)

        # 解析當前時間
        now = datetime.strptime(
            current_date_time.split(" Asia/Taipei")[0], "%Y-%m-%d %H:%M"
        )
        now = pytz.timezone("Asia/Taipei").localize(now)

        # 計算時間差（秒）
        time_diff = (user_dt - now).total_seconds()

        # 判斷是過去還是未來
        if time_diff < 0:
            result = "過去"
        else:
            result = "未來"

        return f"使用者指定的時間是{result}"
    except Exception as e:
        return f"Error: {e}"


@tool
def chat_with_pdf(pdf_url: str, user_input: str):
    """
    Use this to chat with a PDF file.
    User can ask about any text, pictures, charts, and tables in PDFs that is provided. Some sample use cases:
    - Analyzing financial reports and understanding charts/tables
    - Extracting key information from legal documents
    - Translation assistance for documents
    - Converting document information into structured formats

    Data Visualization Integration:
    When the user's input indicates a need for comparison or data visualization (e.g., "compare the quarterly profits",
    "show the trend of sales"), this function can return data in a format suitable for Plotly visualization.
    The returned data will be a dictionary with a special key "__plotly_data__" containing:
    {
        "__plotly_data__": {
            "data": [...],  # Plotly data array
            "layout": {...}  # Plotly layout object
        }
    }
    You can then pass this data to create_plotly_chart to generate an interactive chart.

    If you have a local PDF file, you can use generate_tmp_public_url tool to get a public URL first:
    1. Call generate_tmp_public_url with your local PDF file path
    2. Use the returned URL as the pdf_url parameter for this function

    Args:
        pdf_url: the URL to the PDF file (can be generated using generate_tmp_public_url for local files)
        user_input: the user's input

    Returns:
        str: Analysis result or Plotly-compatible data structure if visualization is needed
    """
    print("chat_with_pdf============>", pdf_url, user_input)
    if not pdf_url.startswith("http"):
        pdf_url = upload_and_get_tmp_public_url(
            pdf_url,
            DICT_VAR.get("botrun_flow_lang_url", ""),
            DICT_VAR.get("user_id", ""),
        )
    return analyze_pdf(pdf_url, user_input)


@tool
def chat_with_imgs(img_urls: list[str], user_input: str):
    """
    Use this to analyze and understand multiple images using Claude's vision capabilities.

    If you have local image files, you can use generate_tmp_public_url tool multiple times to get public URLs first:
    1. Call generate_tmp_public_url for each local image file
    2. Collect all returned URLs into a list
    3. Use the list of URLs as the img_urls parameter for this function

    Data Visualization Integration:
    When the user's input indicates a need for comparison or data visualization (e.g., "compare the values in these charts",
    "extract and plot the data from these images"), this function can return data in a format suitable for Plotly visualization.
    The returned data will be a dictionary with a special key "__plotly_data__" containing:
    {
        "__plotly_data__": {
            "data": [...],  # Plotly data array
            "layout": {...}  # Plotly layout object
        }
    }
    You can then pass this data to create_plotly_chart to generate an interactive chart.

    Supported image formats:
    - JPEG, PNG, GIF, WebP
    - Maximum file size: 5MB per image
    - Recommended size: No more than 1568 pixels in either dimension
    - Very small images (under 200 pixels) may degrade performance
    - Can analyze up to 20 images per request

    Capabilities:
    - Analyzing charts, graphs, and diagrams
    - Reading and understanding text in images
    - Describing visual content and scenes
    - Comparing multiple images in a single request
    - Answering questions about image details
    - Identifying relationships between images
    - Extracting data from charts for visualization

    Limitations:
    - Cannot identify or name specific people
    - May have reduced accuracy with low-quality or very small images
    - Limited spatial reasoning abilities
    - Cannot verify if images are AI-generated
    - Not designed for medical diagnosis or healthcare applications

    Args:
        img_urls: List of URLs to the image files (can be generated using generate_tmp_public_url for local files)
        user_input: Question or instruction about the image content(s)

    Returns:
        str: Claude's analysis of the image(s) based on the query, or Plotly-compatible data structure if visualization is needed
    """
    print("chat_with_imgs============>", img_urls, user_input)
    new_img_urls = []
    for img_url in img_urls:
        if not img_url.startswith("http"):
            img_url = upload_and_get_tmp_public_url(
                img_url,
                DICT_VAR.get("botrun_flow_lang_url", ""),
                DICT_VAR.get("user_id", ""),
            )
        new_img_urls.append(img_url)
    return analyze_imgs(new_img_urls, user_input)


@tool
def generate_tmp_public_url(file_path: str) -> str:
    """
    使用者會給你一個本地端的檔案路徑，請你使用這個 generate_tmp_public_url tool 生成一個臨時的公開 URL，這個 URL 可以讓使用者下載這個檔案。
    如果使用者給了多個本地端的檔案路徑，請你多次呼叫這個 tool，並將每次呼叫的回傳值收集起來。

    Args:
        file_path: The path to the local file you want to make publicly accessible

    Returns:
        str: A public URL that can be used to access the file for 7 days

    Raises:
        FileNotFoundError: If the specified file does not exist
    """
    print("generate_tmp_public_url============>", file_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    return upload_and_get_tmp_public_url(
        file_path,
        DICT_VAR.get("botrun_flow_lang_url", ""),
        DICT_VAR.get("user_id", ""),
    )


@tool
def deep_research(user_input: str, current_date_time: str) -> dict:
    """
    用於深度研究和獲取全面詳細資訊的搜尋工具。當需要以下情況時使用：
    - 使用者明確要求「深入研究」、「深度研究」、「深入搜尋」、「深度搜尋」
    - 需要跨多個領域的全面資訊
    - 需要詳細的新聞和報導
    - 需要深入分析複雜議題

    時間資訊處理要求：
    1. 必須保留使用者查詢中提到的任何特定日期或時間段
    2. 同時包含當前時間和來自查詢的任何特定時間參考

    使用範例：
    - 基本查詢:
      使用者問: "請深入研究台灣晶片產業現況"
      deep_research("請深入研究台灣晶片產業現況", "2025-03-11 14:30 Asia/Taipei")
      返回: {
          "content": "台灣晶片產業目前處於全球領先地位，台積電以...",
          "citations": [
              {"title": "經濟部統計處", "url": "https://www.moea.gov.tw/..."},
              {"title": "台積電官方網站", "url": "https://www.tsmc.com/..."}
          ]
      }

    - 帶有特定時間的查詢:
      使用者問: "深入研究 2025年全球AI發展趨勢"
      deep_research("深入研究 2025年全球AI發展趨勢", "2025-03-11 14:30 Asia/Taipei")
      返回: {
          "content": "2025年全球AI發展呈現快速增長...",
          "citations": [
              {"title": "世界經濟論壇", "url": "https://www.weforum.org/..."},
              {"title": "麻省理工科技評論", "url": "https://www.technologyreview.com/..."}
          ]
      }

    Args:
        user_input: 使用者的原始提問，必須完整保留，特別是其中提到的任何時間信息
                   例如："深入研究2025年台灣經濟狀況"應完整保留"2025年"
        current_date_time: 當前時間字串，必須由current_date_time()工具獲取
                     格式: "YYYY-MM-DD HH:MM Asia/Taipei"

    Returns:
        dict: 包含研究結果的字典:
              - content (str): 基於網路搜尋的詳細答案
              - citations (list): 引用的資訊來源列表，引用對使用者很重要，務必提供
    """
    try:
        print("deep_research============>", user_input, current_date_time)
        now = datetime.now()
        dates = format_dates(now)
        western_date = dates["western_date"]
        taiwan_date = dates["taiwan_date"]
        print("western_date============>", western_date)
        print("taiwan_date============>", taiwan_date)

        final_input = f"現在的西元時間：{western_date}\n現在的民國時間：{taiwan_date}\n\n現在的時間是：{current_date_time}\n\n使用者的提問是：{user_input}"

        # 定義一個內部的非同步函數來處理搜尋結果
        async def process_search():
            search_result = {
                "content": "",
                "citations": [],
            }
            async for event in respond_with_perplexity_search(
                final_input,
                user_prompt_prefix="",
                messages_for_llm=[],
                domain_filter=[],
                stream=False,
                model="sonar-deep-research",
                structured_output=True,
            ):
                if event and isinstance(event.chunk, str):
                    search_result = json.loads(event.chunk)
            return search_result

        # 使用 asyncio.run 執行非同步函數
        search_result = asyncio.run(process_search())
    except Exception as e:
        import traceback

        traceback.print_exc()
        return f"Error during web search: {str(e)}"
    return (
        search_result
        if search_result
        else {"content": "No results found.", "citations": []}
    )


@tool
def web_search(user_input: str, current_date_time: str) -> dict:
    """
    Use this to search the web when you need up-to-date information or when your knowledge is insufficient.
    This tool uses Perplexity to perform web searches and provides detailed answers with citations.

    除非使用者堅持要做多輪搜尋，不然這個工具能夠一次進行多個條件的搜尋，比如：
    一次進行多條件範例1：
    - 可以：
        - web_search("搜尋今天的體育、財經、政治新聞", current_date_time)
    - 不需要：
        - web_search("搜尋今天的體育新聞", current_date_time)
        - web_search("搜尋今天的財經新聞", current_date_time)
        - web_search("搜尋今天的政台新聞", current_date_time)

    Time/Date Information Requirements:
    1. MUST preserve any specific dates or time periods mentioned in the user's query
    2. Include both the current time and any specific time references from the query

    Examples:
    - Basic query:
      User asks: "台灣的人口數量"
      web_search("台灣的人口數量", "2024-03-20 14:30 Asia/Taipei")
      Actual search: "台灣的人口數量"
      Returns: {
          "content": "根據最新統計，台灣人口約為2300萬...",
          "citations": [
              {"title": "內政部統計處", "url": "https://www.moi.gov.tw/..."},
              {"title": "國家發展委員會", "url": "https://www.ndc.gov.tw/..."}
          ]
      }

    - Query with specific date:
      User asks: "幫我查詢 2025/1/1 的新聞"
      web_search("幫我查詢 2025/1/1 的新聞", "2024-03-20 14:30 Asia/Taipei")
      Returns: {
          "content": "關於2025年1月1日的新聞預測...",
          "citations": [
              {"title": "經濟日報", "url": "https://money.udn.com/..."},
              {"title": "中央社", "url": "https://www.cna.com.tw/..."}
          ]
      }

    Args:
        user_input: The search query or question you want to find information about.
                   MUST include any specific time periods or dates from the original query.
                   Examples of time formats to preserve:
                   - Specific dates: "2025/1/1", "2023-12-31"
                   - Years: "2023年"
                   - Quarters/Months: "第一季", "Q1", "一月"
                   - Time periods: "過去三年", "未來五年"
        current_date_time: The current time string MUST be got by current_date_time() tool. You can NOT use the current time from your own knowledge.
                     Format: "YYYY-MM-DD HH:MM Asia/Taipei"

    Returns:
        dict: A dictionary containing:
              - content (str): The detailed answer based on web search results
              - citations (list): A list of URLs, citation對使用者很重要，務必提供給使用者
    """
    print("web_search============>", user_input, current_date_time)
    now = datetime.now()
    dates = format_dates(now)
    western_date = dates["western_date"]
    taiwan_date = dates["taiwan_date"]
    print("western_date============>", western_date)
    print("taiwan_date============>", taiwan_date)

    final_input = f"現在的西元時間：{western_date}\n現在的民國時間：{taiwan_date}\n\n現在的時間是：{current_date_time}\n\n使用者的提問是：{user_input}"
    try:
        # 定義一個內部的非同步函數來處理搜尋結果
        async def process_search():
            search_result = {
                "content": "",
                "citations": [],
            }
            async for event in respond_with_perplexity_search(
                final_input,
                user_prompt_prefix="",
                messages_for_llm=[],
                domain_filter=[],
                stream=False,
                structured_output=True,
            ):
                if event and isinstance(event.chunk, str):
                    search_result = json.loads(event.chunk)
            return search_result

        # 使用 asyncio.run 執行非同步函數
        search_result = asyncio.run(process_search())
    except Exception as e:
        import traceback

        traceback.print_exc()
        return f"Error during web search: {str(e)}"
    return (
        search_result
        if search_result
        else {"content": "No results found.", "citations": []}
    )


@tool
def generate_image(user_input: str):
    """
    Use this to generate high-quality images using DALL-E 3.

    Capabilities:
    - Creates photorealistic images and art
    - Handles complex scenes and compositions
    - Maintains consistent styles
    - Follows detailed prompts with high accuracy
    - Supports various artistic styles and mediums

    Best practices for prompts:
    - Be specific about style, mood, lighting, and composition
    - Include details about perspective and setting
    - Specify artistic medium if desired (e.g., "oil painting", "digital art")
    - Mention color schemes or specific colors
    - Describe the atmosphere or emotion you want to convey

    Limitations:
    - Cannot generate images of public figures or celebrities
    - Avoids harmful, violent, or adult content
    - May have inconsistencies with hands, faces, or text
    - Cannot generate exact copies of existing artworks or brands
    - Limited to single image generation per request

    Args:
        user_input: Detailed description of the image you want to generate.
                   Be specific about style, content, and composition.

    Returns:
        str: URL to the generated image, or error message if generation fails
    """
    try:
        print("generate_image============>", user_input)
        image_response = image_generation(
            prompt=user_input,
            model="dall-e-3",
            api_key=os.getenv("OPENAI_API_KEY"),
        )

        image_url = image_response["data"][0]["url"]
        print("generate_image generated============>", image_url)
        print(
            f"generate_image============> input_token: {image_response.usage.prompt_tokens} output_token: {image_response.usage.completion_tokens}",
        )
        return image_url
    except Exception as e:
        return f"Error: {e}"


@tool
def create_plotly_chart(figure_data: str, title: str = None) -> str:
    """
    Create an interactive Plotly visualization and return its URL.
    This URL should be provided to the user,
    as they will need to access it to view the interactive chart in their web browser.

    使用 create_plotly_chart 的情境：
    - 提到「圖表」、「統計圖」、「視覺化」等字眼
    - 需要呈現數據趨勢（折線圖）
    - 需要比較數值（長條圖、圓餅圖）
    - 需要展示分布情況（散點圖、熱力圖）
    - 需要顯示時間序列資料（時間軸圖）
    - 需要展示地理資訊（地圖）
    - 需要多維度資料分析（3D圖、氣泡圖）
    - 需要展示統計分布（箱型圖）
    - 需要展示累積趨勢（面積圖）
    - 需要互動式資料探索

    Integration with Other Tools:
    This function can be used in conjunction with chat_with_imgs and chat_with_pdf when they return data
    suitable for visualization. When those tools detect a need for visualization, they will return a JSON string
    with a "__plotly_data__" key, which can be directly passed to this function.

    Example workflow:
    1. User asks to analyze and visualize data from images/PDFs
    2. chat_with_imgs or chat_with_pdf returns JSON string with "__plotly_data__" key
    3. Pass that string to this function to get an interactive visualization URL

    Supported Chart Types:
    - Line charts: For showing trends and time series data
    - Bar charts: For comparing values across categories
    - Pie charts: For showing proportions of a whole
    - Scatter plots: For showing relationships between variables
    - Heat maps: For showing patterns in matrix data
    - Box plots: For showing statistical distributions
    - Geographic maps: For showing spatial data
    - 3D plots: For showing three-dimensional data
    - Bubble charts: For showing three variables in 2D
    - Area charts: For showing cumulative totals over time

    The figure_data should be a JSON string containing plotly figure specifications with 'data' and 'layout'.
    Example:
    {
        'data': [{
            'type': 'scatter',
            'x': [1, 2, 3, 4],
            'y': [10, 15, 13, 17]
        }],
        'layout': {
            'title': 'My Plot'
        }
    }

    Args:
        figure_data: JSON string containing plotly figure specifications or output from chat_with_imgs/chat_with_pdf.
                    Will be parsed using json.loads().
        title: Optional title for the plot. If provided, must be in Traditional Chinese.
               For example: "台灣人口統計圖表" instead of "Taiwan Population Chart"

    Returns:
        str: URL for the interactive HTML visualization. This URL should be provided to the user,
             as they will need to access it to view the interactive chart in their web browser.
    """
    try:
        print("create_plotly_chart============>", figure_data, title)
        # Parse the JSON string into a dictionary
        figure_dict = json.loads(figure_data)

        # If the input is from chat_with_imgs or chat_with_pdf, extract the plotly data
        if "__plotly_data__" in figure_dict:
            figure_dict = figure_dict["__plotly_data__"]

        html_url = generate_plotly_files(
            figure_dict,
            DICT_VAR.get("botrun_flow_lang_url", ""),
            DICT_VAR.get("user_id", ""),
            title,
        )
        print("create_plotly_chart generated============>", html_url)
        return html_url
    except Exception as e:
        return f"Error creating visualization URL: {str(e)}"


@tool
def create_mermaid_diagram(mermaid_data: str, title: str = None) -> str:
    """
    Create an interactive Mermaid diagram visualization and return its URL.
    This URL should be provided to the user,
    as they will need to access it to view the interactive diagram in their web browser.

    使用 create_mermaid_diagram 的情境：
    - 提到「流程圖」、「架構圖」、「關係圖」等字眼
    - 需要展示系統架構（flowchart）
    - 需要說明操作流程（flowchart）
    - 需要展示時序互動（sequence diagram）
    - 需要展示狀態轉換（state diagram）
    - 需要展示類別關係（class diagram）
    - 需要展示實體關係（ER diagram）
    - 需要展示專案時程（gantt chart）
    - 需要展示使用者旅程（journey）
    - 需要展示需求關係（requirement diagram）
    - 需要展示資源分配（pie chart）

    Supported Diagram Types:
    1. Flowcharts (graph TD/LR):
       - System architectures
       - Process flows
       - Decision trees
       - Data flows

    2. Sequence Diagrams (sequenceDiagram):
       - API interactions
       - System communications
       - User interactions
       - Message flows

    3. Class Diagrams (classDiagram):
       - Software architecture
       - Object relationships
       - System components
       - Code structure

    4. State Diagrams (stateDiagram-v2):
       - System states
       - Workflow states
       - Process states
       - State transitions

    5. Entity Relationship Diagrams (erDiagram):
       - Database schemas
       - Data relationships
       - System entities
       - Data models

    6. User Journey Diagrams (journey):
       - User experiences
       - Customer flows
       - Process steps
       - Task sequences

    7. Gantt Charts (gantt):
       - Project timelines
       - Task schedules
       - Resource allocation
       - Milestone tracking

    8. Pie Charts (pie):
       - Data distribution
       - Resource allocation
       - Market share
       - Component breakdown

    9. Requirement Diagrams (requirementDiagram):
       - System requirements
       - Dependencies
       - Specifications
       - Constraints

    Example Mermaid syntax for a simple flowchart:
    ```
    graph TD
        A[開始] --> B{是否有資料?}
        B -->|是| C[處理資料]
        B -->|否| D[取得資料]
        C --> E[結束]
        D --> B
    ```

    Args:
        mermaid_data: String containing the Mermaid diagram definition
        title: Optional title for the diagram. If provided, must be in Traditional Chinese.
               For example: "系統流程圖" instead of "System Flowchart"

    Returns:
        str: URL for the interactive HTML visualization. This URL should be provided to the user,
             as they will need to access it to view the interactive diagram in their web browser.
    """
    try:
        print("create_mermaid_diagram============>", mermaid_data, title)
        html_url = generate_mermaid_files(
            mermaid_data,
            DICT_VAR.get("botrun_flow_lang_url", ""),
            DICT_VAR.get("user_id", ""),
            title,
        )
        print("create_mermaid_diagram generated============>", html_url)
        return html_url
    except Exception as e:
        return f"Error creating diagram URL: {str(e)}"


@tool
def create_html_page(html_content: str, title: str = None) -> str:
    """
    Create a custom HTML page and return its URL.
    This URL should be provided to the user, as they will need to access it to view the HTML content in their web browser.

    這個工具支援完整的HTML文檔，包括JavaScript和CSS，可以用來創建複雜的互動式頁面。

    使用 create_html_page 的情境：
    - 需要展示自定義的HTML內容
    - 需要嵌入複雜的互動式內容
    - 需要製作自訂格式的報告或文件
    - 需要使用第三方JavaScript庫
    - 需要展示表格、圖像和多媒體內容
    - 需要創建結構化且易於閱讀的内容呈現
    - 需要使用CSS樣式創建美觀的界面
    - 需要嵌入特殊的圖表或視覺元素

    Input Options:
    You can pass either:
    1. A complete HTML document with doctype, html, head, and body tags
    2. An HTML fragment that will be automatically wrapped in a basic HTML structure

    Supported HTML Features:
    - Complete HTML documents with your own structure
    - Custom JavaScript for interactive elements
    - Custom CSS for styling and layout
    - External libraries and frameworks (via CDN)
    - Tables, lists, and other structural elements
    - Embedded images and multimedia (via URLs)
    - Form elements (though they won't submit data)
    - Responsive design elements
    - Unicode and international text support

    Security Considerations:
    - HTML content is sandboxed in the browser
    - Cannot access user's device or data
    - External resources must be from trusted sources
    - No server-side processing capability
    - No personal data should be included in the HTML

    Example of complete HTML document:
    ```html
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>互動式報告</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .chart { height: 300px; margin: 20px 0; border: 1px solid #ddd; }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <div class="container">
            <h1>業績分析報告</h1>
            <p>本報告提供了公司過去三個月的銷售數據分析。</p>
            <div class="chart">
                <canvas id="salesChart"></canvas>
            </div>
            <script>
                // JavaScript可以直接在HTML中使用
                const ctx = document.getElementById('salesChart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: ['一月', '二月', '三月'],
                        datasets: [{
                            label: '銷售額（千元）',
                            data: [1200, 1900, 1500],
                            backgroundColor: ['#ff6384', '#36a2eb', '#ffce56']
                        }]
                    }
                });
            </script>
        </div>
    </body>
    </html>
    ```

    Example of HTML fragment (will be auto-wrapped):
    ```html
    <div style="padding: 20px; background-color: #f0f8ff;">
      <h1 style="color: #333; font-family: Arial, sans-serif;">客戶報告</h1>
      <p>這份報告包含了重要的資訊。</p>
      <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr>
          <th>項目</th>
          <th>數量</th>
          <th>單價</th>
        </tr>
        <tr>
          <td>產品A</td>
          <td>10</td>
          <td>$100</td>
        </tr>
        <tr>
          <td>產品B</td>
          <td>5</td>
          <td>$200</td>
        </tr>
      </table>
    </div>
    ```

    Args:
        html_content: Complete HTML document or fragment. Can include JavaScript, CSS, and other elements.
        title: Optional title for the HTML page. If provided, must be in Traditional Chinese.
               For example: "客戶報告" instead of "Client Report"
               Note: This is only used if the HTML content doesn't already have a title.

    Returns:
        str: URL for the HTML page. This URL should be provided to the user,
             as they will need to access it to view the content in their web browser.
    """
    try:
        print("create_html_page============>", html_content, title)
        html_url = generate_html_file(
            html_content,
            DICT_VAR.get("botrun_flow_lang_url", ""),
            DICT_VAR.get("user_id", ""),
            title,
        )
        print("create_html_page generated============>", html_url)
        return html_url
    except Exception as e:
        return f"Error creating HTML page URL: {str(e)}"


BASIC_TOOLS = [
    # step_planner,
    current_date_time,
    compare_date_time,
    scrape,
    chat_with_pdf,
    chat_with_imgs,
    web_search,
    # deep_research,
    generate_image,
]
DICT_VAR = {}

# Define the graph

now = datetime.now()
dates = format_dates(now)
western_date = dates["western_date"]
taiwan_date = dates["taiwan_date"]


def create_react_agent_graph(
    system_prompt: str = "",
    botrun_flow_lang_url: str = "",
    user_id: str = "",
    model_name: str = "",
):
    """
    Create a react agent graph with optional system prompt

    Args:
        system_prompt: The system prompt to use for the agent
    """
    tools = BASIC_TOOLS
    if botrun_flow_lang_url and user_id:
        DICT_VAR["botrun_flow_lang_url"] = botrun_flow_lang_url
        DICT_VAR["user_id"] = user_id
        tools.append(generate_tmp_public_url)
        tools.append(create_plotly_chart)
        tools.append(create_mermaid_diagram)
        tools.append(create_html_page)
        # print("tools============>", tools)
    new_system_prompt = (
        system_prompt
        + """

    以下為回應時需注意的準則，請你務必遵守，你會遵守<使用工具 (tools) 需注意的事項>、以及<回應時需注意的準則>。
<回應時需注意的準則>
- 如果 tool 的文件叫你調用其它 tool，請你一定要直接調用，不要叫使用者調用。
- 關於搜尋工具的選擇：
  * 僅當使用者明確提出「深入研究」、「深度研究」、「深入搜尋」、「深度搜尋」等要求時，才使用 deep_research 工具，而且不使用 web_search 工具。
  * 在所有其他情況下，包括一般搜尋、查詢資訊等，都必須使用 web_search 工具。
  * 嚴禁在使用者未明確要求深入研究、深入搜尋的情況下使用 deep_research 工具。
- 如果使用者的問題中有指定日期時間，不要預設它是未來或過去，一定要先使用 current_date_time 和 compare_date_time 這兩個工具，以取得現在的日期時間並判斷使用者指定的日期時間是過去或未來，然後再進行後續的動作。比較日期時，注意<時間解讀說明>。
- 如果你要傳給使用者任何的 URL，請確保 URL 是從 tool 回傳的，或是從歷史記錄中找到的，千萬不可自己創造 URL 回傳給使用者。
- 如果A工具回傳的是 URL，B工具的參數需要用到A工具回傳的URL，請直接使用A工具回傳的URL，不要自己創造URL。
- 如果要傳給工具的內容是使用者提問，要注意原始使用者有沒有特別寫：千萬、注意、一定要、不要、務必…等等的字眼，如果有，請你也要將這些字眼包的使用者提問含在user_input中。
</回應時需注意的準則>
<時間解讀說明>
current_date_time 的回傳值，可以幫助判斷使用者查詢是關於過去的歷史資訊，還是關於未來的預測資訊。
這個函數會回傳此時此刻的精確日期時間。例如：
回傳 "2023-03-19 13:23 Asia/Taipei" 代表現在是2023年3月19日 13點23分台北時間。
當比較使用者查詢的日期時：
- 如果使用者問的是 "2023年3月10日23:00到2023年3月11日23:00"，這個日期發生在過去
- 如果使用者問的是 "2023年3月20日23:00到2023年3月21日23:00"，這個日期發生在未來
- 如果使用者問題是 "2023年3月10-11日"，這個日期發生在過去
</時間解讀說明>
<使用工具 (tools) 需注意的事項>
- deep_research:
    使用條件：當使用者明確提出「深入研究」、「深度研究」、「深入搜尋」、「深度搜尋」等要求時，才會使用這個工具。
    
    工具多次使用策略：
    * 如果第一次的結果不完整或未找到所需資訊，請務必多次使用此工具！
    * 再次使用時可嘗試分解問題為更細部分，或聚焦於尚未取得資訊的特定方面
    * 建議至少嘗試2-3次，以獲取最全面的資訊
    
    首次使用時，請一字不改地將使用者的原始提問傳入 user_input 參數。
    例如：
    使用者提問：「請深入研究2025年3月1~3日亞洲地區所發生的有關於寒害、雪崩相關的災難新聞，參考來源要包含繁體中文、日文、和英文網站」
    首次呼叫：deep_research("請深入研究2025年3月1~3日亞洲地區所發生的有關於寒害、雪崩相關的災難新聞，參考來源要包含繁體中文、日文、和英文網站", current_date_time)
    
    後續使用可調整關鍵詞或細分主題，例如：
    第二次呼叫：deep_research("深入研究2025年3月1~3日日本北海道地區雪崩災害的具體情況和救援行動", current_date_time)
    第三次呼叫：deep_research("深入分析2025年3月1~3日中國東北和韓國地區的極端寒流造成的經濟損失和人員傷亡", current_date_time)

- web_search:
    在所有一般搜尋情況下使用此工具，除非使用者明確提出「深入研究」、「深度研究」、「深入搜尋」、「深度搜尋」等要求。
    如果使用者明確要求深入研究，請使用 deep_research 工具代替。
    
    當使用 web_search 工具時，請先確認前面的 system prompt 以及使用者的提問請求是否包含下列資訊：
    - 搜尋語言
    - 搜尋網站來源
    如果包含上述資訊，請將這些資訊附加於 user_input 結尾，並註明優先搜尋這些語言或網站的資料。

- generate_image: 
    當使用 generate_image 工具時，你必須在回應中包含圖片網址。
    請按照以下格式回應(從 @begin img開始，到 @end 結束，中間包含圖片網址)：
    @begin img("{image_url}") @end

- chat_with_pdf:
    使用者的問題或指令。如果問題中包含以下關鍵字，要在 user_input 中包含以下字句：
    - 「圖表」、「統計圖」、「視覺化」：幫我生成適合的統計圖表，並提供相關 plotly 的資料給我
    - 「趨勢」、「走向」：幫我生成折線圖，並提供相關 plotly 的資料給我
    - 「比較」、「對照」：幫我生成長條圖或圓餅圖，並提供相關 plotly 的資料給我
    - 「分布」、「分散」：幫我生成散點圖或熱力圖，並提供相關 plotly 的資料給我
    - 「時間序列」：幫我生成時間軸圖，並提供相關 plotly 的資料給我
    - 「地理資訊」：幫我生成地圖，並提供相關 plotly 的資料給我
    - 「多維度分析」：幫我生成 3D 圖或氣泡圖，並提供相關 plotly 的資料給我
    - 「流程圖」、「流程」：幫我生成 flowchart，並提供相關 mermaid 的資料給我
    - 「架構圖」、「架構」：幫我生成 flowchart，並提供相關 mermaid 的資料給我
    - 「關係圖」、「關係」：幫我生成 flowchart 或 ER diagram，並提供相關 mermaid 的資料給我
    - 「時序圖」、「序列圖」：幫我生成 sequence diagram，並提供相關 mermaid 的資料給我
    - 「狀態圖」、「狀態」：幫我生成 state diagram，並提供相關 mermaid 的資料給我
    - 「類別圖」、「類別」：幫我生成 class diagram，並提供相關 mermaid 的資料給我
    - 「甘特圖」、「時程圖」：幫我生成 gantt chart，並提供相關 mermaid 的資料給我

- create_plotly_chart:
    當使用 create_plotly_chart 工具時，你必須在回應中包含create_plotly_chart回傳的URL網址。
    請按照以下格式回應：
    [{plotly_chart_title}] ({plotly_chart_url})
    <範例1>
    使用者提問：
    請幫我分析這個PDF的內容，並產出一個圖表給我看
    回應：
    {分析的內容文字}
    我為你製作了一個圖表，請看這個網址：
    [{plotly_chart_title}] ({plotly_chart_url})
    </範例1>
    <範例2>
    使用者提問：
    請幫我深度分析這個檔案內容，並產出讓使用者好懂的比較圖
    回應：
    {分析的內容文字}
    我為你製作了一個圖表，請看這個網址：
    [{plotly_chart_title}] ({plotly_chart_url})
    </範例2>

- create_mermaid_diagram:
    當使用 create_mermaid_diagram 工具時，你必須在回應中包含create_mermaid_diagram回傳的URL網址。
    請按照以下格式回應：
    [{mermaid_diagram_title}] ({mermaid_diagram_url})
    <範例1>
    使用者提問：
    請幫我分析這個PDF的內容，根據開會決議，產出一個行動流程圖
    回應：
    {分析的內容文字}
    我為你製作了一個流程圖，請看這個網址：
    [{mermaid_diagram_title}] ({mermaid_diagram_url})
    </範例1>
    <範例2>
    使用者提問：
    請幫我深度分析這個檔案內容，根據新的伺服器架構，產出一個架構圖
    回應：
    {分析的內容文字}
    我為你製作了一個架構圖，請看這個網址：
    [{mermaid_diagram_title}] ({mermaid_diagram_url})
    </範例2>
</使用工具 (tools) 需注意的事項>
    """
    )
    system_message = SystemMessage(
        content=[
            {
                "text": new_system_prompt,
                "type": "text",
                "cache_control": {"type": "ephemeral"},
            }
        ]
    )

    # 目前先使用了 https://docs.anthropic.com/en/docs/build-with-claude/tool-use/token-efficient-tool-use
    # 這一段會遇到
    #       File "/Users/seba/Projects/botrun_flow_lang/.venv/lib/python3.11/site-packages/langgraph/prebuilt/tool_node.py", line 218, in __init__
    #     tool_ = create_tool(tool_)
    #             ^^^^^^^^^^^^^^^^^^
    #   File "/Users/seba/Projects/botrun_flow_lang/.venv/lib/python3.11/site-packages/langchain_core/tools/convert.py", line 334, in tool
    #     raise ValueError(msg)
    # ValueError: The first argument must be a string or a callable with a __name__ for tool decorator. Got <class 'dict'>
    # 所以先不使用這一段，這一段是參考 https://python.langchain.com/docs/integrations/chat/anthropic/#tools
    # 也許未來可以引用
    # if get_react_agent_model_name(model_name).startswith("claude-"):
    #     new_tools = []
    #     for tool in tools:
    #         new_tool = convert_to_anthropic_tool(tool)
    #         new_tool["cache_control"] = {"type": "ephemeral"}
    #         new_tools.append(new_tool)
    #     tools = new_tools

    return create_react_agent(
        get_react_agent_model(model_name),
        tools=tools,
        prompt=system_message,
        checkpointer=MemorySaver(),
        # checkpointer=FirestoreCheckpointer(env_name=env_name),
    )


# Default graph instance with empty prompt
if False:
    graph = create_react_agent_graph()
    # LangGraph Studio 測試用
# graph = create_react_agent_graph(
#     system_prompt="",
#     botrun_flow_lang_url="https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
#     user_id="sebastian.hsu@gmail.com",
#     env_name="development",
# )
