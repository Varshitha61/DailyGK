"""
Module for fetching and parsing RSS feeds.

Provides functions to read RSS feed URLs from settings and parse them using feedparser.
"""

import feedparser
import yaml
import logging
from pathlib import Path
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def load_settings(config_path: str = "config/settings.yaml") -> Dict[str, Any]:
    """
    Loads configuration settings from a YAML file.
    
    Args:
        config_path: Path to the settings.yaml file.
        
    Returns:
        Dictionary containing configuration settings.
    """
    try:
        path = Path(config_path)
        if not path.exists():
            # Support calling from src directory or project root
            alt_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
            if alt_path.exists():
                path = alt_path
            else:
                logger.error(f"Configuration file not found at {config_path} or {alt_path}")
                return {}

        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load settings from {config_path}: {e}")
        return {}

def fetch_feed_articles(feed_url: str, source_name: str) -> List[Dict[str, str]]:
    """
    Fetches articles from a single RSS feed.
    
    Args:
        feed_url: The URL of the RSS feed.
        source_name: The name of the feed source for tracking.
        
    Returns:
        A list of parsed articles (dictionaries containing title, link, summary, etc.).
    """
    articles = []
    logger.info(f"Fetching RSS feed from: {feed_url}")
    try:
        parsed_feed = feedparser.parse(feed_url)
        
        if parsed_feed.bozo:
            logger.warning(f"Feedparser reported formatting issues for {feed_url} (bozo=True)")
            
        for entry in parsed_feed.entries:
            article = {
                "source": source_name,
                "title": entry.get("title", "No Title"),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "published": entry.get("published", "")
            }
            articles.append(article)
            
        logger.info(f"Successfully fetched {len(articles)} articles from {source_name}")
    except Exception as e:
        logger.error(f"Failed to fetch feed {feed_url}: {e}")
        
    return articles

def get_all_articles() -> List[Dict[str, str]]:
    """
    Reads feeds from settings and aggregates articles from all feeds.
    
    Returns:
        A combined list of all articles fetched from configured feeds.
    """
    settings = load_settings()
    feeds = settings.get("feeds", [])
    
    if not feeds:
        logger.warning("No feeds configured in settings.yaml")
        return []
        
    all_articles = []
    for feed in feeds:
        name = feed.get("name", "Unknown Source")
        url = feed.get("url")
        if url:
            articles = fetch_feed_articles(url, name)
            all_articles.extend(articles)
        else:
            logger.warning(f"Feed '{name}' is missing a URL configuration")
            
    return all_articles

if __name__ == "__main__":
    # Test execution when run directly
    print("Testing Ingestion Module...")
    articles = get_all_articles()
    print(f"Total articles fetched: {len(articles)}")
    if articles:
        print("\nSample of the first article:")
        for key, value in articles[0].items():
            print(f"{key}: {value[:200]}..." if len(str(value)) > 200 else f"{key}: {value}")
