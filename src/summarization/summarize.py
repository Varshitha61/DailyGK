"""
Module for summarizing news articles into concise facts using Gemini.
"""

import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from pydantic import BaseModel
from google import genai
from google.genai import types

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Pydantic models for structured output
class Fact(BaseModel):
    category: str
    fact_text: str
    source_link: str

class FactList(BaseModel):
    facts: list[Fact]

def initialize_client() -> genai.Client:
    """Initializes and returns the Gemini client."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable is not set.")
        raise ValueError("GEMINI_API_KEY is missing.")
    return genai.Client(api_key=api_key)

def summarize_articles(articles: List[Dict[str, str]], target_count: int = 10) -> List[Dict[str, str]]:
    """
    Summarizes a list of articles into concise factual points.
    
    Args:
        articles: List of article dictionaries (title, summary, source).
        target_count: Approximate number of facts to generate.
        
    Returns:
        List of dictionaries containing 'category', 'fact_text', and 'source_link'.
    """
    if not articles:
        logger.warning("No articles provided for summarization.")
        return []
        
    try:
        client = initialize_client()
    except ValueError:
        return []

    # Prepare input text (limiting to top 50 to avoid massive prompt size)
    articles_to_process = articles[:50]
    input_text = "Here are the top news articles of the day:\n\n"
    for idx, article in enumerate(articles_to_process, 1):
        input_text += f"Article {idx}:\nTitle: {article.get('title')}\n"
        input_text += f"Link: {article.get('link')}\n"
        input_text += f"Summary: {article.get('summary')}\n\n"

    prompt = (
        f"You are an expert news curator for UPSC (Union Public Service Commission) civil services candidates.\n"
        f"Your task is to review the provided daily news articles and extract {target_count} highly important, factual one-line news updates.\n"
        "The points should strictly cover current affairs highly relevant to the UPSC syllabus.\n"
        "Focus heavily on distinguishing:\n"
        "1. Major 'India News' and national developments.\n"
        "2. Major 'International News' and geopolitics.\n"
        "Each fact must include the EXACT 'source_link' from the article it was extracted from.\n"
        "Each fact must be tagged with an appropriate category from: India News, International News, Economy, Environment & Science, Polity & Governance, Miscellaneous.\n"
        "Keep the facts objective, analytical, concise, and easy to read. DO NOT hallucinate; rely strictly on the provided articles."
    )

    logger.info(f"Sending {len(articles_to_process)} articles to Gemini for summarization...")
    
    try:
        # Use gemini-2.5-flash for fast and cheap processing, supports structured output
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, input_text],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=FactList,
                temperature=0.2,
            ),
        )
        
        # Parse the structured response
        fact_list_data = response.parsed
        if not fact_list_data or not hasattr(fact_list_data, 'facts'):
            logger.error("Failed to parse structured facts from Gemini response.")
            return []
            
        structured_facts = [
            {"category": fact.category, "fact_text": fact.fact_text, "source_link": fact.source_link}
            for fact in fact_list_data.facts
        ]
        
        logger.info(f"Successfully generated {len(structured_facts)} facts.")
        return structured_facts
        
    except Exception as e:
        logger.error(f"Error during summarization with Gemini API: {e}")
        return []

if __name__ == "__main__":
    # Test execution
    print("Testing Summarization Module...")
    # Add dummy api key for local test if not present
    if not os.environ.get("GEMINI_API_KEY"):
        print("Please set GEMINI_API_KEY in your .env file to run this test.")
        os.environ["GEMINI_API_KEY"] = "dummy_key_just_for_import"
        
    # We will import ingestion module to test the pipeline
    try:
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent.parent))
        from src.ingestion.fetch_feeds import get_all_articles
        
        articles = get_all_articles()
        if not articles:
            print("No articles fetched, test aborted.")
        else:
            print(f"Fetched {len(articles)} articles. Generating facts...")
            facts = summarize_articles(articles)
            print("\nGenerated Facts:")
            for f in facts:
                print(f"[{f['category']}] {f['fact_text']}")
    except Exception as e:
        print(f"Test failed: {e}")
