"""
Example: Using EduGPT to learn Reinforcement Learning

This example demonstrates the complete workflow:
1. Setting up agents
2. Generating syllabus through discussion
3. Interactive teaching session
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator import TeachingOrchestrator
from utils.logger import AgentLogger


def main():
    """Run example for Reinforcement Learning topic"""
    
    print("=" * 70)
    print("EduGPT Example: Learning Reinforcement Learning")
    print("=" * 70)
    
    # Initialize orchestrator
    topic = "Reinforcement Learning"
    orchestrator = TeachingOrchestrator(
        topic=topic,
        max_discussion_rounds=5,
        save_artifacts=True,
        output_dir="./outputs/reinforcement_learning"
    )
    
    agent_logger = AgentLogger()
    
    # Step 1: Setup
    print("\n[STEP 1] Setting up agents...")
    orchestrator.setup()
    print("✓ Agents initialized")
    
    # Step 2: Generate Syllabus
    print("\n[STEP 2] Generating syllabus through agent discussion...")
    
    def print_discussion_update(round_num: int, agent: str, message: str):
        agent_name = "Agent 1" if agent == "agent1" else "Agent 2"
        print(f"  Round {round_num} - {agent_name}: {len(message)} chars")
    
    syllabus = orchestrator.generate_syllabus(discussion_callback=print_discussion_update)
    
    print("\n✓ Syllabus generated!")
    print("\n" + "=" * 70)
    print("GENERATED SYLLABUS")
    print("=" * 70)
    print(syllabus)
    print("=" * 70)
    
    # Step 3: Teaching Session
    print("\n[STEP 3] Starting teaching session...")
    opening = orchestrator.start_teaching()
    
    print("\n" + "-" * 70)
    print("INSTRUCTOR OPENING:")
    print("-" * 70)
    print(opening)
    print("-" * 70)
    
    # Simulate a few student interactions
    print("\n[INTERACTIVE SESSION]")
    
    interactions = [
        "I'm ready to start! Can you explain what reinforcement learning is in simple terms?",
        "That makes sense. Can you give me a real-world example?",
        "How is this different from supervised learning?",
        "What are the main components of a reinforcement learning system?"
    ]
    
    for i, student_msg in enumerate(interactions, 1):
        print(f"\n--- Interaction {i} ---")
        print(f"Student: {student_msg}")
        
        response = orchestrator.teach_interaction(student_msg)
        
        print(f"\nInstructor: {response[:300]}...")
        print()
    
    # Assessment
    print("\n[ASSESSMENT]")
    assessment = orchestrator.assess_student()
    print("Assessment Results:")
    print(assessment['assessment'][:500] + "...")
    
    # End session
    print("\n[SESSION END]")
    summary = orchestrator.end_teaching()
    print("\nSession Summary:")
    print(f"  • Topic: {summary['topic']}")
    print(f"  • Modules Covered: {len(summary['modules_covered'])}")
    print(f"  • Total Interactions: {summary['total_interactions']}")
    print(f"  • Questions Asked: {summary['questions_asked']}")
    
    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("Check the outputs/reinforcement_learning directory for saved artifacts")
    print("=" * 70)


if __name__ == "__main__":
    main()