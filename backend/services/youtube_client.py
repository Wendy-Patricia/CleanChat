import re
from typing import Iterator
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from backend.core.config import get_settings
from backend.core.logging import logger

# cobre watch?v=, youtu.be/, shorts/, embed/, live/
_YT_PATTERNS = [
    re.compile(r"(?:v=|youtu\.be/|shorts/|embed/|live/)([\w-]{11})"),
]

def extract_video_id(url: str) -> str:
    for pattern in _YT_PATTERNS:
        match = pattern.search(url)
        if match:
            return match.group(1)
    raise ValueError(f"Invalid YouTube URL: {url}")


def _client():
    key = get_settings().youtube_api_key
    return build("youtube", "v3", developerKey=key, cache_discovery=False)


def get_comments(video_id: str, max_results: int | None = None) -> list[dict]:
    """Downloads comments by paging until max_results. Returns a normalized list."""
    settings = get_settings()
    max_results = max_results or settings.max_comments
    youtube = _client()
    comments: list[dict] = []

    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            textFormat="plainText",
        )
        while request and len(comments) < max_results:
            response = request.execute()
            for item in response.get("items", []):
                c = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "author": c.get("authorDisplayName", ""),
                    "text": c.get("textDisplay", ""),
                    "likes": int(c.get("likeCount", 0)),
                    "date": c.get("publishedAt"),
                })
            request = youtube.commentThreads().list_next(request, response)
    except HttpError as e:
        # comments disabled / private video / quota exhausted
        logger.warning(f"YouTube API error for video {video_id}: {e}")

    logger.info(f"Downloaded {len(comments)} comments from {video_id}")
    return comments[:max_results]