import feedparser
import re
from datetime import datetime, timedelta, timezone
from src.config import FETCH_DAYS_BACK

# ─── Official AI lab RSS feeds ───────────────────────────────────────
AI_LAB_FEEDS = [
    {"name": "Anthropic",       "url": "https://www.anthropic.com/news/rss"},
    {"name": "Anthropic Alt",   "url": "https://www.anthropic.com/feed.xml"},
    {"name": "OpenAI",          "url": "https://openai.com/news/rss.xml"},
    {"name": "Google DeepMind", "url": "https://deepmind.google/blog/rss.xml"},
    {"name": "Google DeepMind Alt", "url": "https://blog.google/technology/ai/rss/"},
    {"name": "Meta AI",         "url": "https://ai.meta.com/blog/feed/"},
    {"name": "Meta AI Alt",
        "url": "https://engineering.fb.com/category/ai-research/feed/"},
    {"name": "Mistral AI",      "url": "https://mistral.ai/news/rss"},
    {"name": "Hugging Face",    "url": "https://huggingface.co/blog/feed.xml"},
]

# Skip tutorial/academy/help pages
SKIP_URL_PATTERNS = [
    "/academy/", "/help/", "/policies/", "/careers/",
    "/about/", "/pricing/", "/contact/",
]

# Track seen URLs to avoid duplicates from alt feeds
seen_urls = set()


def fetch_lab_blogs() -> list[dict]:
    """
    Fetches recent blog posts from major AI labs via RSS feeds.
    Returns a list of article dictionaries.
    """

    since = datetime.now(timezone.utc) - timedelta(days=FETCH_DAYS_BACK)
    posts = []

    for feed_info in AI_LAB_FEEDS:
        try:
            feed = feedparser.parse(feed_info["url"])
            count = 0

            for entry in feed.entries:
                link = entry.get("link", "")

                # Skip duplicates
                if link in seen_urls:
                    continue

                # Skip tutorial/help pages
                if any(pattern in link for pattern in SKIP_URL_PATTERNS):
                    continue

                # Parse the published date
                try:
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published = datetime(
                            *entry.published_parsed[:6], tzinfo=timezone.utc)
                    else:
                        published = datetime.now(timezone.utc)
                except Exception:
                    published = datetime.now(timezone.utc)

                # Only include posts from the last FETCH_DAYS_BACK days
                if published < since:
                    continue

                # Strip HTML from description
                description = ""
                if hasattr(entry, "summary"):
                    description = re.sub(r"<[^>]+>", "", entry.summary)[:300]

                # Use lab name without "Alt" suffix
                source_name = feed_info["name"].replace(" Alt", "")

                posts.append({
                    "type":         "article",
                    "title":        entry.get("title", "No title"),
                    "url":          link,
                    "source":       source_name,
                    "description":  description,
                    "published_at": published.isoformat(),
                })

                seen_urls.add(link)
                count += 1

            print(
                f"[Blogs] ✅ {feed_info['name']}: {count} posts in last {FETCH_DAYS_BACK} days")

        except Exception as e:
            print(f"[Blogs] ⚠️  {feed_info['name']}: failed ({e})")
            continue

    print(f"[Blogs] Total blog posts fetched: {len(posts)}")
    return posts


# ─── Quick test ─────────────────────────────────────────────────────
if __name__ == "__main__":
    posts = fetch_lab_blogs()
    for p in posts:
        print(f"\n🏢 {p['title']}")
        print(f"   Source   : {p['source']}")
        print(f"   URL      : {p['url']}")
        print(f"   Published: {p['published_at']}")
