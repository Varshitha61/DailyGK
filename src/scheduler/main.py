"""
Main entry point for the DailyGK bot.
Initializes the database and starts the scheduler.
"""

import logging
import time
import sys
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Ensure src modules can be imported
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.storage.db import init_db
from src.ingestion.fetch_feeds import load_settings
from src.scheduler.jobs import run_daily_pipeline

from src.delivery.quiz_generator import run_quiz_job

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    logger.info("Starting DailyGK Bot Initialization...")
    
    # 1. Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # 2. Initialize Database
    init_db()
    
    # 3. Load Settings
    settings = load_settings()
    schedule_settings = settings.get("schedule", {})
    daily_time_str = schedule_settings.get("daily_job_time", "08:00")
    quiz_time_str = schedule_settings.get("quiz_job_time", "18:00")
    
    try:
        daily_hour, daily_minute = map(int, daily_time_str.split(":"))
    except ValueError:
        logger.error(f"Invalid time format for daily job: {daily_time_str}")
        daily_hour, daily_minute = 8, 0

    try:
        quiz_hour, quiz_minute = map(int, quiz_time_str.split(":"))
    except ValueError:
        logger.error(f"Invalid time format for quiz job: {quiz_time_str}")
        quiz_hour, quiz_minute = 18, 0

    # 4. Initialize Scheduler
    scheduler = BackgroundScheduler()
    
    # Add daily pipeline job
    scheduler.add_job(
        run_daily_pipeline,
        trigger=CronTrigger(hour=daily_hour, minute=daily_minute),
        id="daily_pipeline_job",
        name="Daily Content Ingestion and Delivery",
        replace_existing=True
    )
    
    # Add quiz generation job
    scheduler.add_job(
        run_quiz_job,
        trigger=CronTrigger(hour=quiz_hour, minute=quiz_minute),
        id="quiz_generator_job",
        name="Spaced Repetition Quiz Generator",
        replace_existing=True
    )
    
    logger.info(f"Daily pipeline scheduled to run at {daily_hour:02d}:{daily_minute:02d} every day.")
    logger.info(f"Quiz generator scheduled to run at {quiz_hour:02d}:{quiz_minute:02d} every day.")
    
    # 5. Start Scheduler
    scheduler.start()
    logger.info("Scheduler started successfully. Press Ctrl+C to exit.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
        scheduler.shutdown()
        logger.info("DailyGK Bot stopped.")

if __name__ == "__main__":
    main()
