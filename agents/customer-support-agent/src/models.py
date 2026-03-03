"""
Data models and state definitions for the Customer Support Agent.
"""

from typing import TypedDict, Optional

class State(TypedDict):
    """
    State structure for customer support workflow.
    
    Attributes:
        query: The customer's original query text
        category: Classified category (Technical, Billing, or General)
        sentiment: Analyzed sentiment (Positive, Neutral, or Negative)
        response: Generated response or escalation message
    """
    query: str
    category: str
    sentiment: str
    response: str

class QueryCategory:
    """Constants for query categories."""
    TECHNICAL = "Technical"
    BILLING = "Billing"
    GENERAL = "General"

class Sentiment:
    """Constants for sentiment analysis."""
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"