import re
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
from src.config import YOUTUBE_API_KEY, YOUTUBE_SEARCH_QUERY, MAX_YOUTUBE_RESULTS, FETCH_DAYS_BACK

# Words that indicate a video is a Short
SKIP_KEYWORDS = ["#shorts", "#short", "#reels"]

# Favorite channels — add any @handle here to always pull their latest videos
FAVORITE_CHANNELS = [
    "@johnnyharris",
    "@veritasium",
    "@cleoabram",
    "@kurzgesagt",
    "@LexFridman",
    "@TED",
]


def is_english(text: str) -> bool:
    if not text:
        return True
    ascii_count = sum(1 for c in text if ord(c) < 128)
    return (ascii_count / len(text)) > 0.8


def is_short(title: str, description: str) -> bool:
    combined = (title + " " + description).lower()
    return any(kw in combined for kw in SKIP_KEYWORDS)


def is_short_duration(duration: str) -> bool:
    """Returns True if video is under 60 seconds (a YouTube Short)."""
    if not duration:
        return False
    minutes = int(re.search(r"(\d+)M", duration).group(1)) if "M" in duration else 0
    seconds = int(re.search(r"(\d+)S", duration).group(1)) if "S" in duration else 0
    return (minutes * 60 + seconds) < 60


def get_view_count(youtube, video_id: str) -> int:
    try:
        response = youtube.videos().list(part="statistics", id=video_id).execute()
        items = response.get("items", [])
        if items:
            return int(items[0]["statistics"].get("viewCount", 0))
    except Exception:
        pass
    return 0


def resolve_channel_id(youtube, handle: str) -> str | None:
    """Resolves a YouTube @handle to a channel ID."""
    try:
        response = youtube.channels().list(
            part="id",
            forHandle=handle.lstrip("@"),
        ).execute()
        items = response.get("items", [])
        if items:
            return items[0]["id"]
    except Exception as e:
        print(f"[YouTube] Could not resolve {handle}: {e}")
    return None


def _fetch_durations(youtube, video_ids: list[str]) -> dict[str, str]:
    if not video_ids:
        return {}
    details = youtube.videos().list(
        part="contentDetails",
        id=",".join(video_ids),
    ).execute()
    return {item["id"]: item["contentDetails"]["duration"] for item in details.get("items", [])}


def fetch_favorite_channel_videos() -> list[dict]:
    """
    Fetches the latest non-Short videos from FAVORITE_CHANNELS
    published in the last FETCH_DAYS_BACK days.
    """
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    since = (datetime.now(timezone.utc) - timedelta(days=FETCH_DAYS_BACK)).isoformat()

    videos = []
    seen_ids = set()

    for handle in FAVORITE_CHANNELS:
        channel_id = resolve_channel_id(youtube, handle)
        if not channel_id:
            print(f"[YouTube] Could not find channel: {handle}")
            continue

        try:
            # Use the uploads playlist (UU + channel_id[2:]) — works with API keys,
            # unlike search?channelId which requires OAuth for some channels.
            uploads_playlist_id = "UU" + channel_id[2:]
            response = youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=uploads_playlist_id,
                maxResults=10,
            ).execute()

            items = response.get("items", [])
            ids = [item["contentDetails"]["videoId"] for item in items]
            duration_map = _fetch_durations(youtube, ids)

            channel_count = 0
            for item in items:
                snippet = item["snippet"]
                video_id = item["contentDetails"]["videoId"]

                published_str = snippet.get("publishedAt", "")
                try:
                    pub_date = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                    if pub_date < datetime.fromisoformat(since):
                        continue
                except Exception:
                    pass

                if video_id in seen_ids:
                    continue
                seen_ids.add(video_id)

                title = snippet["title"]
                desc = snippet.get("description", "")[:300]

                if not is_english(title):
                    continue
                if is_short(title, desc):
                    continue
                if is_short_duration(duration_map.get(video_id, "")):
                    continue

                videos.append({
                    "type":         "video",
                    "title":        title,
                    "url":          f"https://www.youtube.com/watch?v={video_id}",
                    "channel":      snippet.get("channelTitle", handle),
                    "description":  desc,
                    "published_at": published_str,
                    "view_count":   get_view_count(youtube, video_id),
                })
                channel_count += 1

            print(f"[YouTube] ✅ {handle}: {channel_count} new video(s)")

        except Exception as e:
            print(f"[YouTube] ⚠️  {handle}: failed ({e})")

    print(f"[YouTube] Favorite channels total: {len(videos)} videos.")
    return videos


def fetch_ai_videos() -> list[dict]:
    """
    Fetches recent YouTube videos about AI published in the last 24 hours.
    Filters out Shorts and non-English videos.
    """
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()

    response = youtube.search().list(
        q=YOUTUBE_SEARCH_QUERY,
        part="snippet",
        type="video",
        order="relevance",
        publishedAfter=since,
        relevanceLanguage="en",
        maxResults=MAX_YOUTUBE_RESULTS * 2,
    ).execute()

    items = response.get("items", [])
    ids = [item["id"]["videoId"] for item in items]
    duration_map = _fetch_durations(youtube, ids)

    videos = []
    for item in items:
        snippet = item["snippet"]
        video_id = item["id"]["videoId"]
        title = snippet["title"]
        desc = snippet.get("description", "")[:300]

        if not is_english(title):
            print(f"[YouTube] Skipping non-English: {title}")
            continue
        if is_short(title, desc):
            print(f"[YouTube] Skipping Short (keyword): {title}")
            continue
        if is_short_duration(duration_map.get(video_id, "")):
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

        if len(videos) >= MAX_YOUTUBE_RESULTS:
            break

    print(f"[YouTube] Fetched {len(videos)} AI videos after filtering.")
    return videos


# ─── Quick test ─────────────────────────────────────────────────────
if __name__ == "__main__":
    videos = fetch_ai_videos()
    for v in videos:
        print(f"\n📺 {v['title']}")
        print(f"   Channel : {v['channel']}")
        print(f"   URL     : {v['url']}")
        print(f"   Published: {v['published_at']}")
