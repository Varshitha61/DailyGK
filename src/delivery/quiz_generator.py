"""
Module to generate and deliver spaced-repetition quizzes.
"""
import logging
from pydantic import BaseModel
from google import genai
from google.genai import types

import sys
from pathlib import Path
if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent.parent))

from src.storage.db import get_facts_for_quiz, increment_quiz_count
from src.summarization.summarize import initialize_client
from src.delivery.telegram_bot import run_send_quiz_poll

logger = logging.getLogger(__name__)

class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    correct_option_index: int

def generate_quiz_from_fact(fact_text: str) -> QuizQuestion:
    """
    Uses Gemini to generate a 4-option multiple choice question based on a fact.
    """
    try:
        client = initialize_client()
    except ValueError:
        logger.error("Failed to initialize Gemini client. Cannot generate quiz.")
        return None
        
    prompt = (
        "You are an expert quiz master. Convert the following fact into a multiple-choice question.\n"
        "Generate a clear question, 4 plausible options, and provide the zero-based index (0, 1, 2, or 3) of the correct option.\n"
        "Do not include the correct answer in the text of the other options.\n"
        f"Fact: {fact_text}"
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=QuizQuestion,
                temperature=0.4,
            ),
        )
        
        quiz_data = response.parsed
        if not quiz_data or len(quiz_data.options) != 4:
            logger.error("Failed to parse valid 4-option quiz from Gemini.")
            return None
            
        return quiz_data
    except Exception as e:
        logger.error(f"Error generating quiz with Gemini API: {e}")
        return None

def run_quiz_job():
    """
    Selects older facts, generates quizzes, and sends them to Telegram.
    """
    logger.info("--- Starting Quiz Job ---")
    
    # 1. Select facts
    facts = get_facts_for_quiz(limit=3)
    if not facts:
        logger.info("No facts available for quiz yet.")
        return
        
    for fact in facts:
        logger.info(f"Generating quiz for fact ID {fact.id}: {fact.fact_text[:30]}...")
        quiz = generate_quiz_from_fact(fact.fact_text)
        
        if quiz:
            # Send poll
            run_send_quiz_poll(
                question=quiz.question,
                options=quiz.options,
                correct_option_id=quiz.correct_option_index
            )
            # Update spaced repetition count
            if fact.id is not None:
                increment_quiz_count(fact.id)
            
    logger.info("--- Quiz Job Completed ---")

if __name__ == "__main__":
    print("Testing Quiz Generator...")
    from src.storage.db import init_db
    init_db()
    run_quiz_job()
