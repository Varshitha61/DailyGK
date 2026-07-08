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
    headline: str
    beat: str
    core_fact: str
    why_it_matters: str
    quick_context: Optional[str] = None
    number_or_name: str = ""
    static_link: Optional[str] = None
    source_link: Optional[str] = None
    date_added: Optional[str] = None  # Format: YYYY-MM-DD
    times_quizzed: int = 0
    last_quizzed_date: Optional[str] = None
    id: Optional[int] = None
