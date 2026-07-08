"""
Defines the background jobs to be executed by the scheduler.
"""

import logging
import asyncio
from src.ingestion.fetch_feeds import get_all_articles
from src.summarization.summarize import summarize_articles
from src.storage.db import save_facts, get_todays_facts
from src.delivery.telegram_bot import send_daily_facts

logger = logging.getLogger(__name__)

def run_daily_pipeline():
    """
    Executes the daily pipeline:
    1. Fetch articles from RSS feeds
    2. Summarize articles into facts using LLM
    3. Save facts to the database
    4. Send facts to Telegram
    """
    logger.info("--- Starting Daily Pipeline ---")
    
    # 1. Fetch articles
    articles = get_all_articles()
    if not articles:
        logger.warning("No articles fetched today. Aborting pipeline.")
        return
        
    # 2. Summarize
    facts = summarize_articles(articles)
    if not facts:
        logger.warning("Failed to summarize articles. Aborting pipeline.")
        return
        
    # 3. Save to database
    save_facts(facts)
    
    # 4. Fetch the saved facts (this ensures we have IDs and correct structure)
    saved_facts = get_todays_facts()
    if not saved_facts:
        logger.warning("No facts found in database after saving. Aborting delivery.")
        return
        
    # 5. Send to Telegram
    try:
        # Run the async send_daily_facts in a synchronous manner
        asyncio.run(send_daily_facts(saved_facts))
        logger.info("--- Daily Pipeline Completed Successfully ---")
    except Exception as e:
        logger.error(f"Error during Telegram delivery: {e}")

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    print("Running a one-time test of the daily pipeline...")
    # Initialize the DB first to ensure tables exist
    from src.storage.db import init_db
    init_db()
    run_daily_pipeline()
    print("Pipeline execution complete. Check your Telegram channel!")
