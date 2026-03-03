"""
Basic usage examples for the LangGraph Customer Support Agent.
This script demonstrates how to use the support system in your own applications.
"""

from src.config import get_config
from src.graph import create_support_graph, run_customer_support
from src.utils import format_result, batch_process_queries, print_statistics

def example_single_query():
    """Example: Process a single customer query."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Single Query Processing")
    print("="*80)
    
    # Create the support graph
    app = create_support_graph()
    
    # Process a query
    query = "How do I reset my password?"
    result = run_customer_support(query, app)
    
    # Display result
    print(format_result(result))

def example_multiple_queries():
    """Example: Process multiple queries efficiently."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Batch Query Processing")
    print("="*80)
    
    # Create the support graph once
    app = create_support_graph()
    
    # List of queries to process
    queries = [
        "I can't log into my account",
        "Where is my order?",
        "Your service is terrible and I want a refund!",
        "What payment methods do you accept?",
        "How do I change my subscription plan?"
    ]
    
    # Process all queries
    results = batch_process_queries(queries, app)
    
    # Display all results
    for result in results:
        print(format_result(result))
        print()
    
    # Print statistics
    print_statistics(results)

def example_custom_handling():
    """Example: Custom handling of different response types."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Custom Response Handling")
    print("="*80)
    
    app = create_support_graph()
    
    queries = [
        "I'm having trouble with the API",
        "Can you help me with billing?",
        "This is completely unacceptable!"
    ]
    
    for query in queries:
        result = run_customer_support(query, app)
        
        print(f"\nQuery: {query}")
        print(f"Category: {result['category']}")
        print(f"Sentiment: {result['sentiment']}")
        
        # Custom handling based on sentiment
        if result['sentiment'] == 'Negative':
            print("⚠️  HIGH PRIORITY: Negative sentiment detected!")
            print("Action: Escalating to human agent immediately")
        elif result['sentiment'] == 'Neutral':
            print("ℹ️  Standard priority")
        else:
            print("✓ Positive interaction")
        
        print(f"\nResponse: {result['response']}")
        print("-" * 80)

def example_integration():
    """Example: Integrating into an existing application."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Integration Pattern")
    print("="*80)
    
    # Initialize once at application startup
    support_app = create_support_graph()
    
    # Simulate incoming customer queries
    incoming_queries = [
        {"ticket_id": "T001", "query": "Account locked"},
        {"ticket_id": "T002", "query": "Billing question"},
        {"ticket_id": "T003", "query": "Very unhappy customer"}
    ]
    
    print("\nProcessing incoming support tickets...")
    
    for ticket in incoming_queries:
        # Process the query
        result = run_customer_support(ticket["query"], support_app)
        
        # Handle the result in your system
        print(f"\n[Ticket {ticket['ticket_id']}]")
        print(f"Query: {ticket['query']}")
        print(f"Category: {result['category']}")
        print(f"Sentiment: {result['sentiment']}")
        
        # Example: Store in database, send notification, etc.
        if "escalated" in result['response'].lower():
            print("→ Action: Creating escalation ticket")
            print("→ Action: Notifying human agent")
        else:
            print("→ Action: Sending automated response")
        
        print(f"Response: {result['response'][:100]}...")

def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("LangGraph Customer Support Agent - Usage Examples")
    print("="*80)
    
    # Set up configuration
    try:
        config = get_config()
        config.setup_environment()
        print("\n✓ Configuration loaded successfully")
    except Exception as e:
        print(f"\n✗ Configuration error: {e}")
        print("Please ensure you have a .env file with OPENAI_API_KEY set.")
        return
    
    # Run examples
    example_single_query()
    input("\nPress Enter to continue to next example...")
    
    example_multiple_queries()
    input("\nPress Enter to continue to next example...")
    
    example_custom_handling()
    input("\nPress Enter to continue to next example...")
    
    example_integration()
    
    print("\n" + "="*80)
    print("Examples completed!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()