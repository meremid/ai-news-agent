"""
AI News Agent — Main Entry Point
Fetches YouTube videos, news articles, AI lab blogs and ArXiv papers,
filters them with Groq, and sends a digest email every 3 days.
"""

from src.config import validate_config
from src.youtube_fetcher import fetch_ai_videos
from src.news_fetcher import fetch_ai_news
from src.blog_fetcher import fetch_lab_blogs
from src.arxiv_fetcher import fetch_arxiv_papers
from src.groq_filter import filter_items
from src.email_sender import send_digest


def run():
    print("=" * 50)
    print("🤖 AI News Agent Starting...")
    print("=" * 50)

    # ─── Step 1: Validate all API keys ──────────────────────────
    print("\n[Agent] Validating configuration...")
    validate_config()
    print("[Agent] ✅ Configuration valid.")

    # ─── Step 2: Fetch all content ──────────────────────────────
    print("\n[Agent] Fetching YouTube videos...")
    videos = fetch_ai_videos()

    print("\n[Agent] Fetching news articles...")
    articles = fetch_ai_news()

    print("\n[Agent] Fetching AI lab blog posts...")
    blogs = fetch_lab_blogs()

    print("\n[Agent] Fetching ArXiv research papers...")
    papers = fetch_arxiv_papers()

    all_items = videos + articles + blogs + papers
    print(f"\n[Agent] Total items fetched: {len(all_items)}")
    print(f"         Videos  : {len(videos)}")
    print(f"         News    : {len(articles)}")
    print(f"         Blogs   : {len(blogs)}")
    print(f"         Papers  : {len(papers)}")

    if not all_items:
        print("[Agent] No items fetched. Exiting.")
        return

    # ─── Step 3: Filter with Groq ───────────────────────────────
    print("\n[Agent] Filtering with Groq...")
    filtered_items = filter_items(all_items)

    if not filtered_items:
        print("[Agent] No items passed the filter. Exiting.")
        return

    # ─── Step 4: Split by type ──────────────────────────────────
    filtered_videos = [i for i in filtered_items if i["type"] == "video"]
    filtered_articles = [i for i in filtered_items if i["type"] == "article"
                         and i.get("source", "") not in ["ArXiv"]
                         and "ArXiv" not in i.get("source", "")]
    filtered_blogs = [i for i in filtered_items if i.get("source") in [
        "Anthropic", "OpenAI", "Google DeepMind",
        "Google AI Blog", "Meta AI", "Hugging Face", "Mistral AI"]]
    filtered_papers = [
        i for i in filtered_items if "ArXiv" in i.get("source", "")]

    print(f"\n[Agent] After filtering:")
    print(f"         Videos  : {len(filtered_videos)}")
    print(f"         News    : {len(filtered_articles)}")
    print(f"         Blogs   : {len(filtered_blogs)}")
    print(f"         Papers  : {len(filtered_papers)}")

    # ─── Step 5: Send digest email ──────────────────────────────
    print("\n[Agent] Sending digest email...")
    send_digest(filtered_videos, filtered_articles,
                filtered_blogs, filtered_papers)

    print("\n" + "=" * 50)
    print("✅ AI News Agent finished successfully!")
    print("=" * 50)


if __name__ == "__main__":
    run()
