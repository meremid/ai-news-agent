from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
from src.config import YOUTUBE_API_KEY, YOUTUBE_SEARCH_QUERY, MAX_YOUTUBE_RESULTS, FETCH_DAYS_BACK

since = (datetime.now(timezone.utc) -
         timedelta(days=FETCH_DAYS_BACK)).isoformat()

# Words that indicate a video is a Short or not in English
SKIP_KEYWORDS = ["#shorts", "#short", "#reels"]


def is_english(text: str) -> bool:
    """Basic check — if most characters are ASCII it's likely English."""
    if not text:
        return True
    ascii_count = sum(1 for c in text if ord(c) < 128)
    return (ascii_count / len(text)) > 0.8


def is_short(title: str, description: str) -> bool:
    """Returns True if the video looks like a YouTube Short."""
    combined = (title + " " + description).lower()
    return any(kw in combined for kw in SKIP_KEYWORDS)


def fetch_ai_videos() -> list[dict]:
    """
    Fetches recent YouTube videos about AI published in the last 24 hours.
    Filters out Shorts and non-English videos.
    Returns a list of video dictionaries with title, url, channel, and description.
    """

    # Connect to the YouTube API
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    # Only fetch videos published in the last 24 hours
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()

    # Fetch more than we need so we have enough after filtering
    response = youtube.search().list(
        q=YOUTUBE_SEARCH_QUERY,
        part="snippet",
        type="video",
        order="relevance",
        publishedAfter=since,
        relevanceLanguage="en",       # ← prefer English results
        maxResults=MAX_YOUTUBE_RESULTS * 2,  # fetch extra to account for filtering
    ).execute()

    # Also fetch video durations to filter out Shorts (< 60 seconds)
    video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
    duration_map = {}
    if video_ids:
        details = youtube.videos().list(
            part="contentDetails",
            id=",".join(video_ids)
        ).execute()
        for item in details.get("items", []):
            duration = item["contentDetails"]["duration"]
            # PT1M30S = 1 min 30 sec, PT45S = 45 sec (a Short)
            duration_map[item["id"]] = duration

    def is_short_duration(duration: str) -> bool:
        """Returns True if video is under 60 seconds (a Short)."""
        import re
        if not duration:
            return False
        # Extract minutes and seconds from ISO 8601 duration
        minutes = int(re.search(r"(\d+)M", duration).group(1)
                      ) if "M" in duration else 0
        seconds = int(re.search(r"(\d+)S", duration).group(1)
                      ) if "S" in duration else 0
        total_seconds = minutes * 60 + seconds
        return total_seconds < 60

    videos = []
    for item in response.get("items", []):
        snippet = item["snippet"]
        video_id = item["id"]["videoId"]
        title = snippet["title"]
        desc = snippet.get("description", "")[:300]

        # Skip non-English videos
        if not is_english(title):
            print(f"[YouTube] Skipping non-English: {title}")
            continue

        # Skip Shorts by keyword
        if is_short(title, desc):
            print(f"[YouTube] Skipping Short (keyword): {title}")
            continue

        # Skip Shorts by duration
        duration = duration_map.get(video_id, "")
        if is_short_duration(duration):
            print(f"[YouTube] Skipping Short (duration): {title}")
            continue

        videos.append({
            "type":         "video",
            "title":        title,
            "url":          f"https://www.youtube.com/watch?v={video_id}",
            "channel":      snippet["channelTitle"],
            "description":  desc,
            "published_at": snippet["publishedAt"],
            "view_count":   get_view_count(youtube, video_id),
        })

        # Stop once we have enough
        if len(videos) >= MAX_YOUTUBE_RESULTS:
            break

    print(f"[YouTube] Fetched {len(videos)} videos after filtering.")
    return videos


def get_view_count(youtube, video_id: str) -> int:
    """Fetches the view count for a single video."""
    try:
        response = youtube.videos().list(
            part="statistics",
            id=video_id
        ).execute()
        items = response.get("items", [])
        if items:
            return int(items[0]["statistics"].get("viewCount", 0))
    except Exception:
        pass
    return 0


# ─── Quick test ─────────────────────────────────────────────────────
if __name__ == "__main__":
    videos = fetch_ai_videos()
    for v in videos:
        print(f"\n📺 {v['title']}")
        print(f"   Channel : {v['channel']}")
        print(f"   URL     : {v['url']}")
        print(f"   Published: {v['published_at']}")
