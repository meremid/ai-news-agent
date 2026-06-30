# 🤖 AI News Agent

A fully automated AI-powered news digest agent that curates the latest in artificial intelligence and sends it directly to your inbox every 3 days.

Built with Python and powered by Claude AI (Anthropic), this agent fetches content from multiple sources, filters it for relevance using Groq's LLM, and delivers a beautifully formatted email digest — completely automatically via GitHub Actions.

---

## ✨ What It Does

Every 3 days, the agent automatically:

1. 📺 **Fetches AI YouTube videos** — searches for the latest AI videos, filters out Shorts and non-English content
2. ⭐ **Fetches your favorite channels** — pulls the latest non-Short videos from a curated list of channels (Johnny Harris, Veritasium, Cleo Abram, Kurzgesagt, Lex Fridman, TED, and more)
3. 📰 **Fetches news articles** — pulls from trusted publications like TechCrunch, The Verge, Wired, MIT Technology Review, and more
4. 🏢 **Fetches AI lab blog posts** — monitors official blogs from Anthropic, OpenAI, Google DeepMind, Meta AI, Hugging Face, and Mistral
5. 📄 **Fetches ArXiv research papers** — pulls the latest papers from cs.AI, cs.LG (Machine Learning), and cs.CL (NLP)
6. 🧠 **Filters with Groq AI** — scores every item 1–10 for relevance and quality; news/videos require ≥ 7, papers require ≥ 5 (top 5 shown)
7. 📧 **Sends a digest email** — delivers a clean, formatted HTML email with all curated content

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| **Python 3.11** | Core language |
| **Claude AI (Anthropic)** | Assisted in building and designing this agent |
| **Groq (llama-3.3-70b-versatile)** | AI relevance scoring and filtering |
| **YouTube Data API v3** | Fetch latest AI videos and favorite channel videos |
| **NewsAPI** | Fetch news from trusted publications |
| **feedparser** | Parse RSS feeds from AI lab blogs |
| **ArXiv API** | Fetch latest research papers |
| **Gmail SMTP** | Send the digest email |
| **GitHub Actions** | Run the agent automatically every 3 days for free |

---

## 📁 Project Structure

```
ai-news-agent/
├── main.py                  ← Entry point, orchestrates everything
├── requirements.txt         ← Python dependencies
├── .env.example             ← Template for environment variables
├── .github/
│   └── workflows/
│       ├── digest.yml       ← GitHub Actions scheduler (every 3 days)
│       └── keepalive.yml    ← Prevents GitHub from disabling the schedule
└── src/
    ├── config.py            ← Centralised settings and validation
    ├── youtube_fetcher.py   ← Fetches AI videos + favorite channel videos
    ├── news_fetcher.py      ← Fetches news from trusted sources
    ├── blog_fetcher.py      ← Fetches official AI lab blog posts
    ├── arxiv_fetcher.py     ← Fetches ArXiv research papers
    ├── groq_filter.py       ← Scores and filters content with Groq
    └── email_sender.py      ← Builds and sends the HTML digest email
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOURUSERNAME/ai-news-agent.git
cd ai-news-agent
```

### 2. Set up Python environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set up your API keys

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

| Key | Where to get it | Cost |
|---|---|---|
| `YOUTUBE_API_KEY` | [console.cloud.google.com](https://console.cloud.google.com) → Enable YouTube Data API v3 | Free |
| `NEWS_API_KEY` | [newsapi.org](https://newsapi.org) | Free tier |
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | Free |
| `GMAIL_ADDRESS` | Your Gmail address | Free |
| `GMAIL_APP_PASSWORD` | [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) | Free |
| `RECIPIENT_EMAIL` | Where to receive the digest (comma-separated for multiple) | Free |

### 4. Run the agent locally

```bash
python main.py
```

---

## ⚙️ GitHub Actions Setup (Automated Runs)

To run the agent automatically every 3 days for free:

1. Push this repo to GitHub
2. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
3. Add each key from your `.env` file as a secret:
   - `YOUTUBE_API_KEY`
   - `NEWS_API_KEY`
   - `GROQ_API_KEY`
   - `GMAIL_ADDRESS`
   - `GMAIL_APP_PASSWORD`
   - `RECIPIENT_EMAIL`
4. GitHub Actions will automatically run the agent every 3 days

You can also trigger it manually at any time from the **Actions** tab → **Run workflow**.

> **Note:** GitHub automatically disables scheduled workflows after 60 days of repo inactivity. A separate `keepalive.yml` workflow runs on the 1st of every month and makes an empty commit to prevent this.

---

## 🧠 How the AI Filtering Works

Every fetched item is sent to Groq's `llama-3.3-70b-versatile` model and scored 1–10 based on:

- ✅ Relevance to AI, ML, or cutting-edge technology
- ✅ Quality and credibility of the source or channel
- ✅ How interesting and substantial it is for an AI professional
- ✅ View count as a quality signal (for videos)
- ❌ Penalises clickbait, entertainment, non-English content

| Content type | Minimum score | Max shown |
|---|---|---|
| Videos, News, Blog posts | 7 / 10 | unlimited |
| Research papers | 5 / 10 | top 5 |

Favorite channel videos bypass Groq entirely — they're always included if published in the last 3 days and are not Shorts.

---

## ⭐ Adding Favorite Channels

To add or remove channels from the "Your Favorites" section, edit `FAVORITE_CHANNELS` in `src/youtube_fetcher.py`:

```python
FAVORITE_CHANNELS = [
    "@johnnyharris",
    "@veritasium",
    "@cleoabram",
    "@kurzgesagt",
    "@LexFridman",
    "@TED",
    # add any @handle here
]
```

The agent pulls their latest videos from the past 3 days, skipping Shorts automatically.

---

## 📧 Sample Email

The digest email is divided into 5 sections:

```
🤖 Your AI Digest — April 11, 2026

📺 Top AI Videos
   GPT-6 Explained — Two Minute Papers (450,000 views · ⭐ 9/10)

📰 Top AI News
   OpenAI releases new reasoning model — TechCrunch (⭐ 8/10)

🏢 AI Lab Blog Posts
   Claude 4.6 is now available — Anthropic (⭐ 9/10)

📄 Research Papers
   Attention Is All You Need — Revisited — ArXiv (⭐ 7/10)

⭐ Your Favorites
   Why Every Map is Wrong — Veritasium (1,200,000 views)
```

---

## 🤖 Built With Claude AI

This project was entirely built through a conversation with **Claude** (Anthropic's AI assistant) at [claude.ai](https://claude.ai).

Claude helped with:
- Designing the overall agent architecture
- Writing all Python modules from scratch
- Debugging API issues in real time
- Suggesting improvements like ArXiv integration and Groq filtering
- Writing this README

This project is a demonstration of how Claude can help developers — even those new to a topic — build real, production-quality tools through natural conversation.

---

## 📄 License

MIT License — feel free to fork, modify, and use this project.

---

## 🙌 Acknowledgements

- [Anthropic](https://anthropic.com) — for Claude AI
- [Groq](https://groq.com) — for free, fast LLM inference
- [NewsAPI](https://newsapi.org) — for news aggregation
- [ArXiv](https://arxiv.org) — for open access research
- [GitHub Actions](https://github.com/features/actions) — for free automation
