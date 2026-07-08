"""
Module for sending messages and quizzes via Telegram.
"""
import os
import logging
import requests
from typing import List
from dotenv import load_dotenv

import sys
from pathlib import Path
if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent.parent))

from src.ingestion.fetch_feeds import load_settings
from src.storage.models import Fact
from src.storage.db import get_todays_facts, get_connection
from src.summarization.summarize import initialize_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def generate_newspaper_image() -> bytes:
    """Uses Gemini API to generate a newspaper-style image."""
    try:
        client = initialize_client()
        prompt = "A highly aesthetic, modern digital newspaper front page titled 'DailyGK', designed specifically for UPSC and SSC aspirants. It features sections for Polity, Economy, and International Relations with engaging infographics, bold headlines, clean layout, sleek dark mode aesthetic with vibrant accent colors (gold and cyan), and a premium, inviting feel that tempts users to read. UI mockup style, high quality, professional."
        response = client.models.generate_images(
            model='imagen-3.0-generate-001',
            prompt=prompt,
            config=dict(number_of_images=1, output_mime_type="image/jpeg")
        )
        for image in response.generated_images:
            return image.image.image_bytes
    except Exception as e:
        logger.error(f"Error generating image: {e}")
    return None

def get_weekly_revision() -> str:
    from datetime import datetime, timedelta
    today = datetime.now()
    if today.weekday() != 6: # 6 is Sunday
        return ""
        
    start_of_week = (today - timedelta(days=6)).strftime("%Y-%m-%d")
    end_of_week = today.strftime("%Y-%m-%d")
    
    rev_msg = "\n\n***\n\n### 📚 End of Week Revision Sheet\n*(A quick recap of the most quiz-worthy keywords grouped by Beat)*\n\n"
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT beat, number_or_name FROM facts 
                WHERE date_added BETWEEN ? AND ?
                ORDER BY beat
            ''', (start_of_week, end_of_week))
            rows = cursor.fetchall()
            
            beats = {}
            for r in rows:
                if r['beat'] not in beats:
                    beats[r['beat']] = []
                if r['number_or_name']:
                    beats[r['beat']].append(r['number_or_name'])
                    
            for b, items in beats.items():
                if items:
                    rev_msg += f"*{b}*\n"
                    for i in items:
                        rev_msg += f"- {i}\n"
                    rev_msg += "\n"
        return rev_msg
    except Exception as e:
        logger.error(f"Failed to generate weekly revision: {e}")
        return ""

async def send_daily_facts(facts: List[Fact] = None):
    """
    Formats and sends the daily facts to the configured Telegram channel using requests.
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

    # Group by beat
    beats = {}
    for fact in facts:
        if fact.beat not in beats:
            beats[fact.beat] = []
        beats[fact.beat].append(fact)
        
    message = "📅 *Today's Top GK & Current Affairs*\n\n"
    
    idx = 1
    for beat, facts_in_beat in beats.items():
        for fact in facts_in_beat:
            message += f"{idx}\\.\n"
            message += f"*Headline* — {fact.headline}\n"
            message += f"*Beat* — {fact.beat}\n"
            message += f"*The Core Fact* — {fact.core_fact}\n"
            message += f"*Why It Matters* — {fact.why_it_matters}\n"
            if fact.quick_context:
                message += f"*Quick Context* — {fact.quick_context}\n"
            if fact.number_or_name:
                message += f"*One Number or Name to Remember* — {fact.number_or_name}\n"
            if fact.static_link:
                message += f"*Static Link* — {fact.static_link}\n"
            if fact.source_link:
                message += f"[Read More]({fact.source_link})\n"
            message += "\n"
            idx += 1
            
    # Add weekly revision if it's Sunday
    message += get_weekly_revision()
    
    # Generate image
    image_bytes = await generate_newspaper_image()

    try:
        logger.info(f"Sending daily facts to {channel_id}...")
        
        # We will use standard Markdown parse mode
        # Because we used `*` for bold and `[]()` for links, standard Markdown is sufficient.
        # However, requests doesn't care, we just pass parse_mode="Markdown"
        
        def send_text_msg(text):
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {"chat_id": channel_id, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
            resp = requests.post(url, json=payload, timeout=30)
            if not resp.json().get("ok"):
                logger.error(f"Telegram API Error: {resp.text}")

        def send_photo_msg(photo_bytes, caption):
            url = f"https://api.telegram.org/bot{token}/sendPhoto"
            data = {"chat_id": channel_id, "caption": caption, "parse_mode": "Markdown"}
            files = {"photo": ("newspaper.jpg", photo_bytes, "image/jpeg")}
            resp = requests.post(url, data=data, files=files, timeout=30)
            if not resp.json().get("ok"):
                logger.error(f"Telegram API Error (Photo): {resp.text}")

        if len(message) > 4000:
            parts = [message[i:i+4000] for i in range(0, len(message), 4000)]
            if image_bytes:
                send_photo_msg(image_bytes, "Today's News Snapshot!")
            for part in parts:
                send_text_msg(part)
        else:
            if image_bytes:
                if len(message) > 1000:
                    send_photo_msg(image_bytes, "Today's News Snapshot!")
                    send_text_msg(message)
                else:
                    send_photo_msg(image_bytes, message)
            else:
                send_text_msg(message)
                
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
