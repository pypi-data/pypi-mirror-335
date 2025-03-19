import os
from tempfile import NamedTemporaryFile
from typing import Dict, Any, Optional
from .local_files import upload_and_get_tmp_public_url, upload_html_and_get_public_url


def generate_html_file(
    html_content: str,
    botrun_flow_lang_url: str,
    user_id: str,
    title: Optional[str] = None,
) -> str:
    """
    Generate HTML file from complete HTML content (including JS and CSS) and upload it to GCS.

    This function accepts complete HTML documents with JavaScript, CSS, and other elements.
    You can pass either:
    1. A complete HTML document (<!DOCTYPE html><html>...<head>...</head><body>...</body></html>)
    2. HTML fragment that will be wrapped in a basic HTML structure if needed

    The function preserves all JavaScript, CSS, and other elements in the HTML content.

    Args:
        html_content: Complete HTML content string, including head/body tags, JavaScript, CSS, etc.
        botrun_flow_lang_url: URL for the botrun flow lang API
        user_id: User ID for file upload
        title: Optional title for the HTML page (used only if the HTML doesn't already have a title)

    Returns:
        str: URL for the HTML file or error message starting with "Error: "
    """
    try:
        # Check if the content is already a complete HTML document
        is_complete_html = html_content.strip().lower().startswith(
            "<!doctype html"
        ) or html_content.strip().lower().startswith("<html")

        # Only process HTML content if it's not already a complete document
        if not is_complete_html:
            # If not a complete HTML document, check if it has a head tag
            if "<head>" in html_content.lower():
                # Has head tag but not complete doc, add title if needed and provided
                if title and "<title>" not in html_content.lower():
                    html_content = html_content.replace(
                        "<head>", f"<head>\n    <title>{title}</title>", 1
                    )
            else:
                # No head tag, wrap the content in a basic HTML structure
                html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>{title if title else 'HTML Page'}</title>
    <style>
        body {{
            font-family: "Microsoft JhengHei", "微軟正黑體", "Heiti TC", "黑體-繁", sans-serif;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
        # If we have complete HTML but title is provided and no title exists
        elif title and "<title>" not in html_content.lower():
            # Try to insert title into the head tag
            if "<head>" in html_content.lower():
                html_content = html_content.replace(
                    "<head>", f"<head>\n    <title>{title}</title>", 1
                )

        # Create temporary file
        with NamedTemporaryFile(
            suffix=".html", mode="w", encoding="utf-8", delete=False
        ) as html_temp:
            try:
                # Save HTML content
                html_temp.write(html_content)
                html_temp.flush()

                # Upload file to GCS
                html_url = upload_html_and_get_public_url(
                    html_temp.name, botrun_flow_lang_url, user_id
                )

                # Clean up temporary file
                os.unlink(html_temp.name)

                return html_url
            except Exception as e:
                # Clean up temporary file in case of error
                os.unlink(html_temp.name)
                return f"Error: {str(e)}"

    except Exception as e:
        return f"Error: {str(e)}"
