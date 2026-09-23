import os, re
from googleapiclient.discovery import build

def extract_video_id(url: str) -> str:
    match = re.search(r"(?:v=|youtu\.be/)([\w-]{11})", url)
    if not match:
        raise ValueError("Youtube URL invalide.")
    return match.group(1)


def get_comments(video_id: str, max_results: int = 200):
    youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))
    comments = []
    request = youtube.commentThreads().list(
        part="snippet", videoId=video_id, maxResults=100, textFormat="plainText"
    )
    while request and len(comments) < max_results:
        response = request.execute()
        for item in response["items"]:
            c = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "author": c["authorDisplayName"],
                "text": c["textDisplay"],
                "likes": c["likeCount"],
                "date": c["publishedAt"],
            })
        request = youtube.commentThreads().list_next(request, response)
    return comments