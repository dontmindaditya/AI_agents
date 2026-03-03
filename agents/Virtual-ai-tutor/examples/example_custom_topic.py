"""
Example: Custom topic with configuration

This example shows how to:
1. Use custom LLM providers
2. Configure discussion rounds
3. Export artifacts
4. Customize the teaching flow
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator import TeachingOrchestrator
from models.llm_provider import LLMProvider


def example_with_custom_config():
    """Example with custom configuration"""
    
    print("=" * 70)
    print("EduGPT Example: Custom Topic with Configuration")
    print("=" * 70)
    
    # Custom topic
    topic = "Deep Learning for Computer Vision"
    
    print(f"\nTopic: {topic}")
    print("Configuration:")
    print("  - Discussion rounds: 3 (faster)")
    print("  - Save artifacts: Yes")
    print("  - Custom output directory")
    
    # Initialize orchestrator with custom config
    orchestrator = TeachingOrchestrator(
        topic=topic,
        max_discussion_rounds=3,  # Fewer rounds for faster execution
        save_artifacts=True,
        output_dir="./outputs/custom_topic"
    )
    
    # Run complete workflow
    print("\n[RUNNING WORKFLOW]")
    
    result = orchestrator.run_complete_workflow(
        initial_student_message="Hi! I'm excited to learn about deep learning for computer vision. Where should we start?"
    )
    
    print("\n" + "=" * 70)
    print("WORKFLOW RESULTS")
    print("=" * 70)
    print(f"✓ Discussion: {len(result['discussion_history'])} characters")
    print(f"✓ Syllabus: {len(result['syllabus'])} characters")
    print(f"✓ Artifacts saved to: {result['output_dir']}")
    
    if result['first_interaction']:
        print("\n[FIRST INTERACTION]")
        print(f"Student: {result['first_interaction']['student']}")
        print(f"Instructor: {result['first_interaction']['instructor'][:200]}...")
    
    # Continue with a few more interactions
    print("\n[CONTINUING SESSION]")
    
    questions = [
        "What's the difference between CNNs and traditional neural networks?",
        "Can you explain what convolution means in this context?"
    ]
    
    for q in questions:
        print(f"\nStudent: {q}")
        response = orchestrator.teach_interaction(q)
        print(f"Instructor: {response[:150]}...")
    
    # Get final state
    state = orchestrator.get_state()
    print("\n[ORCHESTRATOR STATE]")
    print(f"  Discussion complete: {state['discussion_complete']}")
    print(f"  Syllabus generated: {state['syllabus_generated']}")
    print(f"  Teaching active: {state['teaching_active']}")
    
    print("\n" + "=" * 70)
    print("Custom configuration example completed!")
    print("=" * 70)


def example_syllabus_only():
    """Example: Generate syllabus only, no teaching"""
    
    print("\n" + "=" * 70)
    print("EduGPT Example: Syllabus Generation Only")
    print("=" * 70)
    
    topic = "Natural Language Processing Fundamentals"
    
    print(f"\nTopic: {topic}")
    print("Mode: Syllabus generation only (no teaching session)")
    
    orchestrator = TeachingOrchestrator(
        topic=topic,
        max_discussion_rounds=4,
        save_artifacts=True,
        output_dir="./outputs/syllabus_only"
    )
    
    # Setup and generate syllabus
    orchestrator.setup()
    syllabus = orchestrator.generate_syllabus()
    
    print("\n✓ Syllabus generated successfully!")
    print(f"\nSyllabus preview (first 500 chars):")
    print("-" * 70)
    print(syllabus[:500] + "...")
    print("-" * 70)
    
    # Export artifacts
    artifacts = orchestrator.export_all_artifacts()
    
    print("\n✓ Artifacts exported:")
    for artifact_type, path in artifacts.items():
        print(f"  • {artifact_type}: {path}")
    
    print("\n" + "=" * 70)
    print("Syllabus-only example completed!")
    print("=" * 70)


def main():
    """Run all examples"""
    
    # Example 1: Custom configuration with teaching
    example_with_custom_config()
    
    print("\n\n")
    
    # Example 2: Syllabus generation only
    example_syllabus_only()
    
    print("\n\n" + "=" * 70)
    print("All examples completed successfully!")
    print("Check the outputs directory for all generated artifacts")
    print("=" * 70)


if __name__ == "__main__":
    main()