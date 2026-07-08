"""
Data structures for the storage module.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Fact:
    """
    Represents a single fact extracted from news articles.
    """
    category: str
    fact_text: str
    source_link: Optional[str] = None
    date_added: Optional[str] = None  # Format: YYYY-MM-DD
    times_quizzed: int = 0
    last_quizzed_date: Optional[str] = None
    id: Optional[int] = None
