"""
Database operations for the DailyGK bot.
Handles SQLite connection, schema creation, insert/query functions.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import sys

# Append parent dir to path if run directly for testing
if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent.parent))

from src.storage.models import Fact

logger = logging.getLogger(__name__)
DB_PATH = Path("data/dailygk.db")

def get_connection() -> sqlite3.Connection:
    """
    Returns a connection to the SQLite database.
    Creates the data directory if it doesn't exist.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database schema.
    """
    logger.info("Initializing database schema...")
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DROP TABLE IF EXISTS facts')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_added TEXT NOT NULL,
                    headline TEXT NOT NULL,
                    beat TEXT NOT NULL,
                    core_fact TEXT NOT NULL,
                    why_it_matters TEXT NOT NULL,
                    quick_context TEXT,
                    number_or_name TEXT,
                    static_link TEXT,
                    source_link TEXT,
                    times_quizzed INTEGER DEFAULT 0,
                    last_quizzed_date TEXT
                )
            ''')
            conn.commit()
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database schema: {e}")

def save_facts(facts: List[dict]):
    """
    Saves a list of facts to the database.
    
    Args:
        facts: List of dictionaries containing 'category' and 'fact_text'.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    inserted_count = 0
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            for fact in facts:
                try:
                    link = fact.get('source_link', '')
                    cursor.execute('''
                        INSERT INTO facts (date_added, headline, beat, core_fact, why_it_matters, quick_context, number_or_name, static_link, source_link)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        today_str, 
                        fact['headline'], 
                        fact['beat'], 
                        fact['core_fact'], 
                        fact['why_it_matters'],
                        fact.get('quick_context', ''),
                        fact.get('number_or_name', ''),
                        fact.get('static_link', ''),
                        link
                    ))
                    inserted_count += 1
                except sqlite3.IntegrityError:
                    # Skip duplicate facts
                    logger.debug(f"Skipped duplicate fact: {fact['headline'][:30]}...")
                    
            conn.commit()
        logger.info(f"Successfully saved {inserted_count} new facts to the database.")
    except Exception as e:
        logger.error(f"Error saving facts to database: {e}")

def get_todays_facts() -> List[Fact]:
    """
    Retrieves all facts added today.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    return get_facts_by_date(today_str)

def get_facts_by_date(date_str: str) -> List[Fact]:
    """
    Retrieves facts for a specific date.
    
    Args:
        date_str: Date string in YYYY-MM-DD format.
    """
    facts = []
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM facts WHERE date_added = ?', (date_str,))
            rows = cursor.fetchall()
            
            for row in rows:
                facts.append(Fact(
                    id=row['id'],
                    date_added=row['date_added'],
                    headline=row['headline'],
                    beat=row['beat'],
                    core_fact=row['core_fact'],
                    why_it_matters=row['why_it_matters'],
                    quick_context=row['quick_context'],
                    number_or_name=row['number_or_name'],
                    static_link=row['static_link'],
                    source_link=row['source_link'],
                    times_quizzed=row['times_quizzed'],
                    last_quizzed_date=row['last_quizzed_date']
                ))
    except Exception as e:
        logger.error(f"Error querying facts for date {date_str}: {e}")
        
    return facts

def get_facts_for_quiz(limit: int = 3) -> List[Fact]:
    """
    Retrieves a list of older facts that have been quizzed the least.
    """
    facts = []
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Order by times_quizzed (ascending) and random to mix things up
            cursor.execute('''
                SELECT * FROM facts 
                ORDER BY times_quizzed ASC, RANDOM()
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            
            for row in rows:
                facts.append(Fact(
                    id=row['id'],
                    date_added=row['date_added'],
                    headline=row['headline'],
                    beat=row['beat'],
                    core_fact=row['core_fact'],
                    why_it_matters=row['why_it_matters'],
                    quick_context=row['quick_context'],
                    number_or_name=row['number_or_name'],
                    static_link=row['static_link'],
                    source_link=row['source_link'],
                    times_quizzed=row['times_quizzed'],
                    last_quizzed_date=row['last_quizzed_date']
                ))
    except Exception as e:
        logger.error(f"Error querying facts for quiz: {e}")
        
    return facts

def increment_quiz_count(fact_id: int):
    """
    Increments the times_quizzed count for a given fact.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE facts 
                SET times_quizzed = times_quizzed + 1, last_quizzed_date = ?
                WHERE id = ?
            ''', (today_str, fact_id))
            conn.commit()
    except Exception as e:
        logger.error(f"Error updating quiz count for fact ID {fact_id}: {e}")

if __name__ == "__main__":
    # Test execution
    print("Testing Storage Module...")
    init_db()
    
    # Save dummy data
    dummy_facts = [
        {
            "headline": "Test Headline",
            "beat": "Science and Technology", 
            "core_fact": "Water boils at 100 degrees Celsius at sea level.",
            "why_it_matters": "Fundamental physics property.",
            "quick_context": "At standard atmospheric pressure.",
            "number_or_name": "100",
            "static_link": "Connected to thermodynamics."
        }
    ]
    save_facts(dummy_facts)
    
    # Retrieve data
    todays_facts = get_todays_facts()
    print(f"\nRetrieved {len(todays_facts)} facts added today:")
    for f in todays_facts:
        print(f"[{f.beat}] {f.headline}")
        
    print("\nStorage Module test complete.")
