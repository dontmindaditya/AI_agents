"""
Standalone Paper2Code Test Script
No config files needed - just set your API key below
"""

import os
from crewai import Agent, Task

# SET YOUR API KEY HERE
os.environ["ANTHROPIC_API_KEY"] = "your-key-here"  # <-- ADD YOUR KEY
# OR use OpenAI:
# os.environ["OPENAI_API_KEY"] = "your-key-here"

def quick_paper_to_code(algorithm_description: str, language: str = "python"):
    """
    Convert algorithm description to code
    
    Args:
        algorithm_description: Text description of algorithm
        language: Programming language (python, javascript, etc)
    """
    
    # Create Code Generator Agent
    coder = Agent(
        role="Expert Software Developer",
        goal=f"Write clean, production-ready {language} code",
        backstory="""You are a world-class developer who writes elegant, 
        efficient code with proper documentation and error handling.""",
        verbose=True,
        allow_delegation=False
    )
    
    # Create task
    task = Task(
        description=f"""
Implement this algorithm in {language}:

{algorithm_description}

Requirements:
1. Complete, working implementation
2. Comprehensive docstrings/comments
3. Type hints (if applicable)
4. Error handling
5. Usage example

Return only the code, properly formatted.
""",
        agent=coder,
        expected_output=f"Complete {language} code with documentation"
    )
    
    # Execute using Crew
    from crewai import Crew, Process
    
    crew = Crew(
        agents=[coder],
        tasks=[task],
        process=Process.sequential,
        verbose=False
    )
    
    print(f"\n🤖 Generating {language} code...\n")
    result = crew.kickoff()
    
    # Extract string from CrewOutput
    result_str = result.raw if hasattr(result, 'raw') else str(result)
    
    # Extract code
    if f'```{language}' in result_str:
        code = result_str.split(f'```{language}')[1].split('```')[0].strip()
    elif '```' in result_str:
        code = result_str.split('```')[1].split('```')[0].strip()
    else:
        code = result_str
    
    return code


# Example Usage
if __name__ == "__main__":
    # Test 1: Simple algorithm
    print("="*60)
    print("Test 1: Binary Search")
    print("="*60)
    
    binary_search_desc = """
    Binary Search Algorithm:
    - Works on sorted arrays
    - Repeatedly divides search interval in half
    - Returns index of target element or -1 if not found
    - Time complexity: O(log n)
    - Space complexity: O(1)
    """
    
    code = quick_paper_to_code(binary_search_desc, "python")
    
    print("\n✅ Generated Code:")
    print("-"*60)
    print(code)
    print("-"*60)
    
    # Save to file
    with open("binary_search.py", "w") as f:
        f.write(code)
    print("\n💾 Saved to: binary_search.py")
    
    # Test 2: Try your own
    print("\n" + "="*60)
    print("Try your own algorithm!")
    print("="*60)
    
    custom_desc = input("\nDescribe an algorithm (or press Enter to skip): ").strip()
    
    if custom_desc:
        code = quick_paper_to_code(custom_desc, "python")
        print("\n✅ Generated Code:")
        print("-"*60)
        print(code)
        print("-"*60)