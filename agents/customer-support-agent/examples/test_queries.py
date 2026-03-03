"""
Comprehensive test queries for the Customer Support Agent.
This module contains various test queries organized by category and sentiment.
"""

# Technical queries
TECHNICAL_QUERIES = [
    "How do I reset my password?",
    "I can't log into my account",
    "The app keeps crashing on my phone",
    "My internet connection keeps dropping",
    "I'm getting an error code 500",
    "How do I integrate the API?",
    "The website is loading very slowly",
    "I need help talking to chatGPT",
    "My two-factor authentication isn't working",
    "How do I export my data?"
]

# Billing queries
BILLING_QUERIES = [
    "Where can I find my receipt?",
    "I was charged twice for the same order",
    "How do I update my payment method?",
    "What payment methods do you accept?",
    "I want to cancel my subscription",
    "When will I be charged for my subscription?",
    "Can I get a refund?",
    "I didn't authorize this charge",
    "How do I upgrade my plan?",
    "Are there any discounts available?"
]

# General queries
GENERAL_QUERIES = [
    "What are your business hours?",
    "How do I contact customer support?",
    "Where is your office located?",
    "Do you offer international shipping?",
    "What is your return policy?",
    "How long does delivery take?",
    "Can you recommend some features for my use case?",
    "Do you have a mobile app?",
    "Is my data secure?",
    "What's new in the latest update?"
]

# Negative sentiment queries
NEGATIVE_QUERIES = [
    "I'm very frustrated with your terrible service!",
    "This is completely unacceptable!",
    "Your product is broken and I want my money back!",
    "I've been waiting for hours with no response!",
    "This is the worst experience I've ever had!",
    "I'm extremely disappointed with your company",
    "Your service is a complete joke!",
    "I demand to speak to a manager right now!",
    "I will never use your service again!",
    "This is ridiculous and unprofessional!"
]

# Positive sentiment queries
POSITIVE_QUERIES = [
    "I love your product! Can you help me with a small issue?",
    "Thank you so much for your great service!",
    "Your support team is amazing! Quick question...",
    "I'm really impressed with your platform!",
    "Great job on the new features! How do I access them?",
    "Your product has been a game-changer for my business!",
    "I appreciate your quick response! One more thing...",
    "Everything works perfectly! Just curious about...",
    "Best customer service I've experienced!",
    "I recommend your service to everyone!"
]

# Edge case queries
EDGE_CASE_QUERIES = [
    "",  # Empty query
    "?",  # Single character
    "help",  # Single word
    "a" * 500,  # Very long query
    "How do I... uh... what was I going to ask?",  # Incomplete thought
    "billing technical general",  # Multiple categories
    "😊 😊 😊",  # Only emojis
    "HELP!!!!!!!!!",  # All caps with punctuation
    "Can you help me with... never mind",  # Changed mind
    "I don't know what I need help with"  # Unclear request
]

# All queries combined
ALL_QUERIES = (
    TECHNICAL_QUERIES +
    BILLING_QUERIES +
    GENERAL_QUERIES +
    NEGATIVE_QUERIES +
    POSITIVE_QUERIES +
    EDGE_CASE_QUERIES
)

def get_queries_by_category(category: str) -> list:
    """
    Get queries filtered by expected category.
    
    Args:
        category: One of 'technical', 'billing', 'general', 'negative', 'positive', 'edge'
        
    Returns:
        List of queries for that category
    """
    category_map = {
        'technical': TECHNICAL_QUERIES,
        'billing': BILLING_QUERIES,
        'general': GENERAL_QUERIES,
        'negative': NEGATIVE_QUERIES,
        'positive': POSITIVE_QUERIES,
        'edge': EDGE_CASE_QUERIES
    }
    return category_map.get(category.lower(), [])

def run_test_suite():
    """Run a comprehensive test suite with all queries."""
    from src.graph import create_support_graph, run_customer_support
    from src.utils import print_statistics
    
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    # Create the support graph
    print("\nInitializing support system...")
    app = create_support_graph()
    
    # Test each category
    categories = [
        ("Technical Queries", TECHNICAL_QUERIES),
        ("Billing Queries", BILLING_QUERIES),
        ("General Queries", GENERAL_QUERIES),
        ("Negative Sentiment Queries", NEGATIVE_QUERIES),
        ("Positive Sentiment Queries", POSITIVE_QUERIES),
        ("Edge Case Queries", EDGE_CASE_QUERIES)
    ]
    
    all_results = []
    
    for category_name, queries in categories:
        print(f"\n{'='*80}")
        print(f"Testing: {category_name} ({len(queries)} queries)")
        print(f"{'='*80}")
        
        category_results = []
        for i, query in enumerate(queries, 1):
            print(f"\nQuery {i}/{len(queries)}: {query[:50]}{'...' if len(query) > 50 else ''}")
            result = run_customer_support(query, app)
            category_results.append(result)
            all_results.append(result)
            print(f"→ Category: {result['category']}, Sentiment: {result['sentiment']}")
        
        # Print category statistics
        print_statistics(category_results)
        
        if category_name != categories[-1][0]:
            input("\nPress Enter to continue to next category...")
    
    # Print overall statistics
    print("\n" + "="*80)
    print("OVERALL TEST SUITE RESULTS")
    print("="*80)
    print_statistics(all_results)
    
    return all_results

if __name__ == "__main__":
    # Set up configuration
    from src.config import get_config
    
    try:
        config = get_config()
        config.setup_environment()
        print("✓ Configuration loaded successfully")
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        print("Please ensure you have a .env file with OPENAI_API_KEY set.")
        exit(1)
    
    # Run the test suite
    run_test_suite()