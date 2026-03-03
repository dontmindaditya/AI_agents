"""
Main entry point for the LangGraph Customer Support Agent.
Provides a simple CLI interface for testing the support system.
"""

import sys
from colorama import init, Fore, Style

from src.config import get_config
from src.graph import create_support_graph, run_customer_support
from src.utils import format_result

# Initialize colorama for colored terminal output
init(autoreset=True)

def print_banner():
    """Print application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        LangGraph Customer Support Agent v1.0.0               ║
    ║        Intelligent Query Routing and Response System         ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(Fore.CYAN + banner)

def print_menu():
    """Print the main menu options."""
    print("\n" + Fore.YELLOW + "Options:")
    print("  1. Enter a single query")
    print("  2. Run test queries")
    print("  3. Exit")
    print()

def run_single_query(app):
    """Handle single query input and processing."""
    print(Fore.GREEN + "\nEnter your customer support query:")
    query = input(Fore.WHITE + "> ").strip()
    
    if not query:
        print(Fore.RED + "Empty query. Please try again.")
        return
    
    print(Fore.CYAN + "\nProcessing query...\n")
    result = run_customer_support(query, app)
    print(format_result(result))

def run_test_queries(app):
    """Run predefined test queries."""
    test_queries = [
        "My internet connection keeps dropping. Can you help?",
        "I need help talking to chatGPT",
        "Where can I find my receipt?",
        "What are your business hours?",
        "I'm very frustrated with your service! This is unacceptable!",
        "How do I reset my password?",
        "I was charged twice for the same order",
        "Can you recommend some features for my use case?"
    ]
    
    print(Fore.CYAN + f"\nRunning {len(test_queries)} test queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(Fore.YELLOW + f"\n{'='*80}")
        print(Fore.YELLOW + f"Test Query {i}/{len(test_queries)}")
        print(Fore.YELLOW + f"{'='*80}")
        result = run_customer_support(query, app)
        print(format_result(result))
        
        if i < len(test_queries):
            input(Fore.CYAN + "\nPress Enter to continue to next test query...")

def main():
    """Main application loop."""
    print_banner()
    
    # Initialize configuration
    try:
        config = get_config()
        config.setup_environment()
        print(Fore.GREEN + "✓ Configuration loaded successfully")
    except Exception as e:
        print(Fore.RED + f"✗ Configuration error: {e}")
        print(Fore.YELLOW + "Please ensure you have a .env file with OPENAI_API_KEY set.")
        sys.exit(1)
    
    # Create the support graph
    try:
        print(Fore.GREEN + "✓ Building customer support workflow...")
        app = create_support_graph()
        print(Fore.GREEN + "✓ Workflow ready!")
    except Exception as e:
        print(Fore.RED + f"✗ Error creating workflow: {e}")
        sys.exit(1)
    
    # Main application loop
    while True:
        print_menu()
        choice = input(Fore.WHITE + "Select an option (1-3): ").strip()
        
        if choice == "1":
            run_single_query(app)
        elif choice == "2":
            run_test_queries(app)
        elif choice == "3":
            print(Fore.CYAN + "\nThank you for using the Customer Support Agent!")
            print(Fore.CYAN + "Goodbye!\n")
            break
        else:
            print(Fore.RED + "Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\nApplication interrupted by user.")
        print(Fore.CYAN + "Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"\n\nUnexpected error: {e}")
        sys.exit(1)