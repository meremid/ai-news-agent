import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from src.config import FETCH_DAYS_BACK, MAX_NEWS_RESULTS

# ─── ArXiv categories to watch ───────────────────────────────────────
# cs.AI = Artificial Intelligence
# cs.LG = Machine Learning
# cs.CL = Computation & Language (NLP)
ARXIV_QUERY = "cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CL"
ARXIV_API_URL = "http://export.arxiv.org/api/query"


def fetch_arxiv_papers() -> list[dict]:
    """
    Fetches recent AI/ML research papers from ArXiv.
    Returns a list of paper dictionaries.
    """

    # Fetch extra to account for weekends/slow days
    params = urllib.parse.urlencode({
        "search_query": ARXIV_QUERY,
        "sortBy":       "submittedDate",
        "sortOrder":    "descending",
        "max_results":  MAX_NEWS_RESULTS * 5,
    })

    url = f"{ARXIV_API_URL}?{params}"
    print(f"[ArXiv] Fetching from: {url[:80]}...")

    try:
        with urllib.request.urlopen(url, timeout=45) as response:
            xml_data = response.read()
    except Exception as e:
        print(f"[ArXiv] ⚠️  Failed to fetch papers: {e}")
        return []

    root = ET.fromstring(xml_data)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}

    # Check total results available
    total = root.find("{http://a9.com/-/spec/opensearch/1.1/}totalResults")
    if total is not None:
        print(f"[ArXiv] Total results available: {total.text}")

    since = datetime.now(timezone.utc) - timedelta(days=FETCH_DAYS_BACK)
    papers = []

    for entry in root.findall("atom:entry", namespace):
        try:
            title = entry.find(
                "atom:title", namespace).text.strip().replace("\n", " ")
            summary = entry.find(
                "atom:summary", namespace).text.strip().replace("\n", " ")[:300]
            url = entry.find("atom:id", namespace).text.strip()
            published = entry.find("atom:published", namespace).text.strip()

            # Parse date
            pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
            print(f"[ArXiv] Paper date: {pub_date.date()} — {title[:50]}")

            # Skip papers older than FETCH_DAYS_BACK
            if pub_date < since:
                print(f"[ArXiv] Skipping (too old): {title[:50]}")
                continue

            # Get authors (first 3 only)
            authors = entry.findall("atom:author", namespace)
            author_names = [
                a.find("atom:name", namespace).text for a in authors[:3]]
            author_str = ", ".join(author_names)
            if len(authors) > 3:
                author_str += " et al."

            papers.append({
                "type":         "article",
                "title":        title,
                "url":          url,
                "source":       f"ArXiv — {author_str}",
                "description":  summary,
                "published_at": published,
            })

        except Exception as e:
            print(f"[ArXiv] Error parsing entry: {e}")
            continue

    print(f"[ArXiv] Fetched {len(papers)} papers after date filter.")
    return papers


# ─── Quick test ─────────────────────────────────────────────────────
if __name__ == "__main__":
    papers = fetch_arxiv_papers()
    for p in papers:
        print(f"\n📄 {p['title']}")
        print(f"   Source   : {p['source']}")
        print(f"   URL      : {p['url']}")
        print(f"   Published: {p['published_at']}")
