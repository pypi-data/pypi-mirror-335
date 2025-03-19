from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import re

load_dotenv()


def get_video_id(url: str) -> str:
    """
    Extract video ID from various YouTube URL formats.
    Supports:
    - Standard watch URLs (youtube.com/watch?v=...)
    - Shortened URLs (youtu.be/...)
    - Embed URLs (youtube.com/embed/...)
    """
    # Try parsing as standard URL first
    parsed_url = urlparse(url)

    # Handle youtu.be URLs
    if parsed_url.netloc == "youtu.be":
        return parsed_url.path.lstrip("/")

    # Handle standard youtube.com URLs
    if parsed_url.netloc in ["www.youtube.com", "youtube.com"]:
        if parsed_url.path == "/watch":
            # Standard watch URL
            return parse_qs(parsed_url.query).get("v", [""])[0]
        elif "/embed/" in parsed_url.path:
            # Embed URL
            return parsed_url.path.split("/embed/")[-1]

    # Try extracting video ID using regex as fallback
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if video_id_match:
        return video_id_match.group(1)

    raise ValueError(f"Could not extract video ID from URL: {url}")


def get_youtube_transcript(url: str) -> str:
    """
    Get transcript from YouTube video with improved error handling.
    Will try multiple methods to get the transcript.
    """
    try:
        video_id = get_video_id(url)
        print("[get_youtube_transcript]video_id============>", video_id)
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        print("[get_youtube_transcript]transcript_list============>", transcript_list)

        # If both failed, try to get any available transcript
        for transcript in transcript_list:
            print("[get_youtube_transcript]transcript============>", transcript)
            try:
                result = "\n".join(line["text"] for line in transcript.fetch())
                return result
            except Exception as e:
                continue

        raise Exception("No transcripts could be retrieved")

    except Exception as e:
        error_message = str(e)
        if "Subtitles are disabled for this video" in error_message:
            return "Error: Subtitles are disabled for this video"
        elif "Video is no longer available" in error_message:
            return "Error: Video is no longer available"
        elif "Could not extract video ID" in error_message:
            return "Error: Invalid YouTube URL format"
        else:
            return f"Error getting YouTube transcript: {error_message}"
