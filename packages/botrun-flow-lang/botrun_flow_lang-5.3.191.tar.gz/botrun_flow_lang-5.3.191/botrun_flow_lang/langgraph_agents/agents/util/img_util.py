import anthropic
import base64
import httpx
import mimetypes
import os
import imghdr
from pathlib import Path
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv

load_dotenv()


def get_img_content_type(file_path: str | Path) -> str:
    """
    Get the content type (MIME type) of a local file.
    This function checks the actual image format rather than relying on file extension.

    Args:
        file_path: Path to the local file (can be string or Path object)

    Returns:
        str: The content type of the file (e.g., 'image/jpeg', 'image/png')

    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file type is not recognized or not supported
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check actual image type using imghdr
    img_type = imghdr.what(file_path)
    if not img_type:
        raise ValueError(f"File is not a recognized image format: {file_path}")

    # Map image type to MIME type
    mime_types = {
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
    }

    content_type = mime_types.get(img_type.lower())
    if not content_type:
        raise ValueError(f"Unsupported image format '{img_type}': {file_path}")

    return content_type


def analyze_imgs_with_claude(
    img_urls: list[str], user_input: str, model_name: str = "claude-3-7-sonnet-latest"
) -> str:
    """
    Analyze multiple images using Claude Vision API

    Args:
        img_urls: List of URLs to the image files
        user_input: User's query about the image content(s)

    Returns:
        str: Claude's analysis of the image content(s) based on the query
    """
    try:
        # Initialize message content
        message_content = []

        # Download and encode each image file from URLs
        with httpx.Client(follow_redirects=True) as client:
            for img_url in img_urls:
                response = client.get(img_url)
                if response.status_code != 200:
                    return f"Error: Failed to download image from URL: {img_url}"

                # Detect content type from response headers
                content_type = response.headers.get("content-type", "")
                if not content_type.startswith("image/"):
                    return f"Error: URL does not point to a valid image: {img_url}"

                # Check file size (5MB limit for API)
                if len(response.content) > 5 * 1024 * 1024:
                    return f"Error: Image file size exceeds 5MB limit: {img_url}"

                # Encode image data
                img_data = base64.standard_b64encode(response.content).decode("utf-8")

                # Add image to message content
                message_content.append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": content_type,
                            "data": img_data,
                        },
                    }
                )

            # Add user input text
            message_content.append({"type": "text", "text": user_input})

            # Initialize Anthropic client
            client = anthropic.Anthropic()

            # Send to Claude
            message = client.messages.create(
                model=model_name,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": message_content,
                    }
                ],
            )

            print(
                f"analyze_imgs_with_claude============> input_token: {message.usage.input_tokens} output_token: {message.usage.output_tokens}",
            )
            return message.content[0].text

    except httpx.RequestError as e:
        return f"Error: Failed to download image(s): {str(e)}"
    except anthropic.APIError as e:
        return f"Error accessing Claude API: {str(e)}"
    except Exception as e:
        return f"Error analyzing image(s): {str(e)}"


def analyze_imgs_with_gemini(
    img_urls: list[str], user_input: str, model_name: str = "gemini-2.0-flash"
) -> str:
    """
    Analyze multiple images using Gemini-2.0-flash Vision API

    Args:
        img_urls: List of URLs to the image files
        user_input: User's query about the image content(s)

    Returns:
        str: Gemini's analysis of the image content(s) based on the query
    """
    try:
        # Initialize the Gemini client
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return "Error: GEMINI_API_KEY environment variable not set"

        # 設定 API 金鑰
        genai.configure(api_key=api_key)

        # 初始化模型
        model = genai.GenerativeModel(model_name)

        # 準備內容列表
        contents = []
        contents.append(user_input)

        # 下載並處理每個圖片
        with httpx.Client(follow_redirects=True) as client:
            for img_url in img_urls:
                response = client.get(img_url)
                if response.status_code != 200:
                    return f"Error: Failed to download image from URL: {img_url}"

                # 檢測內容類型
                content_type = response.headers.get("content-type", "")
                if not content_type.startswith("image/"):
                    return f"Error: URL does not point to a valid image: {img_url}"

                # 檢查檔案大小
                if len(response.content) > 20 * 1024 * 1024:  # 20MB 限制
                    return f"Error: Image file size too large: {img_url}"

                # 將圖片添加到內容中
                contents.append(
                    {
                        "inline_data": {
                            "mime_type": content_type,
                            "data": base64.b64encode(response.content).decode("utf-8"),
                        }
                    }
                )

        # 生成內容
        generation_config = {
            "temperature": 0.4,
            "top_p": 1,
            "top_k": 32,
            "max_output_tokens": 2048,
        }

        # 使用正確的 HarmCategory 名稱
        safety_settings = [
            {
                "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
        ]

        response = model.generate_content(
            contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
        )
        print(
            f"analyze_imgs_with_gemini============> input_token: {response.usage_metadata.prompt_token_count} output_token: {response.usage_metadata.candidates_token_count}"
        )
        return response.text

    except httpx.RequestError as e:
        return f"Error: Failed to download image(s): {str(e)}"
    except Exception as e:
        import traceback

        traceback.print_exc()
        return f"Error analyzing image(s) with Gemini: {str(e)}"


def analyze_imgs(img_urls: list[str], user_input: str) -> str:
    """
    Analyze multiple images using Gemini-2.0-flash Vision API
    Falls back to Claude if Gemini fails

    Args:
        img_urls: List of URLs to the image files
        user_input: User's query about the image content(s)

    Returns:
        str: AI analysis of the image content(s) based on the query
    """
    try:
        if os.getenv("IMG_ANALYZER_MODEL", "gemini-2.0-flash").startswith("gemini-"):
            return analyze_imgs_with_gemini(
                img_urls,
                user_input,
                os.getenv("IMG_ANALYZER_MODEL", "gemini-2.0-flash"),
            )
        elif os.getenv("IMG_ANALYZER_MODEL").startswith("claude-"):
            return analyze_imgs_with_claude(
                img_urls, user_input, os.getenv("IMG_ANALYZER_MODEL")
            )

        # Try with Gemini first
        # return analyze_imgs_with_claude(img_urls, user_input)
    except Exception as e:
        # Fall back to Claude if Gemini fails
        print(f"Gemini image analysis failed: {str(e)}")
        # return analyze_imgs_with_gemini(img_urls, user_input)
        return "Error analyzing image(s) exception " + str(e)
