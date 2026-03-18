import feedparser
import httpx
from youtube_transcript_api import YouTubeTranscriptApi
from backend.config import get_config

RSS_FEEDS = [
    "https://feeds.feedburner.com/oreilly/radar",        # O'Reilly — AI/tech
    "https://techcrunch.com/feed/",                       # TechCrunch — AI & automation news
    "https://venturebeat.com/feed/",                      # VentureBeat — AI focus
    "https://www.artificialintelligence-news.com/feed/",  # AI News
    "https://aiweekly.co/issues.rss",                     # AI Weekly digest
]

def fetch_rss_headlines(max_per_feed=5) -> list[str]:
    """Fetch recent headlines from RSS feeds. Skip unavailable feeds."""
    headlines = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                print(f"[Sources] RSS feed unavailable, skipping: {url}")
                continue
            for entry in feed.entries[:max_per_feed]:
                headlines.append(entry.title)
        except Exception as e:
            print(f"[Sources] RSS error for {url}: {e} — skipping")
            continue
    return headlines

def fetch_reddit_titles(subreddit="artificial", limit=10) -> list[str]:
    """Fetch top post titles from a subreddit."""
    try:
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
        headers = {"User-Agent": "content-pipeline/1.0"}
        resp = httpx.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        posts = resp.json()["data"]["children"]
        return [p["data"]["title"] for p in posts]
    except Exception as e:
        print(f"[Sources] Reddit fetch failed: {e} — skipping")
        return []

def fetch_youtube_transcript(video_id: str) -> str:
    """Fetch transcript from a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t["text"] for t in transcript[:50]])
    except Exception as e:
        print(f"[Sources] YouTube transcript failed for {video_id}: {e}")
        return ""

def gather_all_sources() -> str:
    """Collect all available source content into a single context string."""
    parts = []
    headlines = fetch_rss_headlines()
    if headlines:
        parts.append("RSS Headlines:\n" + "\n".join(headlines))
    for sub in ["artificial", "MachineLearning", "automation"]:
        reddit = fetch_reddit_titles(subreddit=sub, limit=5)
        if reddit:
            parts.append(f"Reddit r/{sub}:\n" + "\n".join(reddit))
    if not parts:
        parts.append("No external sources available — use knowledge base only.")
    return "\n\n".join(parts)
