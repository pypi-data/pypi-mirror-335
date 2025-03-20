from datetime import datetime
import unittest
import json
from langchain_anthropic import ChatAnthropic
import pytz
import requests
import os
from typing import Dict, Any, List
import litellm
from litellm import completion
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from trustcall import create_extractor
from botrun_flow_lang.langgraph_agents.agents.util.local_files import (
    upload_and_get_tmp_public_url,
)
from pathlib import Path


class ValidationResult(BaseModel):
    """Pydantic model for the validation result"""

    pass_: bool = Field(
        description="Whether the validation passes (true) or fails (false), If all conditions are met, return true, otherwise return false"
    )
    reason: str = Field(
        description="Detailed explanation of why validation passed or failed"
    )


class TestAPIFunctionality(unittest.TestCase):
    """Test class for REST API functionality tests"""

    def setUp(self):
        """Setup method that runs before each test"""
        # Default base URL, can be overridden by setting the class attribute
        if not hasattr(self, "base_url"):
            self.base_url = "http://0.0.0.0:8080"
            # self.base_url = (
            #     "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app"
            # )

        # Common headers
        self.headers = {"Content-Type": "application/json"}

        # Initialize LLM and extractor
        # self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.llm = ChatAnthropic(model="claude-3-5-haiku-latest", temperature=0)
        self.validator = create_extractor(
            self.llm, tools=[ValidationResult], tool_choice="ValidationResult"
        )
        local_tz = pytz.timezone("Asia/Taipei")
        self.local_time = datetime.now(local_tz)

    def api_post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method to make POST requests to the API

        Args:
            endpoint: The API endpoint path (without base URL)
            data: The request payload as a dictionary

        Returns:
            The JSON response as a dictionary
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, headers=self.headers, json=data)

        # Raise an exception if the response was unsuccessful
        response.raise_for_status()

        return response.json()

    def validate_with_llm(
        self, response_content: str, validation_criteria: str
    ) -> Dict[str, Any]:
        """Use trustcall with GPT-4o-mini to validate the response content

        Args:
            response_content: The content to validate
            validation_criteria: Validation criteria description

        Returns:
            Dictionary with 'pass' (boolean) and 'reason' (string)
        """
        prompt = f"""
        你是一個專業的API回應驗證員。請評估以下API回應是否符合所有指定條件。
        
        === 驗證條件 ===
        {validation_criteria}
        
        === API回應內容 ===
        {response_content}
        
        請評估API回應是否符合所有驗證條件。詳細說明評估原因，若不符合條件，請明確指出哪些條件未達成。
        """

        try:
            # Use trustcall extractor to validate
            result = self.validator.invoke(
                {"messages": [{"role": "user", "content": prompt}]}
            )

            # Extract the validated response
            validation_result = result["responses"][0]

            # Convert to the expected format
            return {"pass": validation_result.pass_, "reason": validation_result.reason}

        except Exception as e:
            return {"pass": False, "reason": f"Error during validation: {str(e)}"}

    def test_langgraph_news_joke_emoji(self):
        """測試是否會抓到今天的新聞，檢查重點：
        1. 是否會抓到今天的新聞
        2. 是否會列出來源網址
        3. 是否會講個笑話，並加上 emoji
        """
        # Test payload
        payload = {
            "graph_name": "langgraph_react_agent",
            "messages": [
                {
                    "role": "user",
                    "content": "幫我搜尋今天的新聞是什麼？一一列出來，並給我參考來源網址。",
                }
            ],
            "config": {
                "system_prompt": "回答後你都會在結尾講個笑話，並加上 emoji",
                "botrun_flow_lang_url": "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
                "user_id": "sebastian.hsu@gmail.com",
            },
        }

        # Make the request
        endpoint = "/api/langgraph/invoke"
        print(f"\nTesting API: {self.base_url}{endpoint}")
        print("-" * 50)

        try:
            response = self.api_post(endpoint, payload)

            # Basic assertions to verify the response
            self.assertIsNotNone(response)

            # Extract the content field from the response
            if "content" in response:
                response_content = response["content"]
            else:
                self.fail("Response does not contain 'content' field")

            validation_criteria = f"""
            1. 是否包含今天 {self.local_time.strftime("%Y-%m-%d")} 日期的新聞資訊，沒有列出日期測試算失敗
            2. 是否列出每則新聞的來源網址
            3. 是否在回答結尾包含一個笑話
            """

            # Validate with LLM
            validation_result = self.validate_with_llm(
                response_content, validation_criteria
            )

            # Assert that the validation passed
            self.assertTrue(
                validation_result["pass"],
                f"LLM validation failed in {self._testMethodName}: {validation_result['reason']}, LLM response: {response_content}",
            )

        except Exception as e:
            print(f"test_langgraph_news_joke_emoji: Test failed with error: {str(e)}")
            raise

    def test_langgraph_multinode_news_dall_e(self):
        """測試多節點處理流程，檢查重點：
        1. 是否會抓到今天的新聞
        2. 是否有評分新聞 (1-10分)
        3. 是否有產出一張圖片，並帶有 URL
        """
        # Test payload
        payload = {
            "graph_name": "langgraph_react_agent",
            "messages": [
                {
                    "role": "user",
                    "content": "好。 我們現在就是跟那個Bert人講多個節點,那它裡面它就會用多個節點的方式直接去工作,比如說第一個節點就是請Bert人上網去搜尋今天的新聞。 然後第二個節點呢,請你把這個新聞,打分,一分到十分,哪個新聞最可愛。 然後第三個節點呢,請你根據分數最高的那一個新聞,你幫我呼叫達利畫一張跟那個新聞相關的圖片,那我們就用這個來示範一下,來。",
                }
            ],
            "config": {
                "system_prompt": "回答後你都會在結尾講個笑話，並加上 emoji",
                "botrun_flow_lang_url": "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
                "user_id": "sebastian.hsu@gmail.com",
            },
        }

        # Make the request
        endpoint = "/api/langgraph/invoke"
        print(f"\nTesting API: {self.base_url}{endpoint}")
        print("-" * 50)

        try:
            response = self.api_post(endpoint, payload)

            # Basic assertions to verify the response
            self.assertIsNotNone(response)

            # Extract the content field from the response
            if "content" in response:
                response_content = response["content"]
            else:
                self.fail("Response does not contain 'content' field")

            # Define validation criteria based on the test requirements
            validation_criteria = f"""
            1. 是否會抓到今天 {self.local_time.strftime("%Y-%m-%d")} 日期的新聞
            2. 是否有評分新聞 (1-10分)
            3. 是否有產出一張圖片，並帶有 URL
            4. 是否在回答結尾包含一個笑話
            """

            # Validate with LLM
            validation_result = self.validate_with_llm(
                response_content, validation_criteria
            )

            # Assert that the validation passed
            self.assertTrue(
                validation_result["pass"],
                f"LLM validation failed in {self._testMethodName}: {validation_result['reason']}, LLM response: {response_content}",
            )

        except Exception as e:
            print(
                f"test_langgraph_multinode_news_dall_e: Test failed with error: {str(e)}"
            )
            raise

    def test_langgraph_future_date_news(self):
        """測試未來日期的新聞搜尋，檢查重點：
        1. 是否是指定時間的 2025/2/10 的新聞，回覆內容要有這個時間
        2. 不能回應說這個時間在未來，所以無法回答，可以說 "截至2025年2月10日，相關的新聞如下："。
        """
        # Test payload
        payload = {
            "graph_name": "langgraph_react_agent",
            "messages": [
                {
                    "role": "user",
                    "content": "請你幫我找2025/2/10全球災難新聞",
                }
            ],
            "config": {
                "system_prompt": "回答後你都會在結尾講個笑話，並加上 emoji",
                "botrun_flow_lang_url": "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
                "user_id": "sebastian.hsu@gmail.com",
            },
        }

        # Make the request
        endpoint = "/api/langgraph/invoke"
        print(f"\nTesting API: {self.base_url}{endpoint}")
        print("-" * 50)

        try:
            response = self.api_post(endpoint, payload)

            # Basic assertions to verify the response
            self.assertIsNotNone(response)

            # Extract the content field from the response
            if "content" in response:
                response_content = response["content"]
            else:
                self.fail("Response does not contain 'content' field")

            # Define validation criteria based on the test requirements
            validation_criteria = """
            1. 是否包含指定時間 2025/2/10 的新聞資訊，回覆內容中必須有出現「2025/2/10」或類似的日期格式
            2. 不能包含任何提到該日期在未來、無法預測未來、尚未發生等類似的說明
            3. 是否在回答結尾包含一個笑話
            """

            # Validate with LLM
            validation_result = self.validate_with_llm(
                response_content, validation_criteria
            )

            # Assert that the validation passed
            self.assertTrue(
                validation_result["pass"],
                f"LLM validation failed in {self._testMethodName}: {validation_result['reason']}, LLM response: {response_content}",
            )

        except Exception as e:
            print(f"test_langgraph_future_date_news: Test failed with error: {str(e)}")
            raise

    def test_langgraph_pdf_analysis(self):
        """測試PDF分析功能，檢查重點：
        1. 是否能正確解析PDF檔案中的「表 4.3-1 環境敏感地區調查表-第一級環境敏感地區」
        2. 是否能列出所有項目的「查詢結果及限制內容」（是或否）
        3. 回傳結果是否符合預期的敏感區域結果
        """
        # 使用pathlib構建正確的檔案路徑

        current_dir = Path(__file__).parent
        pdf_path = (
            current_dir
            / "test_files"
            / "1120701A海廣離岸風力發電計畫環境影響說明書-C04.PDF"
        )

        # 確保檔案存在
        self.assertTrue(pdf_path.exists(), f"Test file not found at {pdf_path}")
        # 將絕對路徑轉為字串
        pdf_path_str = str(pdf_path)
        # 上傳檔案到 tmp_public_url
        tmp_public_url = upload_and_get_tmp_public_url(
            pdf_path_str,
            "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
            "sebastian.hsu@gmail.com",
        )

        # Test payload
        payload = {
            "graph_name": "langgraph_react_agent",
            "messages": [
                {
                    "role": "user",
                    "content": f"幫我分析 {tmp_public_url} 這個檔案，請你幫我找出在報告書中的「表 4.3-1 環境敏感地區調查表-第一級環境敏感地區」表格中的所有項目的「查詢結果及限制內容」幫我列出是或否？請全部列出來，不要遺漏",
                }
            ],
            "config": {
                "system_prompt": "回答後你都會在結尾講個笑話，並加上 emoji",
                "botrun_flow_lang_url": "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
                "user_id": "sebastian.hsu@gmail.com",
            },
        }

        # Make the request
        endpoint = "/api/langgraph/invoke"
        print(f"\nTesting API: {self.base_url}{endpoint}")
        print("-" * 50)

        try:
            response = self.api_post(endpoint, payload)

            # Basic assertions to verify the response
            self.assertIsNotNone(response)

            # Extract the content field from the response
            if "content" in response:
                response_content = response["content"]
            else:
                self.fail("Response does not contain 'content' field")

            # Define validation criteria based on existing test_pdf_analyzer.py
            validation_criteria = """
            請確認回應是否包含以下項目的查詢結果（是或否），所有項目都必須存在：
            1. 活動斷層兩側一定範圍: 否
            2. 特定水土保持區: 否
            3. 河川區域: 否
            4. 洪氾區一級管制區及洪水平原一級管制區: 否
            5. 區域排水設施範圍: 是
            6. 國家公園區內之特別景觀區、生態保護區: 否
            7. 自然保留區: 否
            8. 野生動物保護區: 否
            9. 野生動物重要棲息環境: 是
            10. 自然保護區: 否
            11. 一級海岸保護區: 是
            12. 國際級重要濕地、國家級重要濕地之核心保育區及生態復育區: 否
            13. 古蹟保存區: 否
            14. 考古遺址: 否
            15. 重要聚落建築群: 否
            
            所有項目都必須正確列出，且其中：
            - 區域排水設施範圍應為「是」
            - 野生動物重要棲息環境應為「是」
            - 一級海岸保護區應為「是」
            
            如果有遺漏任何一項或者結果不符合預期，則視為測試失敗。
            如果結果有超過，沒有關係。
            """

            # Validate with LLM
            validation_result = self.validate_with_llm(
                response_content, validation_criteria
            )

            # Assert that the validation passed
            self.assertTrue(
                validation_result["pass"],
                f"LLM validation failed in {self._testMethodName}: {validation_result['reason']}, LLM response: {response_content}",
            )

        except Exception as e:
            print(f"test_langgraph_pdf_analysis: Test failed with error: {str(e)}")
            raise

    def test_langgraph_pdf_attendance_analysis(self):
        """測試PDF分析功能，檢查重點：
        1. 是否能正確解析PDF檔案中的「目錄4」的出席名單
        2. 回答中是否有包含「德懷師父」、「德宸師父」、「德倫師父」
        """

        current_dir = Path(__file__).parent
        pdf_path = (
            current_dir
            / "test_files"
            / "(溫馨成果 行政請示匯總)20250210向 上人報告簡報 (1).pdf"
        )

        # 確保檔案存在
        self.assertTrue(pdf_path.exists(), f"Test file not found at {pdf_path}")

        # 將絕對路徑轉為字串
        pdf_path_str = str(pdf_path)

        # 上傳檔案到 tmp_public_url
        tmp_public_url = upload_and_get_tmp_public_url(
            pdf_path_str,
            "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
            "sebastian.hsu@gmail.com",
        )

        # Test payload
        payload = {
            "graph_name": "langgraph_react_agent",
            "messages": [
                {
                    "role": "user",
                    "content": f"幫我分析 {tmp_public_url} 這個檔案，你幫我看「目錄4」，告訴我有哪些師父和講者、執辦、主管有出席",
                }
            ],
            "config": {
                "system_prompt": "回答後你都會在結尾講個笑話，並加上 emoji",
                "botrun_flow_lang_url": "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
                "user_id": "sebastian.hsu@gmail.com",
            },
        }

        # Make the request
        endpoint = "/api/langgraph/invoke"
        print(f"\nTesting API: {self.base_url}{endpoint}")
        print("-" * 50)

        try:
            response = self.api_post(endpoint, payload)

            # Basic assertions to verify the response
            self.assertIsNotNone(response)

            # Extract the content field from the response
            if "content" in response:
                response_content = response["content"]
            else:
                self.fail("Response does not contain 'content' field")

            # Define validation criteria
            validation_criteria = """
            請確認回應是否包含以下師父的名字，所有名字都必須存在：
            1. 德懷師父
            2. 德宸師父
            3. 德倫師父
            
            此外，回應應該提供「目錄4」中出席的師父、講者、執辦和主管的完整列表。
            如果缺少上述任一師父的名字，則視為測試失敗。
            """

            # Validate with LLM
            validation_result = self.validate_with_llm(
                response_content, validation_criteria
            )

            # Assert that the validation passed
            self.assertTrue(
                validation_result["pass"],
                f"LLM validation failed in {self._testMethodName}: {validation_result['reason']}, LLM response: {response_content}",
            )

        except Exception as e:
            print(
                f"test_langgraph_pdf_attendance_analysis: Test failed with error: {str(e)}"
            )
            raise

    def test_langgraph_image_analysis_generation(self):
        """測試圖片分析與生成功能，檢查重點：
        1. 是否能正確分析圖片並識別出「佛教」相關元素
        2. 是否產生一張相同意境的圖片並提供URL
        """

        current_dir = Path(__file__).parent
        image_path = current_dir / "test_files" / "d5712343.jpg"

        # 確保檔案存在
        self.assertTrue(image_path.exists(), f"Test file not found at {image_path}")

        # 將絕對路徑轉為字串
        image_path_str = str(image_path)

        # 上傳檔案到 tmp_public_url
        tmp_public_url = upload_and_get_tmp_public_url(
            image_path_str,
            "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
            "sebastian.hsu@gmail.com",
        )

        # Test payload
        payload = {
            "graph_name": "langgraph_react_agent",
            "messages": [
                {
                    "role": "user",
                    "content": f"{tmp_public_url} 幫我分析這張圖裡的元素，然後幫我創作一張相同意境的圖片",
                }
            ],
            "config": {
                "system_prompt": "回答後你都會在結尾講個笑話，並加上 emoji",
                "botrun_flow_lang_url": "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
                "user_id": "sebastian.hsu@gmail.com",
            },
        }

        # Make the request
        endpoint = "/api/langgraph/invoke"
        print(f"\nTesting API: {self.base_url}{endpoint}")
        print("-" * 50)

        try:
            response = self.api_post(endpoint, payload)

            # Basic assertions to verify the response
            self.assertIsNotNone(response)

            # Extract the content field from the response
            if "content" in response:
                response_content = response["content"]
            else:
                self.fail("Response does not contain 'content' field")

            # Define validation criteria
            validation_criteria = """
            請確認回應是否符合以下條件：
            1. 分析結果中有提到「佛教」相關的元素（如佛像、和尚、寺廟、佛教符號等）
            2. 回應中包含一個圖片的URL（通常是以http或https開頭的網址，並包含在圖片的描述旁）
            3. 是否在回答結尾包含一個笑話
            
            所有條件都必須滿足，尤其是必須確認分析中有提到佛教元素，並且有生成一張新的圖片和提供其URL。
            """

            # Validate with LLM
            validation_result = self.validate_with_llm(
                response_content, validation_criteria
            )

            # Assert that the validation passed
            self.assertTrue(
                validation_result["pass"],
                f"LLM validation failed in {self._testMethodName}: {validation_result['reason']}, LLM response: {response_content}",
            )

        except Exception as e:
            print(
                f"test_langgraph_image_analysis_generation: Test failed with error: {str(e)}"
            )
            raise

    def test_langgraph_spot_difference(self):
        """測試圖片比對功能，檢查重點：
        1. 是否能正確分析兩張找不同遊戲的圖片
        2. 是否能找出並明確描述出兩張圖片的不同之處
        """

        current_dir = Path(__file__).parent
        image1_path = current_dir / "test_files" / "spot_difference_1.png"
        image2_path = current_dir / "test_files" / "spot_difference_2.png"

        # 確保檔案存在
        self.assertTrue(image1_path.exists(), f"Test file not found at {image1_path}")
        self.assertTrue(image2_path.exists(), f"Test file not found at {image2_path}")

        # 將絕對路徑轉為字串
        image1_path_str = str(image1_path)
        image2_path_str = str(image2_path)

        # 上傳檔案到 tmp_public_url
        tmp_public_url_1 = upload_and_get_tmp_public_url(
            image1_path_str,
            "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
            "sebastian.hsu@gmail.com",
        )
        tmp_public_url_2 = upload_and_get_tmp_public_url(
            image2_path_str,
            "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
            "sebastian.hsu@gmail.com",
        )

        # Test payload
        payload = {
            "graph_name": "langgraph_react_agent",
            "messages": [
                {
                    "role": "user",
                    "content": f"這是一個找不同的遊戲，幫我分析兩張圖有幾處不同？ {tmp_public_url_1}，{tmp_public_url_2}",
                }
            ],
            "config": {
                "system_prompt": "回答後你都會在結尾講個笑話，並加上 emoji",
                "botrun_flow_lang_url": "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
                "user_id": "sebastian.hsu@gmail.com",
            },
        }

        # Make the request
        endpoint = "/api/langgraph/invoke"
        print(f"\nTesting API: {self.base_url}{endpoint}")
        print("-" * 50)

        try:
            response = self.api_post(endpoint, payload)

            # Basic assertions to verify the response
            self.assertIsNotNone(response)

            # Extract the content field from the response
            if "content" in response:
                response_content = response["content"]
            else:
                self.fail("Response does not contain 'content' field")

            # Define validation criteria
            validation_criteria = """
            請確認回應是否符合以下條件：
            1. 回應中有具體指出並描述兩張圖片之間的不同之處
            2. 必須明確描述出不同的位置、形狀、顏色或其他特徵差異
            3. 不能只回應「無法處理」、「無法比較」或類似的無能力陳述
            4. 是否在回答結尾包含一個笑話
            
            關鍵是要確保系統能夠實際找出差異並清楚描述，而不是迴避任務或宣稱無法完成。
            如果回應只是說明系統不支援圖片比較功能，則測試視為失敗。
            """

            # Validate with LLM
            validation_result = self.validate_with_llm(
                response_content, validation_criteria
            )

            # Assert that the validation passed
            self.assertTrue(
                validation_result["pass"],
                f"LLM validation failed in {self._testMethodName}: {validation_result['reason']}, LLM response: {response_content}",
            )

        except Exception as e:
            print(f"test_langgraph_spot_difference: Test failed with error: {str(e)}")
            raise

    def test_langgraph_platform_images_analysis(self):
        """測試分析多張車站月台圖片功能，檢查重點：
        1. 是否能正確分析多張車站月台圖片
        2. 是否能根據圖片提供清晰的月台指引和理由
        3. 回覆中是否包含「月台」相關的特定字眼
        """

        current_dir = Path(__file__).parent
        image1_path = current_dir / "test_files" / "ImportedPhoto.760363950.029251.jpeg"
        image2_path = current_dir / "test_files" / "ImportedPhoto.760363950.031127.jpeg"
        image3_path = current_dir / "test_files" / "ImportedPhoto.760363950.030446.jpeg"

        # 確保檔案存在
        self.assertTrue(image1_path.exists(), f"Test file not found at {image1_path}")
        self.assertTrue(image2_path.exists(), f"Test file not found at {image2_path}")
        self.assertTrue(image3_path.exists(), f"Test file not found at {image3_path}")

        # 將絕對路徑轉為字串
        image1_path_str = str(image1_path)
        image2_path_str = str(image2_path)
        image3_path_str = str(image3_path)

        # 上傳檔案到 tmp_public_url
        tmp_public_url_1 = upload_and_get_tmp_public_url(
            image1_path_str,
            "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
            "sebastian.hsu@gmail.com",
        )
        tmp_public_url_2 = upload_and_get_tmp_public_url(
            image2_path_str,
            "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
            "sebastian.hsu@gmail.com",
        )
        tmp_public_url_3 = upload_and_get_tmp_public_url(
            image3_path_str,
            "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
            "sebastian.hsu@gmail.com",
        )

        # Test payload
        payload = {
            "graph_name": "langgraph_react_agent",
            "messages": [
                {
                    "role": "system",
                    "content": "妳是臺灣人，回答要用臺灣繁體中文正式用語，需要的時候也可以用英文，可以親切、俏皮、幽默，但不能隨便輕浮。在使用者合理的要求下請盡量配合他的需求，不要隨便拒絕。",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"以下為使用者上傳的圖片，請參考這些圖片回答使用者的問題：\n\n{tmp_public_url_1}\n{tmp_public_url_2}\n{tmp_public_url_3}\n\n使用者問題：\n\n我要去哪個月台，為什麼？",
                        }
                    ],
                },
            ],
            "config": {
                "botrun_flow_lang_url": "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
                "user_id": "sebastian.hsu@gmail.com",
            },
        }

        # Make the request
        endpoint = "/api/langgraph/invoke"
        print(f"\nTesting API: {self.base_url}{endpoint}")
        print("-" * 50)

        try:
            response = self.api_post(endpoint, payload)

            # Basic assertions to verify the response
            self.assertIsNotNone(response)

            # Extract the content field from the response
            if "content" in response:
                response_content = response["content"]
            else:
                self.fail("Response does not contain 'content' field")

            # Define validation criteria
            validation_criteria = """
            請確認回應是否符合以下條件：
            1. 回應中有明確提及「月台」、「站台」或「platform」等相關詞彙
            2. 回應中有具體指出一個明確的月台方向或號碼，尤其應該包含以下月台號碼其中之一：
               - 5 A-C
               - 5 D-F
               - 5-A-C
               - 5-A/C
               - 5-D-F
               - 5-D/F
            3. 回應中提供了選擇該月台的理由或依據（例如目的地、車次、方向等）
            4. 回應使用了臺灣繁體中文正式用語
            
            回應必須能清楚指引使用者應該前往哪個月台，以及為什麼要去那個月台。如果回應中缺少明確的月台指引或理由，則視為測試失敗。
            """

            # Validate with LLM
            validation_result = self.validate_with_llm(
                response_content, validation_criteria
            )

            # Assert that the validation passed
            self.assertTrue(
                validation_result["pass"],
                f"LLM validation failed in {self._testMethodName}: {validation_result['reason']}, LLM response: {response_content}",
            )

            # Additional check for specific platform numbers
            possible_platforms = ["5 A-C", "5 D-F", "5-A-C", "5-A/C", "5-D-F", "5-D/F"]
            platform_found = False

            for platform in possible_platforms:
                if platform in response_content:
                    platform_found = True
                    print(f"Found expected platform: {platform}")
                    break

            self.assertTrue(
                platform_found,
                f"Response does not contain any of the expected platform numbers: {possible_platforms}, but get {response_content}",
            )

        except Exception as e:
            print(
                f"test_langgraph_platform_images_analysis: Test failed with error: {str(e)}"
            )
            raise

    def test_langgraph_population_analysis(self):
        """測試PDF人口分析與圖表生成功能，檢查重點：
        1. 是否能正確分析PDF中各縣市的人口數據
        2. 是否生成相關的比較圖表並提供Google Storage URL
        """

        current_dir = Path(__file__).parent
        pdf_path = (
            current_dir
            / "test_files"
            / "11206_10808人口數(3段年齡組+比率)天下雜誌1.pdf"
        )

        # 確保檔案存在
        self.assertTrue(pdf_path.exists(), f"Test file not found at {pdf_path}")

        # 將絕對路徑轉為字串
        pdf_path_str = str(pdf_path)
        tmp_public_url = upload_and_get_tmp_public_url(
            pdf_path_str,
            "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
            "sebastian.hsu@gmail.com",
        )

        # Test payload
        payload = {
            "graph_name": "langgraph_react_agent",
            "messages": [
                {
                    "role": "user",
                    "content": f"{tmp_public_url} 幫我分析這個檔案，做深度的人口狀況分析，然後產出一個相關的比較圖表給我看。",
                }
            ],
            "config": {
                "system_prompt": "回答後你都會在結尾講個笑話，並加上 emoji",
                "botrun_flow_lang_url": "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
                "user_id": "sebastian.hsu@gmail.com",
            },
        }

        # Make the request
        endpoint = "/api/langgraph/invoke"
        print(f"\nTesting API: {self.base_url}{endpoint}")
        print("-" * 50)

        try:
            response = self.api_post(endpoint, payload)

            # Basic assertions to verify the response
            self.assertIsNotNone(response)

            # Extract the content field from the response
            if "content" in response:
                response_content = response["content"]
            else:
                self.fail("Response does not contain 'content' field")

            # Define validation criteria
            validation_criteria = """
            請確認回應是否符合以下條件：
            1. 回應中有包含各縣市的人口數據分析，至少提及三個以上的縣市名稱及其人口狀況
            2. 回應中包含至少一個以 "https://storage.googleapis.com" 開頭的URL，這個URL應該指向一個生成的圖表
            3. 分析內容應該涵蓋人口結構的深度分析，例如年齡分布、老化指數、人口增減等
            4. 是否在回答結尾包含一個笑話
            
            所有條件都必須滿足，特別是必須有各縣市的人口分析並含有Google Storage的圖表URL。
            """

            # Validate with LLM
            validation_result = self.validate_with_llm(
                response_content, validation_criteria
            )

            # Assert that the validation passed
            self.assertTrue(
                validation_result["pass"],
                f"LLM validation failed in {self._testMethodName}: {validation_result['reason']}, LLM response: {response_content}",
            )

            # Additional check for Google Storage URL
            self.assertTrue(
                "https://storage.googleapis.com" in response_content,
                "Response does not contain a Google Storage URL",
            )

        except Exception as e:
            print(
                f"test_langgraph_population_analysis: Test failed with error: {str(e)}"
            )
            raise

    def test_langgraph_wind_power_flowchart(self):
        """測試風力發電計畫PDF分析與流程圖生成功能，檢查重點：
        1. 是否能正確分析PDF中的風力發電計畫內容
        2. 是否生成相關的流程圖並提供Google Storage URL
        """

        current_dir = Path(__file__).parent
        pdf_path = (
            current_dir
            / "test_files"
            / "1120701A海廣離岸風力發電計畫環境影響說明書-C04.PDF"
        )

        # 確保檔案存在
        self.assertTrue(pdf_path.exists(), f"Test file not found at {pdf_path}")

        # 將絕對路徑轉為字串
        pdf_path_str = str(pdf_path)
        tmp_public_url = upload_and_get_tmp_public_url(
            pdf_path_str,
            "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
            "sebastian.hsu@gmail.com",
        )

        # Test payload
        payload = {
            "graph_name": "langgraph_react_agent",
            "messages": [
                {
                    "role": "user",
                    "content": f"{tmp_public_url} 幫我分析這個檔案，針對風力發電計畫，生成一張流程圖給我。",
                }
            ],
            "config": {
                "system_prompt": "回答後你都會在結尾講個笑話，並加上 emoji",
                "botrun_flow_lang_url": "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
                "user_id": "sebastian.hsu@gmail.com",
            },
        }

        # Make the request
        endpoint = "/api/langgraph/invoke"
        print(f"\nTesting API: {self.base_url}{endpoint}")
        print("-" * 50)

        try:
            response = self.api_post(endpoint, payload)

            # Basic assertions to verify the response
            self.assertIsNotNone(response)

            # Extract the content field from the response
            if "content" in response:
                response_content = response["content"]
            else:
                self.fail("Response does not contain 'content' field")

            # Define validation criteria
            validation_criteria = """
            請確認回應是否符合以下條件：
            1. 回應中有包含風力發電計畫的分析內容，例如計畫目標、執行步驟、環境影響等
            2. 回應中包含至少一個以 "https://storage.googleapis.com" 開頭的URL，這個URL應該指向一個生成的流程圖
            3. 分析內容應該專注於風力發電計畫的程序或流程，而非僅是一般性描述
            4. 是否在回答結尾包含一個笑話
            
            所有條件都必須滿足，特別是必須有風力發電計畫的分析並含有Google Storage的流程圖URL。
            """

            # Validate with LLM
            validation_result = self.validate_with_llm(
                response_content, validation_criteria
            )

            # Assert that the validation passed
            self.assertTrue(
                validation_result["pass"],
                f"LLM validation failed in {self._testMethodName}: {validation_result['reason']}, LLM response: {response_content}",
            )

            # Additional check for Google Storage URL
            self.assertTrue(
                "https://storage.googleapis.com" in response_content,
                "Response does not contain a Google Storage URL",
            )

        except Exception as e:
            print(
                f"test_langgraph_wind_power_flowchart: Test failed with error: {str(e)}"
            )
            raise

    def test_langgraph_oauth_flow_diagram(self):
        """測試OAuth流程圖生成功能，檢查重點：
        1. 是否能正確生成OAuth認證流程圖
        2. 是否提供Google Storage URL連結到生成的圖表
        """
        # Test payload based on the curl command
        payload = {
            "graph_name": "langgraph_react_agent",
            "messages": [
                {
                    "role": "user",
                    "content": "我想做一個 oauth 的流程，幫我生出一個流程表",
                }
            ],
            "config": {
                "system_prompt": "回答後你都會在結尾講個笑話，並加上 emoji",
                "botrun_flow_lang_url": "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
                "user_id": "sebastian.hsu@gmail.com",
            },
        }

        # Make the request
        endpoint = "/api/langgraph/invoke"
        print(f"\nTesting API: {self.base_url}{endpoint}")
        print("-" * 50)

        try:
            response = self.api_post(endpoint, payload)

            # Basic assertions to verify the response
            self.assertIsNotNone(response)

            # Extract the content field from the response
            if "content" in response:
                response_content = response["content"]
            else:
                self.fail("Response does not contain 'content' field")

            # Define validation criteria
            validation_criteria = """
            請確認回應是否符合以下條件：
            1. 回應中有詳細描述OAuth認證流程的步驟，必須包含關鍵步驟如授權請求、令牌交換等
            2. 回應中包含至少一個以 "https://storage.googleapis.com" 開頭的URL，這個URL應該指向一個生成的流程圖
            3. 回應應該提供清晰的OAuth流程解釋，包括不同參與者（如用戶、客戶端應用、授權伺服器等）之間的互動
            4. 是否在回答結尾包含一個笑話
            
            所有條件都必須滿足，特別是必須有OAuth流程的詳細描述，並含有Google Storage的流程圖URL。
            """

            # Validate with LLM
            validation_result = self.validate_with_llm(
                response_content, validation_criteria
            )

            # Assert that the validation passed
            self.assertTrue(
                validation_result["pass"],
                f"LLM validation failed in {self._testMethodName}: {validation_result['reason']}, LLM response: {response_content}",
            )

            # Additional check for Google Storage URL
            self.assertTrue(
                "https://storage.googleapis.com" in response_content,
                "Response does not contain a Google Storage URL",
            )

        except Exception as e:
            print(
                f"test_langgraph_oauth_flow_diagram: Test failed with error: {str(e)}"
            )
            raise

    def test_langgraph_moda_news_dall_e(self):
        """測試多節點處理數位發展部新聞流程，檢查重點：
        1. 是否會抓到今天日期，或截至今天日期的數位發展部相關新聞
        2. 是否有評分新聞 (1-10分)，並標示出「最可愛」的新聞
        3. 是否有產出一張圖片，並帶有 URL
        """
        # Test payload based on the curl command
        payload = {
            "graph_name": "langgraph_react_agent",
            "messages": [
                {
                    "role": "user",
                    "content": "好，那個你幫我那個啟動幾個多個節點,然後第一個節點請你幫我上網搜尋。 上網搜尋今天那個我們那個數位發展部的夥伴,或者最近一個禮拜數位發展部的那個夥伴有沒有什麼新聞好。 然後第二個節點,你幫我做一件事,你幫我做幫我把這些新聞評分數,評分一到十分。 那哪個新聞你覺得最可愛。 然後第三個節點,你幫我做一件事。 就是你把這個分數最可愛的那一個新聞挑出來以後,你幫我生成一個prompt,這個prompt是我要把你丟進打理畫圖用的prompt。那第四個節點你才真的呼叫打理把那個圖給畫出來,你幫我依序執行這個這個工作流程好不好,謝謝。",
                }
            ],
            "config": {
                "system_prompt": "回答後你都會在結尾講個笑話，並加上 emoji",
                "botrun_flow_lang_url": "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
                "user_id": "sebastian.hsu@gmail.com",
            },
        }

        # Make the request
        endpoint = "/api/langgraph/invoke"
        print(f"\nTesting API: {self.base_url}{endpoint}")
        print("-" * 50)

        try:
            response = self.api_post(endpoint, payload)

            # Basic assertions to verify the response
            self.assertIsNotNone(response)

            # Extract the content field from the response
            if "content" in response:
                response_content = response["content"]
            else:
                self.fail("Response does not contain 'content' field")

            # Define validation criteria based on the test requirements
            validation_criteria = f"""
            請確認回應是否符合以下條件：
            1. 回應中有包含今天({self.local_time.strftime("%Y-%m-%d")})或最近一週內的數位發展部相關新聞資訊
            2. 回應中有對新聞進行1-10分的評分，並明確指出哪則新聞「最可愛」或分數最高
            3. 回應中包含至少一個圖片URL（通常是以http或https開頭的網址）
            4. 是否在回答結尾包含一個笑話
            
            所有條件都必須滿足，特別是必須有數位發展部相關新聞、評分結果以及最終生成的圖片URL。
            """

            # Validate with LLM
            validation_result = self.validate_with_llm(
                response_content, validation_criteria
            )

            # Assert that the validation passed
            self.assertTrue(
                validation_result["pass"],
                f"LLM validation failed in {self._testMethodName}: {validation_result['reason']}, LLM response: {response_content}",
            )

            # Additional check for an image URL
            self.assertTrue(
                "http" in response_content.lower()
                and (
                    "jpg" in response_content.lower()
                    or "png" in response_content.lower()
                    or "https://storage.googleapis.com" in response_content
                ),
                "Response does not contain a valid image URL",
            )

        except Exception as e:
            print(f"test_langgraph_moda_news_dall_e: Test failed with error: {str(e)}")
            raise

    def test_langgraph_global_disaster_news(self):
        """測試深度研究災難新聞流程，檢查重點：
        1. 是否有收集全球災難新聞
        2. 是否以表格方式呈現災難資料
        3. 是否提供新聞來源
        """
        # Test payload based on the curl command
        payload = {
            "graph_name": "langgraph_react_agent",
            "messages": [
                {
                    "role": "user",
                    "content": "請幫我進行深度研究，深度研究時請遵循以下三個步驟\n第一步驟：\n身為一個專業的全球新聞蒐集分析人員，請透過網路幫我收集Google News、路透社、美聯社、CNN、BBC、法新社、歐洲傳媒應急中心、公共透視網路、台灣聯合報及東森新聞，不使用不可信賴媒體及模擬資料，盡力確保可收集到全球的災難新聞。產生的研究報告文件名稱請以「xxxx年xx月xx日 全球災難新聞收集與追蹤」這樣的格式生成。收集時間請以UTC+8時區為基準，收集從2025年2月24日15:00到2025年2月25日15:00 的24 小時內，全球在時區內發生的災難事件及發生時間，包括大型自然災害或人為災難的人數統計，包括「傷亡」、「失蹤」、「受影響」、「流離失所」、「避難」等。自然災難類型包括但不限於地震、風災、火山爆發、寒流、大雪、冰雹、雪崩、土石流、野火、山火之類的極端氣候災難，人為災害包括 空難、戰爭、大型交通事故、海難、建物倒塌、疫情、中毒等並整理成表格，以繁體中文輸出，表格名請加上當天的年月日，格式為「xxxx年xx月xx日」並按照亞洲、歐洲、美洲、大洋洲、非洲等五大洲排列，後面要加上國家、省市別做完整地點呈現\n第二個表格請搜集以2025年2月24日為基準過去 96 小時的全球新聞中的災難報導。請確認事件發生時間在區間內，若是非區間內發生，請在說明欄清楚說明原因。並再三確認報導更新時間是否在區間內，也就是從前三天到當天，四天中發生的災難後續報導。\n第三個表格請就第一和第二個表格中收集到的災難事件中，逐條就每個災難進行250字的災難摘要及資料來源連結。並收集有關房屋（棟）的損壞統計，包括「受損」、「毁損」等。請務必以表格呈現，不要逐條展示。\n第二步驟：\n我要復盤上述資料都來自於可信賴的國際或台灣新聞媒體即時新聞報導，並且要找到三個不同的資訊來源，交差比對確認災難真實發生的時間點。第一個表格要有詳細的災難發生地點，每條災難收集的時間條件是指災難發生時間而非新聞發布時間在時間區間內，若災難發生時間不在時間區間內，請移到第二個表格。第二個表格是在過去96個小時不重複第一個表格的時間區間中新聞媒體對於災難的後續報導，第三個部份也請用表格呈現，而不是條列式。請檢視每個表格的災難資料，並合併相同的災難事件，確保每條事件只有一筆， 我很怕你使用到不可信的網路媒體資料，如：維基百科或是災難預言、天氣預警、模擬訊息或是你預訓練的資料Youtube及專題報導等。 若無傷亡或防屋毀損實際統計數據，請勿收集。\n第三步驟：\n請將下列附加檔案的表格一和表格二匯的每條災難事件透過網路可信賴媒體交叉比對時間和真實性後，匯整到原有的表格一和二中並合併相同的災難資訊，重新整理完整的表格三。再重新檢查每筆資料都符合各表格的時間區間及規範，重新盤點100遍，幫我整理出最完整的表格一到三。每筆資料請幫我再三搜尋可信賴媒體進行交差比對，務求每條事件都在真實世界中發生，地點明確，發生時間可驗證，若無傷亡資料就不收集。要確認表格一加上表格二的條目，能完整在表格三中呈現，不可多也不可少。",
                }
            ],
            "config": {
                "system_prompt": "回答後你都會在結尾講個笑話，並加上 emoji",
                "botrun_flow_lang_url": "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
                "user_id": "sebastian.hsu@gmail.com",
            },
        }

        # Make the request
        endpoint = "/api/langgraph/invoke"
        print(f"\nTesting API: {self.base_url}{endpoint}")
        print("-" * 50)

        try:
            response = self.api_post(endpoint, payload)

            # Basic assertions to verify the response
            self.assertIsNotNone(response)

            # Extract the content field from the response
            if "content" in response:
                response_content = response["content"]
            else:
                self.fail("Response does not contain 'content' field")

            # Define validation criteria based on the test requirements
            validation_criteria = """
            請確認回應是否符合以下條件：
            1. 回應中包含災難新聞信息（至少提到了一些具體災難事件）
            2. 回應中有表格呈現（HTML表格標籤或是文字表格形式呈現災難數據）
            3. 回應中提供了新聞來源（至少包含一個可識別的媒體來源名稱如CNN、BBC、路透社等）
            4. 回應中有提及災難事件的類型（自然災害或人為災害）
            5. 回應中有提及災難事件的地理位置（國家、城市等）
            6. 回應中是否在結尾包含一個笑話
            
            所有條件都必須滿足，特別是必須有災難新聞、表格呈現方式及新聞來源引用。
            """

            # Validate with LLM
            validation_result = self.validate_with_llm(
                response_content, validation_criteria
            )

            # Assert that the validation passed
            self.assertTrue(
                validation_result["pass"],
                f"LLM validation failed in {self._testMethodName}: {validation_result['reason']}, LLM response: {response_content}",
            )

            # Additional checks for tables and sources
            self.assertTrue(
                "|" in response_content
                or "<table" in response_content.lower()
                or "表格" in response_content,
                "Response does not appear to contain any tables",
            )

            # # Check for news sources
            # news_sources = [
            #     "CNN",
            #     "BBC",
            #     "路透社",
            #     "美聯社",
            #     "法新社",
            #     "聯合報",
            #     "東森",
            # ]
            # sources_found = any(source in response_content for source in news_sources)
            # self.assertTrue(
            #     sources_found,
            #     "Response does not reference any recognizable news sources",
            # )

        except Exception as e:
            print(
                f"test_langgraph_global_disaster_news: Test failed with error: {str(e)}"
            )
            raise

    def test_langgraph_global_disaster_news_can_cause_25_limites(self):
        """測試深度研究災難新聞流程，檢查重點：
        1. 確認是否不會回應執行 LangGraph 時發生錯誤
        """
        # todo 壓力測試這個項目先拿掉
        return
        # Test payload based on the curl command
        payload = {
            "graph_name": "langgraph_react_agent",
            "messages": [
                {
                    "role": "user",
                    "content": "身為一個專業的全球新聞蒐集分析人員，請透過網路幫我收集Google News、路透社、美聯社、CNN、BBC、法新社、歐洲傳媒應急中心、公共透視網路、台灣聯合報及東森新聞，不使用不可信賴媒體及模擬資料，請你用英文進行搜尋，用日文進行搜尋，用韓文進行搜尋，並且搜尋的範圍要全球，要多國語言，盡力確保可收集到全球的災難新聞，但最終產出結果請以繁體中文呈現。\n產生的研究報告文件名稱請以「xxxx年xx月xx日 全球災難新聞收集與追蹤」這樣的格式生成。收集時間請以UTC+8時區為基準，收集從2025年2月25日15:00到2025年2月26日15:00 的24 小時內，全球在時區內發生的災難事件及發生時間，包括大型自然災害或人為災難的人數統計，包括「傷亡」、「失蹤」、「受影響」、「流離失所」、「避難」等。自然災難類型包括但不限於地震、風災、火山爆發、寒流、大雪、冰雹、雪崩、土石流、野火、山火之類的極端氣候災難，人為災害包括 空難、戰爭、大型交通事故、海難、建物倒塌、疫情、中毒等並整理成表格，以繁體中文輸出，表格名請加上當天的年月日，格式為「xxxx年xx月xx日」並按照亞洲、歐洲、美洲、大洋洲、非洲等五大洲排列，後面要加上國家、省市別做完整地點呈現\n第二個表格請搜集以2025年2月25日為基準過去 96 小時的全球新聞中的災難報導。請確認事件發生時間在區間內，若是非區間內發生，請在說明欄清楚說明原因。並再三確認報導更新時間是否在區間內，也就是從前三天到當天，四天中發生的災難後續報導。\n第三個表格請就第一和第二個表格中收集到的災難事件中，請就你收集到的災難事件經要彙整，最終我希望產出以下的表格標題內容要涵蓋這些欄位\n災害類型\n洲別\n國家\n地區\n災難日期\n災情摘要（約250個字）\n受影響人數\n房屋損毀(棟)\n芮氏規模\n震源深度(公里)\n颱風名稱\n颱風級數\n資料來源（要附上超連結）\n請務必以表格直接回覆呈現給我，不要逐條展示，不要做成 html。",
                },
                {
                    "role": "assistant",
                    "content": "我理解您需要一份全球災難新聞的收集與分析報告。為了取得最新的災難新聞資訊，我需要先確認當前時間，然後進行全球範圍的新聞搜尋。\n\n感謝您的請求。我注意到您希望收集的時間範圍是「2025年2月25日15:00到2025年2月26日15:00」的24小時內的災難事件。由於現在是2025年2月27日，這個時間範圍是在過去的時間，我將進行相關搜尋。\n\n我將使用網路搜尋工具來收集全球災難新聞，並按照您的要求進行整理。我會使用多種語言進行搜尋，以確保能夠收集到全球範圍內的災難新聞。\n\n首先，讓我用英文搜尋全球災難新聞：\n\n現在讓我用日文搜尋全球災難新聞：\n現在讓我用韓文搜尋全球災難新聞：\n現在讓我搜尋臺灣的災難新聞：\n現在讓我搜尋中國的災難新聞：\n現在讓我搜尋歐洲的災難新聞：\n現在讓我搜尋美洲的災難新聞：\n現在讓我搜尋非洲的災難新聞：\n最後讓我搜尋大洋洲的災難新聞：\n\n現在，我將根據收集到的資訊，整理成您要求的報告格式：\n\n# 2025年02月27日 全球災難新聞收集與追蹤\n\n## 表格一：2025年2月25日15:00至2025年2月26日15:00全球災難事件\n\n### 2025年02月26日\n\n| 洲別 | 國家 | 省市別 | 災難類型 | 傷亡 | 失蹤 | 受影響 | 流離失所 | 避難 |\n|------|------|--------|----------|------|------|--------|----------|------|\n| 亞洲 | 日本 | 巖手縣 | 地震 | 0 | 0 | 未知 | 0 | 0 |\n| 亞洲 | 日本 | 巖手縣 | 山林火災 | 1 | 0 | 未知 | 0 | 546 |\n| 亞洲 | 日本 | 山梨縣 | 山林火災 | 0 | 0 | 未知 | 0 | 未知 |\n| 亞洲 | 韓國 | 仁川市 | 住宅火災 | 1 | 0 | 1 | 0 | 0 |\n| 亞洲 | 韓國 | 京畿道/忠北 | 山林火災 | 0 | 0 | 未知 | 0 | 未知 |\n| 亞洲 | 臺灣 | 新北市 | 工廠火災 | 0 | 0 | 未知 | 0 | 0 |\n| 亞洲 | 臺灣 | 臺南 | 海纜事故 | 0 | 0 | 未知 | 0 | 0 |\n| 亞洲 | 臺灣 | 彰化縣 | 交通事故 | 2 | 0 | 0 | 0 | 0 |\n| 歐洲 | 希臘 | 多德卡尼斯群島 | 地震活動 | 0 | 0 | 未知 | 0 | 0 |\n| 美洲 | 美國 | 肯塔基州 | 洪水 | 14 | 未知 | 未知 | 未知 | 未知 |\n| 美洲 | 美國 | 華盛頓/俄勒岡州 | 大氣河流 | 0 | 0 | 未知 | 0 | 0 |\n| 美洲 | 美國 | 加州 | 交通事故 | 2 | 0 | 未知 | 0 | 0 |\n| 非洲 | 南非 | 誇祖魯-納塔爾省 | 洪水/山崩 | 9 | 0 | 未知 | 未知 | 未知 |\n| 非洲 | 南非 | 多地區 | 洪水 | 0 | 0 | 未知 | 0 | 0 |\n| 大洋洲 | 澳洲 | 昆士蘭州 | 洪水後疫情 | 12 | 0 | 1,700戶 | 未知 | 未知 |\n| 大洋洲 | 澳洲 | 西澳州 | 熱帶氣旋 | 0 | 0 | 未知 | 0 | 未知 |\n| 大洋洲 | 湯加 | 'Ohonua | 地震 | 0 | 0 | 0 | 0 | 0 |\n\n## 表格二：2025年2月22日至2025年2月25日全球災難報導\n\n| 洲別 | 國家 | 省市別 | 災難類型 | 發生時間 | 報導更新時間 | 說明 |\n|------|------|--------|----------|----------|--------------|------|\n| 亞洲 | 日本 | 本州南岸近海 | 地震 | 2025/02/26 | 2025/02/26 | 5.8級地震，震源深度400公里 |\n| 亞洲 | 韓國 | 釜山 | 飯店火災 | 2025/02/14 | 2025/02/27 | 安全管理不當導致6死27傷，調查持續進行中 |\n| 亞洲 | 臺灣 | 臺南 | 海纜事故 | 2025/02/25 | 2025/02/25 | 臺澎三號海纜全斷，疑似多哥籍貨輪「宏泰」所為 |\n| 亞洲 | 馬爾地夫 | 全國 | 氣候應對 | 2025/02中旬 | 2025/02/25 | 使用無人機進行防災管理，應對海平面上升威脅 |\n| 歐洲 | 義大利 | 坎皮弗萊格雷 | 地震群 | 2025/02/05-17 | 2025/02/25 | 超過200次地震，規模1.5-3.9 |\n| 美洲 | 美國 | 太平洋西北部 | 大氣河流 | 2025/02/22 | 2025/02/25 | 大氣河流帶來強降雨，引發洪水風險 |\n| 美洲 | 美國 | 阿帕拉契亞 | 洪水 | 2025/02/15-16 | 2025/02/26 | 中期風暴造成致命洪水，18人死亡 |\n| 非洲 | 波札那 | 哈博羅內 | 洪水 | 2025/02/16-21 | 2025/02/21 | 強降雨導致4人死亡，多人流離失所 |\n| 非洲 | 衣索比亞 | 芬塔萊火山附近 | 地震 | 2025/02/14 | 2025/02/25 | 6.0級地震，震源淺 |\n| 大洋洲 | 澳洲 | 昆士蘭州北部 | 洪水 | 2025/02/02 | 2025/02/25 | 極端降雨導致嚴重洪水，48小時內降雨量達1,000毫米 |\n\n## 表格三：全球災難事件彙整\n\n| 災害類型 | 洲別 | 國家 | 地區 | 災難日期 | 災情摘要 | 受影響人數 | 房屋損毀(棟) | 芮氏規模 | 震源深度(公里) | 颱風名稱 | 颱風級數 | 資料來源 |\n|----------|------|------|------|----------|----------|------------|--------------|----------|--------------|----------|----------|----------|\n| 地震 | 亞洲 | 日本 | 巖手縣近海 | 2025/02/26 | 規模4.3地震，最大震度1級，無海嘯風險 | 未知 | 0 | 4.3 | 30 | - | - | [日本雅虎天氣](https://emergency-weather.yahoo.co.jp/weather/zh-TW/earthquake/20250226082302/) |\n| 地震 | 大洋洲 | 湯加 | 'Ohonua南方 | 2025/02/25 | 里氏4.8級地震，未引發海嘯警報，無重大損失報告 | 0 | 0 | 4.8 | 10 | - | - | [SMS海嘯警報](https://www.sms-tsunami-warning.com/earthquakes-today/us6000pvc9/%E2%80%98Ohonua-Tonga/25-02-2025) |\n| 山林火災 | 亞洲 | 日本 | 巖手縣沿海 | 2025/02/25-26 | 火勢起源於居民焚燒垃圾失控，西風助長下延燒8公頃林地，大船渡市與陸前高田市共疏散546人 | 546+ | 84 | - | - | - | - | [中國新聞網](https://www.chinanews.com.cn/gj/2025/02-26/10374234.shtml) |\n| 山林火災 | 亞洲 | 日本 | 山梨縣北杜市 | 2025/02/25-27 | 發生於須玉町山林，延燒面積達8.5公頃（約東京巨蛋1.8倍），27日上午11時確認鎮火 | 未知 | 0 | - | - | - | - | [TBS新聞](https://newsdig.tbs.co.jp/articles/-/1755507) |\n| 住宅火災 | 亞洲 | 韓國 | 仁川市 | 2025/02/26 | 仁川美秀區1層住宅發生火災，70多歲男性死亡，60多歲女性受傷，疑似行動不便者未能及時逃生 | 2 | 1 | - | - | - | - | [YouTube](https://www.youtube.com/watch?v=ME6m2jZlwik) |\n| 山林火災 | 亞洲 | 韓國 | 京畿道/忠北 | 2025/02/26 | 乾燥天氣影響下，京畿光州和忠北鎮川發生山林火災，具體損失規模未確認 | 未知 | 未知 | - | - | - | - | [YouTube](https://www.youtube.com/watch?v=ME6m2jZlwik) |\n| 工廠火災 | 亞洲 | 臺灣 | 新北市五股區 | 2025/02/26 | 民義路二段一處工廠起火燃燒，濃煙直竄天際。消防局出動48車、111人撲救，火勢於7時15分撲滅 | 未知 | 未知 | - | - | - | - | [中央通訊社](https://www.cna.com.tw/news/asoc/202502260389.aspx) |\n| 海纜事故 | 亞洲 | 臺灣 | 臺南 | 2025/02/25 | 臺澎三號海纜全斷，海巡署監控到多哥籍貨輪「宏泰」滯留海域並下錨，疑似拖斷海纜 | 未知 | 0 | - | - | - | - | [iThome](https://www.ithome.com.tw/news/167548) |\n| 交通事故 | 亞洲 | 臺灣 | 彰化縣 | 2025/02/25 | 彰化139線大彰路發生兩起車禍，一名騎士因閃避車輛失控衝撞後噴飛受傷，同日晚間同一路段再發生第二起事故 | 2 | 0 | - | - | - | - | [ProNews](https://pronews.tw/2025/02/26/122949/) |\n| 洪水/山崩 | 非洲 | 南非 | 誇祖魯-納塔爾省 | 2025/02/25 | 德班地區發生山崩和洪水，Folweni、Demat和Ensimbini地區至少9人死亡 | 9+ | 未知 | - | - | - | - | [ReliefWeb](https://reliefweb.int/report/south-africa/south-africa-landslides-and-floods-noaa-cpc-media-echo-daily-flash-25-february-2025) |\n| 洪水 | 非洲 | 南非 | 多地區 | 2025/02/25 | Vaal河沿岸Bothaville和Leeudoringstad之間發生嚴重洪水，Midmar水壩溢流，Thabazimbi-Buisdoorens和比勒陀利亞N1高速公路被淹沒 | 未知 | 未知 | - | - | - | - | [YouTube](https://www.youtube.com/watch?v=otXnWTK-FjQ) |\n| 洪水後疫情 | 大洋洲 | 澳洲 | 昆士蘭州 | 2025/02/25 | 持續洪水導致類鼻疽病爆發，已造成12人死亡。與2月初北昆士蘭創紀錄降雨引發的長期積水有關 | 12+ | 1,700 | - | - | - | - | [維基百科](https://en.wikipedia.org/wiki/Portal:Current_events/2025_February_25) |\n| 熱帶氣旋 | 大洋洲 | 澳洲 | 西澳州 | 2025/02/25-26 | 熱帶氣旋「阿爾弗雷德」25日達到3級，最大風速150公里/小時，26日降為2級，西澳Pilbara地區發布紅色警報 | 未知 | 未知 | - | - | 阿爾弗雷德 | 2-3級 | [YouTube](https://www.youtube.com/watch?v=gXrhF8gkyv4) |\n| 洪水 | 美洲 | 美國 | 肯塔基州 | 2025/02/15-26 | 嚴重風暴和洪水持續影響，2月26日發佈重大災難宣告，至少14人死亡，冬季天氣進一步複雜化救援行動 | 14+ | 未知 | - | - | - | - | [FEMA](https://www.fema.gov/disaster/declarations) |\n| 大氣河流 | 美洲 | 美國 | 華盛頓/俄勒岡州 | 2025/02/22-26 | 大氣河流在2月22日登陸華盛頓和俄勒岡州，帶來強降雨，融雪增加，河水上漲，引發洪水風險 | 未知 | 未知 | - | - | - | - | [Watchers News](https://watchers.news/2025/02/20/atmospheric-river-forecast-to-make-landfall-over-the-pacific-northwest-on-february-22/) |\n| 交通事故 | 美洲 | 美國 | 加州安納海姆山 | 2025/02/26 | 91號高速公路東向發生多車相撞火災事故，造成2人死亡，事故涵蓋3輛車，發生在Coal Canyon路附近 | 2 | 0 | - | - | - | - | [Arash Law](https://arashlaw.com/02-26-2025-two-people-killed-after-fiery-multi-vehicle-crash-on-91-freeway-in-anaheim-hills/) |\n\n以上是根據您的要求整理的全球災難新聞收集與追蹤報告。報告涵蓋了2025年2月25日15:00至2025年2月26日15:00期間全球發生的主要災難事件，以及前96小時內的相關災難報導。資料來源包括各大國際新聞媒體和官方機構的報導。",
                },
                {
                    "role": "user",
                    "content": "我要復盤上述資料都來自於可信賴的國際或台灣新聞媒體即時新聞報導，並且要找到三個不同的資訊來源，交差比對確認災難真實發生的時間點。第一個表格要有詳細的災難發生地點，每條災難收集的時間條件是指災難發生時間而非新聞發布時間在時間區間內，若災難發生時間不在時間區間內，請移到第二個表格。第二個表格是在過去96個小時不重複第一個表格的時間區間中新聞媒體對於災難的後續報導，第三個部份也請用表格呈現，而不是條列式。請檢視每個表格的災難資料，並合併相同的災難事件，確保每條事件只有一筆， 我很怕你使用到不可信的網路媒體資料，如：維基百科或是災難預言、天氣預警、模擬訊息或是你預訓練的資料Youtube及專題報導等。 若無傷亡或防屋毀損實際統計數據，請勿收集。\n\n最後請幫我以html網頁呈現",
                },
            ],
            "config": {
                "system_prompt": "回答後你都會在結尾講個笑話，並加上 emoji",
                "botrun_flow_lang_url": "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
                "user_id": "sebastian.hsu@gmail.com",
            },
        }

        # Make the request
        endpoint = "/api/langgraph/invoke"
        print(f"\nTesting API: {self.base_url}{endpoint}")
        print("-" * 50)

        try:
            response = self.api_post(endpoint, payload)

            # Basic assertions to verify the response
            self.assertIsNotNone(response)

            # Extract the content field from the response
            if "content" in response:
                response_content = response["content"]
            else:
                self.fail("Response does not contain 'content' field")

            # Define validation criteria based on the test requirements
            validation_criteria = """
                請確認回應是否符合以下條件：
                1. 回應中不會發生錯誤，不會有「執行 LangGraph 時發生錯誤」
                2. 回應中會包含有一個 URL 連結
                """

            # Validate with LLM
            validation_result = self.validate_with_llm(
                response_content, validation_criteria
            )

            # Assert that the validation passed
            self.assertTrue(
                validation_result["pass"],
                f"LLM validation failed in {self._testMethodName}: {validation_result['reason']}, LLM response: {response_content}",
            )

        except Exception as e:
            print(f"{self._testMethodName}: Test failed with error: {str(e)}")
            raise

    def test_langgraph_date_time_comparison(self):
        """測試日期時間比較功能，檢查重點：
        1. 當使用者僅指定日期時間而未明確要求比較時，agent 是否能自動使用 current_date_time 工具獲取當前時間
        2. agent 是否能自動使用 compare_date_time 工具比較指定時間與當前時間
        3. agent 是否能正確判斷指定時間是過去還是未來並提供解釋
        """
        # 共用的系統提示
        system_prompt = "如果使用者的問題中有指定日期時間，不要預設它是未來或過去，一定要先使用 current_date_time 和 compare_date_time 這兩個工具，以取得現在的日期時間並判斷使用者指定的日期時間是過去或未來，然後再進行後續的動作。"

        # 共用的配置
        base_config = {
            "system_prompt": system_prompt,
            "botrun_flow_lang_url": "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
            "user_id": "sebastian.hsu@gmail.com",
        }

        # 測試過去時間
        past_payload = {
            "graph_name": "langgraph_react_agent",
            "messages": [
                {
                    "role": "user",
                    "content": "2020年1月1日發生了什麼重要事件？",
                }
            ],
            "config": base_config,
        }

        # 測試未來時間
        future_payload = {
            "graph_name": "langgraph_react_agent",
            "messages": [
                {
                    "role": "user",
                    "content": "2030年12月31日會有什麼重要活動？",
                }
            ],
            "config": base_config,
        }

        # 測試端點
        endpoint = "/api/langgraph/invoke"
        print(f"\nTesting API: {self.base_url}{endpoint}")
        print("-" * 50)

        try:
            # 測試過去時間
            print("Testing past date comparison...")
            past_response = self.api_post(endpoint, past_payload)
            self.assertIsNotNone(past_response)

            if "content" in past_response:
                past_response_content = past_response["content"]
            else:
                self.fail("Response does not contain 'content' field")

            # 定義過去時間的驗證標準
            past_validation_criteria = """
            請確認回應是否符合以下條件：
            1. 回應中是否提到或暗示 2020年1月1日 是過去的時間
            2. 回應中是否有跡象表明 agent 使用了 current_date_time 工具獲取當前時間（例如提到「根據當前時間」、「現在是...」等）
            3. 回應中是否有跡象表明 agent 使用了 compare_date_time 工具比較時間（例如提到「比較結果」、「早於當前時間」等）
            4. 回應中是否包含關於 2020年1月1日 發生的重要事件的資訊
            """

            # 使用 LLM 驗證
            past_validation_result = self.validate_with_llm(
                past_response_content, past_validation_criteria
            )

            # 驗證結果
            self.assertTrue(
                past_validation_result["pass"],
                f"LLM validation failed for past date in {self._testMethodName}: {past_validation_result['reason']}, LLM response: {past_response_content}",
            )

            # 測試未來時間
            print("Testing future date comparison...")
            future_response = self.api_post(endpoint, future_payload)
            self.assertIsNotNone(future_response)

            if "content" in future_response:
                future_response_content = future_response["content"]
            else:
                self.fail("Response does not contain 'content' field")

            # 定義未來時間的驗證標準
            future_validation_criteria = """
            請確認回應是否符合以下條件：
            1. 回應中是否提到或暗示 2030年12月31日 是未來的時間
            2. 回應中是否有跡象表明 agent 使用了 current_date_time 工具獲取當前時間（例如提到「根據當前時間」、「現在是...」等）
            3. 回應中是否有跡象表明 agent 使用了 compare_date_time 工具比較時間（例如提到「比較結果」、「晚於當前時間」等）
            4. 回應中是否適當地處理了關於未來日期的問題（例如表明無法預測未來具體事件，但可能提供一些合理的推測或建議）
            """

            # 使用 LLM 驗證
            future_validation_result = self.validate_with_llm(
                future_response_content, future_validation_criteria
            )

            # 驗證結果
            self.assertTrue(
                future_validation_result["pass"],
                f"LLM validation failed for future date in {self._testMethodName}: {future_validation_result['reason']}, LLM response: {future_response_content}",
            )

        except Exception as e:
            print(
                f"test_langgraph_date_time_comparison: Test failed with error: {str(e)}"
            )
            raise

    def test_langgraph_react_agent_business_flow(self):
        """Test the langgraph_react_agent with a business flow example."""
        # Test payload
        payload = {
            "graph_name": "langgraph_react_agent",
            "messages": [
                {
                    "role": "user",
                    "content": "我想要請你 給我 一個業務流的範例,我只要三個節點,然後我還要針對這個業務流範例當中的其中中間的一個工作流程,然後來 進行示意,然後我那個工作流程也只需要三個節點,那原因是因為我要做成簡報,這樣子比較清晰容易看懂,那業務流 他是人如何工作的,的,的一個重點,記錄人員互動、決策跟情緒體驗,那也因此在業務流的時候呢,我需要請你幫我畫成使用者旅程地圖,裡面有酷酷點跟笑笑點,對不起,那請你節點幫我增加為五個好,然後再來工作流程的地方,它則是聚焦在任務跟文件,還有系統間的流動,它是一個操作的程序跟規則,那我,我也需要,我要修改前面的說法,要改成五個節點,那業務流是使用使用者旅程庫庫地圖,那工作流程的話,我希望它是一個,也許是一個工作流程程圖,或者是時序圖,然後看你覺得哪一個的表現比較明確,那這個內容呢,我需要以內政部的任何一個轄下的任何一個業務來進行舉例,然後我我想要請你幫我現在畫出來。",
                },
                {
                    "role": "assistant",
                    "content": "**我瞭解您需要一個業務流程的範例，特別是以內政部的業務為例，包含：**\n1. **一個使用者旅程地圖（業務流）- 5個節點，記錄人員互動、決策和情緒體驗**\n2. **一個工作流程程圖或時序圖 - 5個節點，聚焦在任務、文件和系統間的流動**\n**我會先幫您創建這兩個圖表。讓我們以內政部戶政司的「結婚登記」業務為例。**\n**首先，讓我建立使用者旅程地圖（業務流）：**",
                },
                {
                    "role": "user",
                    "content": "等一下，你在第二個跟第三個給我的連結啊，裡面都是亂買，你到底在幹什麼？你重新確認一下。",
                },
                {"role": "assistant", "content": ""},
                {"role": "user", "content": "你還好嗎？你有沒有在動作？"},
            ],
            "config": {
                "system_prompt": "回答後你都會在結尾講個笑話，並加上 emoji",
                "botrun_flow_lang_url": "https://botrun-flow-lang-fastapi-dev-36186877499.asia-east1.run.app",
                "user_id": "sebastian.hsu@gmail.com",
            },
        }

        # Make the request
        endpoint = "/api/langgraph/invoke"
        print(f"\nTesting API: {self.base_url}{endpoint}")
        print("-" * 50)

        try:
            response = self.api_post(endpoint, payload)

            # Basic assertions to verify the response
            self.assertIsNotNone(response)

            # Check for error response format
            if "detail" in response:
                error_message = response["detail"]
                # Fail if the error is about empty message content
                self.assertNotIn(
                    "messages.3: all messages must have non-empty content except for the optional final assistant message",
                    error_message,
                    f"API returned expected error about empty content: {error_message}",
                )
                print(
                    f"API returned an error, but not the empty content error: {error_message}"
                )
            # Check for successful response format
            else:
                # For successful responses, verify content key exists at the top level
                self.assertIn("content", response, "Response missing 'content' field")
                print(f"Response received successfully with content!")

        except Exception as e:
            self.fail(f"Error testing API: {str(e)}")


def run_with_base_url(base_url=None):
    """Run the tests with an optional custom base URL

    Args:
        base_url: Optional base URL to override the default
    """
    # If a base URL is provided, set it as a class attribute
    if base_url:
        TestAPIFunctionality.base_url = base_url

    # Run the tests
    unittest.main(argv=["first-arg-is-ignored"], exit=False)


if __name__ == "__main__":
    # Default execution uses the URL from setUp
    unittest.main()
