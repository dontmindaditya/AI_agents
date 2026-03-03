"""
Graph construction and workflow management for the Customer Support Agent.
"""

from langgraph.graph import StateGraph, END
from typing import Dict

from .models import State
from .nodes import (
    categorize,
    analyze_sentiment,
    handle_technical,
    handle_billing,
    handle_general,
    escalate,
    route_query
)

def create_support_graph():
    """
    Create and compile the customer support workflow graph.
    
    Returns:
        Compiled LangGraph application ready for execution
    """
    # Initialize the StateGraph
    workflow = StateGraph(State)
    
    # Add nodes to the graph
    workflow.add_node("categorize", categorize)
    workflow.add_node("analyze_sentiment", analyze_sentiment)
    workflow.add_node("handle_technical", handle_technical)
    workflow.add_node("handle_billing", handle_billing)
    workflow.add_node("handle_general", handle_general)
    workflow.add_node("escalate", escalate)
    
    # Add edges between nodes
    # First, categorize the query
    workflow.add_edge("categorize", "analyze_sentiment")
    
    # Then, route based on sentiment and category
    workflow.add_conditional_edges(
        "analyze_sentiment",
        route_query,
        {
            "handle_technical": "handle_technical",
            "handle_billing": "handle_billing",
            "handle_general": "handle_general",
            "escalate": "escalate"
        }
    )
    
    # All handler nodes lead to END
    workflow.add_edge("handle_technical", END)
    workflow.add_edge("handle_billing", END)
    workflow.add_edge("handle_general", END)
    workflow.add_edge("escalate", END)
    
    # Set the entry point
    workflow.set_entry_point("categorize")
    
    # Compile the graph
    app = workflow.compile()
    
    return app

def run_customer_support(query: str, app=None) -> Dict[str, str]:
    """
    Process a customer query through the LangGraph workflow.
    
    Args:
        query: The customer's query string
        app: Optional pre-compiled graph application (creates new one if None)
        
    Returns:
        Dictionary containing the query's category, sentiment, and response
    """
    if app is None:
        app = create_support_graph()
    
    try:
        # Invoke the workflow with the query
        results = app.invoke({"query": query})
        
        return {
            "query": query,
            "category": results.get("category", "Unknown"),
            "sentiment": results.get("sentiment", "Unknown"),
            "response": results.get("response", "Unable to process query.")
        }
    except Exception as e:
        print(f"Error processing query: {e}")
        return {
            "query": query,
            "category": "Error",
            "sentiment": "Error",
            "response": f"An error occurred while processing your query: {str(e)}"
        }