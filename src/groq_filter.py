from groq import Groq
from src.config import GROQ_API_KEY, MIN_RELEVANCE_SCORE

# Connect to Groq
client = Groq(api_key=GROQ_API_KEY)


def score_item(item: dict) -> int:
    """
    Asks Groq to score a single video or article 1-10 based on:
    - How relevant it is to AI/ML/tech
    - How interesting and substantial it is
    - Whether it comes from a credible source
    - How many views it has (for videos)
    Returns an integer score 1-10.
    """

    if item["type"] == "video":
        views = item.get("view_count", 0)
        content = f"""
Title: {item['title']}
Channel: {item['channel']}
Description: {item['description']}
Views: {views:,}
Type: YouTube Video
"""
    else:
        content = f"""
Title: {item['title']}
Source: {item['source']}
Description: {item['description']}
Type: News Article
"""

    prompt = f"""You are a strict AI/ML content curator for a professional with a Masters in AI.

Score the following piece of content from 1 to 10 based on:
- Relevance to AI, machine learning, or cutting-edge technology (most important)
- Quality and credibility of the source or channel
- How interesting and substantial it is for an AI professional
- Consider view count as a signal of quality (more views = more credible, but not the only factor)
- Penalize heavily: clickbait, entertainment, non-English content, unrelated topics

Content to score:
{content}

Respond ONLY with a single integer between 1 and 10. Nothing else."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=5,
        temperature=0,
    )

    try:
        score = int(response.choices[0].message.content.strip())
        score = max(1, min(10, score))
    except ValueError:
        score = 0

    return score


def filter_items(items: list[dict]) -> list[dict]:
    """
    Takes a list of videos and articles, scores each one with Groq,
    and returns only the ones that score >= MIN_RELEVANCE_SCORE.
    """
    print(f"\n[Groq] Scoring {len(items)} items...")
    filtered = []

    for item in items:
        score = score_item(item)
        item["score"] = score
        status = "✅ KEEP" if score >= MIN_RELEVANCE_SCORE else "❌ SKIP"
        print(f"[Groq] Score {score}/10 {status} — {item['title'][:60]}")

        if score >= MIN_RELEVANCE_SCORE:
            filtered.append(item)

    filtered.sort(key=lambda x: x["score"], reverse=True)
    print(f"[Groq] Kept {len(filtered)} out of {len(items)} items.")
    return filtered


# ─── Quick test ─────────────────────────────────────────────────────
if __name__ == "__main__":
    test_items = [
        {
            "type": "video",
            "title": "Artificial Intelligence vs Machine Learning vs Deep Learning",
            "channel": "Geeky Arvi",
            "description": "A detailed explanation of the differences between AI, ML and deep learning",
            "url": "https://youtube.com/watch?v=test1",
            "published_at": "2026-04-11T12:00:00Z",
            "view_count": 150000,
        },
        {
            "type": "video",
            "title": "Hasan vs Yapay zeka",
            "channel": "BaBa Yorumlar",
            "description": "Funny video about chatting with AI",
            "url": "https://youtube.com/watch?v=test2",
            "published_at": "2026-04-11T12:00:00Z",
            "view_count": 1200,
        },
        {
            "type": "article",
            "title": "Databricks co-founder declares AGI is already here",
            "source": "The Next Web",
            "description": "Matei Zaharia wins ACM Prize and makes bold claims about AGI",
            "url": "https://thenextweb.com/test",
            "published_at": "2026-04-10T06:00:00Z",
        },
    ]

    results = filter_items(test_items)
    print(f"\n--- Final kept items ---")
    for item in results:
        print(f"⭐ {item['score']}/10 — {item['title']}")
