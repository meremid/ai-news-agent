import os
from dotenv import load_dotenv

load_dotenv()

# ─── API Keys ───────────────────────────────────────────────────────
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ─── Gmail ──────────────────────────────────────────────────────────
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# ─── Agent behaviour ────────────────────────────────────────────────
YOUTUBE_SEARCH_QUERY = "artificial intelligence"   # what to search on YouTube
NEWS_SEARCH_QUERY = "artificial intelligence"   # what to search on NewsAPI
MAX_YOUTUBE_RESULTS = 10   # how many videos to fetch before filtering
MAX_NEWS_RESULTS = 20   # how many articles to fetch before filtering
MIN_RELEVANCE_SCORE = 7    # Claude scores items 1-10; only send >= this
FETCH_DAYS_BACK = 3

# ─── Validation ─────────────────────────────────────────────────────
REQUIRED_VARS = [
    "YOUTUBE_API_KEY",
    "NEWS_API_KEY",
    "GROQ_API_KEY",
    "GMAIL_ADDRESS",
    "GMAIL_APP_PASSWORD",
    "RECIPIENT_EMAIL",
]


def validate_config():
    missing = [v for v in REQUIRED_VARS if not os.getenv(v)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Copy .env.example to .env and fill in your keys."
        )
