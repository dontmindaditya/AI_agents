"""
LangGraph Customer Support Agent
A sophisticated customer support system using LangGraph for query routing and handling.
"""

__version__ = "1.0.0"
__author__ = "Aditya Pamar"

from .models import State
from .graph import create_support_graph
from .nodes import (
    categorize,
    analyze_sentiment,
    handle_technical,
    handle_billing,
    handle_general,
    escalate,
    route_query
)

__all__ = [
    "State",
    "create_support_graph",
    "categorize",
    "analyze_sentiment",
    "handle_technical",
    "handle_billing",
    "handle_general",
    "escalate",
    "route_query"
]