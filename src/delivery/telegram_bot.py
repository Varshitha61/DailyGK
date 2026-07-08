"""
Module for sending messages and quizzes via Telegram.
"""
import os
import logging
import asyncio
from typing import List
from dotenv import load_dotenv
from telegram import Bot
from telegram.constants import ParseMode

import sys
from pathlib import Path
if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent.parent))

from src.ingestion.fetch_feeds import load_settings
from src.storage.models import Fact
from src.storage.db import get_todays_facts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def send_daily_facts(facts: List[Fact] = None):
    """
    Formats and sends the daily facts to the configured Telegram channel.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set.")
        return
        
    settings = load_settings()
    channel_id = settings.get("telegram", {}).get("channel_id")
    if not channel_id:
        logger.error("telegram.channel_id not found in settings.yaml")
        return

    if facts is None:
        facts = get_todays_facts()
        
    if not facts:
        logger.info("No facts found for today to send.")
        return

    # Format the message
    message = "📅 *Today's Top GK & Current Affairs*\n\n"
    
    # Group by category
    categories = {}
    for fact in facts:
        if fact.category not in categories:
            categories[fact.category] = []
        categories[fact.category].append(fact)
        
    for category, facts_in_cat in categories.items():
        message += f"*{category}*\n"
        for fact in facts_in_cat:
            text = fact.fact_text
            link = fact.source_link
            if link:
                message += f"• {text} [Link]({link})\n"
            else:
                message += f"• {text}\n"
        message += "\n"
        
    message += "_Stay updated, stay ahead!_"

    bot = Bot(token=token)
    
    try:
        logger.info(f"Sending daily facts to {channel_id}...")
        await bot.send_message(
            chat_id=channel_id,
            text=message,
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info("Successfully sent daily facts to Telegram.")
    except Exception as e:
        logger.error(f"Failed to send message to Telegram: {e}")

async def send_quiz_poll(question: str, options: List[str], correct_option_id: int):
    """
    Sends a native Telegram quiz poll to the configured channel.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set.")
        return
        
    settings = load_settings()
    channel_id = settings.get("telegram", {}).get("channel_id")
    if not channel_id:
        logger.error("telegram.channel_id not found in settings.yaml")
        return

    bot = Bot(token=token)
    try:
        logger.info(f"Sending quiz poll to {channel_id}...")
        await bot.send_poll(
            chat_id=channel_id,
            question=question,
            options=options,
            type="quiz",
            correct_option_id=correct_option_id,
            is_anonymous=True
        )
        logger.info("Successfully sent quiz poll.")
    except Exception as e:
        logger.error(f"Failed to send quiz poll to Telegram: {e}")

def run_send_daily_facts(facts: List[Fact] = None):
    """Synchronous wrapper for send_daily_facts."""
    asyncio.run(send_daily_facts(facts))

def run_send_quiz_poll(question: str, options: List[str], correct_option_id: int):
    """Synchronous wrapper for send_quiz_poll."""
    asyncio.run(send_quiz_poll(question, options, correct_option_id))

if __name__ == "__main__":
    print("Testing Telegram Delivery Module...")
    # Will send the dummy facts we inserted in Step 3
    run_send_daily_facts()
