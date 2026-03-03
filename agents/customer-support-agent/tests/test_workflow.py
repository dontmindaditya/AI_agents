"""
Integration tests for the complete workflow.
These tests require a valid OPENAI_API_KEY in the environment.
"""

import pytest
import os
from src.graph import create_support_graph, run_customer_support
from src.models import QueryCategory, Sentiment

# Skip these tests if no API key is available
pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set in environment"
)

class TestWorkflowIntegration:
    """Integration tests for the complete customer support workflow."""
    
    @pytest.fixture
    def app(self):
        """Create a graph application for testing."""
        return create_support_graph()
    
    def test_technical_query_workflow(self, app):
        """Test complete workflow for a technical query."""
        query = "How do I reset my password?"
        result = run_customer_support(query, app)
        
        assert result["query"] == query
        assert result["category"] in [QueryCategory.TECHNICAL, QueryCategory.GENERAL]
        assert result["sentiment"] in [Sentiment.POSITIVE, Sentiment.NEUTRAL, Sentiment.NEGATIVE]
        assert len(result["response"]) > 0
        assert result["response"] != "Unable to process query."
    
    def test_billing_query_workflow(self, app):
        """Test complete workflow for a billing query."""
        query = "Where can I find my receipt?"
        result = run_customer_support(query, app)
        
        assert result["query"] == query
        assert result["category"] in [QueryCategory.BILLING, QueryCategory.GENERAL]
        assert result["sentiment"] in [Sentiment.POSITIVE, Sentiment.NEUTRAL, Sentiment.NEGATIVE]
        assert len(result["response"]) > 0
    
    def test_general_query_workflow(self, app):
        """Test complete workflow for a general query."""
        query = "What are your business hours?"
        result = run_customer_support(query, app)
        
        assert result["query"] == query
        assert result["sentiment"] in [Sentiment.POSITIVE, Sentiment.NEUTRAL, Sentiment.NEGATIVE]
        assert len(result["response"]) > 0
    
    def test_negative_sentiment_escalation(self, app):
        """Test that negative sentiment triggers escalation."""
        query = "I'm very frustrated with your terrible service!"
        result = run_customer_support(query, app)
        
        assert result["query"] == query
        # Negative sentiment should trigger escalation
        # Check for escalation keywords in response
        assert any(word in result["response"].lower() for word in ["escalated", "human agent", "concern"])
    
    def test_multiple_queries_batch(self, app):
        """Test processing multiple queries in sequence."""
        queries = [
            "How do I update my email?",
            "I was charged twice",
            "What's your return policy?"
        ]
        
        results = []
        for query in queries:
            result = run_customer_support(query, app)
            results.append(result)
        
        # All queries should be processed
        assert len(results) == len(queries)
        
        # All should have valid responses
        for result in results:
            assert len(result["response"]) > 0
            assert result["category"] != "Error"
    
    def test_empty_query_handling(self, app):
        """Test handling of edge case: empty query."""
        query = ""
        result = run_customer_support(query, app)
        
        # Should still return a valid result structure
        assert "response" in result
        assert "category" in result
        assert "sentiment" in result

class TestGraphCreation:
    """Tests for graph creation and structure."""
    
    def test_create_graph_succeeds(self):
        """Test that graph creation doesn't raise errors."""
        app = create_support_graph()
        assert app is not None
    
    def test_graph_has_required_nodes(self):
        """Test that graph contains all required nodes."""
        app = create_support_graph()
        graph = app.get_graph()
        
        # Get node names from the graph
        node_names = [node.name for node in graph.nodes.values()]
        
        # Check for required nodes
        required_nodes = [
            "categorize",
            "analyze_sentiment",
            "handle_technical",
            "handle_billing",
            "handle_general",
            "escalate"
        ]
        
        for node in required_nodes:
            assert node in node_names, f"Missing required node: {node}"