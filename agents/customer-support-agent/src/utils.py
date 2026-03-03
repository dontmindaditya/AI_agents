"""
Utility functions for the Customer Support Agent.
"""

from typing import Dict
from IPython.display import Image, display
from langchain_core.runnables.graph import MermaidDrawMethod

def visualize_graph(app):
    """
    Visualize the LangGraph workflow using Mermaid.
    
    Args:
        app: Compiled LangGraph application
        
    Returns:
        None (displays the graph visualization)
    """
    try:
        display(
            Image(
                app.get_graph().draw_mermaid_png(
                    draw_method=MermaidDrawMethod.API,
                )
            )
        )
    except Exception as e:
        print(f"Unable to visualize graph: {e}")
        print("Graph visualization requires IPython and network access.")

def format_result(result: Dict[str, str], verbose: bool = True) -> str:
    """
    Format the result dictionary into a readable string.
    
    Args:
        result: Dictionary containing query, category, sentiment, and response
        verbose: Whether to include all details or just the response
        
    Returns:
        Formatted string representation of the result
    """
    if not verbose:
        return result.get("response", "No response available")
    
    output = []
    output.append("=" * 80)
    output.append(f"Query: {result.get('query', 'N/A')}")
    output.append("-" * 80)
    output.append(f"Category: {result.get('category', 'N/A')}")
    output.append(f"Sentiment: {result.get('sentiment', 'N/A')}")
    output.append("-" * 80)
    output.append(f"Response:\n{result.get('response', 'N/A')}")
    output.append("=" * 80)
    
    return "\n".join(output)

def batch_process_queries(queries: list, app=None) -> list:
    """
    Process multiple queries in batch.
    
    Args:
        queries: List of query strings
        app: Optional pre-compiled graph application
        
    Returns:
        List of result dictionaries
    """
    from .graph import run_customer_support
    
    if app is None:
        from .graph import create_support_graph
        app = create_support_graph()
    
    results = []
    for query in queries:
        result = run_customer_support(query, app)
        results.append(result)
    
    return results

def print_statistics(results: list) -> None:
    """
    Print statistics from a batch of results.
    
    Args:
        results: List of result dictionaries
    """
    if not results:
        print("No results to analyze.")
        return
    
    total = len(results)
    categories = {}
    sentiments = {}
    escalations = 0
    
    for result in results:
        # Count categories
        category = result.get("category", "Unknown")
        categories[category] = categories.get(category, 0) + 1
        
        # Count sentiments
        sentiment = result.get("sentiment", "Unknown")
        sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
        
        # Count escalations
        if "escalated" in result.get("response", "").lower():
            escalations += 1
    
    print("\n" + "=" * 80)
    print("BATCH PROCESSING STATISTICS")
    print("=" * 80)
    print(f"Total Queries Processed: {total}")
    print("\nCategory Distribution:")
    for category, count in categories.items():
        percentage = (count / total) * 100
        print(f"  {category}: {count} ({percentage:.1f}%)")
    
    print("\nSentiment Distribution:")
    for sentiment, count in sentiments.items():
        percentage = (count / total) * 100
        print(f"  {sentiment}: {count} ({percentage:.1f}%)")
    
    print(f"\nEscalations: {escalations} ({(escalations/total)*100:.1f}%)")
    print("=" * 80 + "\n")