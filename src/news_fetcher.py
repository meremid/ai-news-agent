from newsapi import NewsApiClient
from datetime import datetime, timedelta, timezone
from src.config import NEWS_API_KEY, NEWS_SEARCH_QUERY, MAX_NEWS_RESULTS, FETCH_DAYS_BACK

since = (datetime.now(timezone.utc) -
         timedelta(days=FETCH_DAYS_BACK)).strftime("%Y-%m-%d")

# ─── Trusted AI/Tech sources only ───────────────────────────────────
TRUSTED_SOURCES = [
    "techcrunch",
    "the-verge",
    "wired",
    "ars-technica",
    "mit-technology-review",
    "reuters",
    "bloomberg",
    "the-next-web",
    "engadget",
    "venturebeat",
]


def fetch_ai_news() -> list[dict]:
    """
    Fetches recent English AI news from trusted sources in the last 24 hours.
    Returns a list of article dictionaries with title, url, source, and description.
    """

    # Connect to NewsAPI
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)

    # Only fetch articles from the last 24 hours
    since = (datetime.now(timezone.utc) -
             timedelta(hours=24)).strftime("%Y-%m-%d")

    response = newsapi.get_everything(
        q=NEWS_SEARCH_QUERY,
        sources=",".join(TRUSTED_SOURCES),  # only trusted sources
        language="en",                       # English only
        sort_by="relevancy",                 # most relevant first
        from_param=since,
        page_size=MAX_NEWS_RESULTS,
    )

    articles = []
    for article in response.get("articles", []):

        # Skip articles with no title or description
        if not article.get("title") or not article.get("description"):
            continue

        # Skip removed articles
        if article["title"] == "[Removed]":
            continue

        articles.append({
            "type":         "article",
            "title":        article["title"],
            "url":          article["url"],
            "source":       article["source"]["name"],
            "description":  article.get("description", "")[:300],
            "published_at": article.get("publishedAt", ""),
        })

    print(f"[News] Fetched {len(articles)} articles.")
    return articles


# ─── Quick test ─────────────────────────────────────────────────────
if __name__ == "__main__":
    articles = fetch_ai_news()
    for a in articles:
        print(f"\n📰 {a['title']}")
        print(f"   Source   : {a['source']}")
        print(f"   URL      : {a['url']}")
        print(f"   Published: {a['published_at']}")
