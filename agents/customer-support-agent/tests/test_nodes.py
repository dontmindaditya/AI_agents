"""
Unit tests for node functions.
"""

import pytest
from src.models import State, QueryCategory, Sentiment
from src.nodes import route_query

class TestRouteQuery:
    """Test cases for the route_query function."""
    
    def test_route_negative_sentiment_escalates(self):
        """Test that negative sentiment always routes to escalate."""
        state = {
            "query": "Test query",
            "category": QueryCategory.TECHNICAL,
            "sentiment": Sentiment.NEGATIVE,
            "response": ""
        }
        result = route_query(state)
        assert result == "escalate"
    
    def test_route_technical_category(self):
        """Test routing for technical category with neutral sentiment."""
        state = {
            "query": "Test query",
            "category": QueryCategory.TECHNICAL,
            "sentiment": Sentiment.NEUTRAL,
            "response": ""
        }
        result = route_query(state)
        assert result == "handle_technical"
    
    def test_route_billing_category(self):
        """Test routing for billing category with neutral sentiment."""
        state = {
            "query": "Test query",
            "category": QueryCategory.BILLING,
            "sentiment": Sentiment.NEUTRAL,
            "response": ""
        }
        result = route_query(state)
        assert result == "handle_billing"
    
    def test_route_general_category(self):
        """Test routing for general category with neutral sentiment."""
        state = {
            "query": "Test query",
            "category": QueryCategory.GENERAL,
            "sentiment": Sentiment.NEUTRAL,
            "response": ""
        }
        result = route_query(state)
        assert result == "handle_general"
    
    def test_route_positive_sentiment_respects_category(self):
        """Test that positive sentiment still respects category routing."""
        state = {
            "query": "Test query",
            "category": QueryCategory.BILLING,
            "sentiment": Sentiment.POSITIVE,
            "response": ""
        }
        result = route_query(state)
        assert result == "handle_billing"
    
    def test_route_unknown_category_defaults_to_general(self):
        """Test that unknown categories default to general handling."""
        state = {
            "query": "Test query",
            "category": "Unknown",
            "sentiment": Sentiment.NEUTRAL,
            "response": ""
        }
        result = route_query(state)
        assert result == "handle_general"

class TestEscalate:
    """Test cases for the escalate function."""
    
    def test_escalate_returns_message(self):
        """Test that escalate returns appropriate message."""
        from src.nodes import escalate
        
        state = {
            "query": "Test query",
            "category": QueryCategory.TECHNICAL,
            "sentiment": Sentiment.NEGATIVE,
            "response": ""
        }
        result = escalate(state)
        assert "response" in result
        assert "escalated" in result["response"].lower()
        assert len(result["response"]) > 0

# Note: Full integration tests with actual LLM calls are in test_workflow.py
# These unit tests focus on logic that doesn't require API calls