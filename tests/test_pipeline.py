import sys
from pathlib import Path
import asyncio

# Add backend to sys path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from pipeline.dynamic import DynamicPipeline, PipelineConfig, PipelineStep
from agents.registry import agent_registry

async def test_pipeline():
    print("🧪 Testing Dynamic Pipeline...")
    
    # Ensure text_processor is available
    if not agent_registry.get_agent_class('text_processor'):
        print("❌ text_processor agent not found.")
        return

    # Define Pipeline
    # Step 1: Uppercase "hello world" -> stored in "step1"
    # Step 2: Count words of "hello world" (just to show chaining works, even if inputs are static for now)
    
    config = PipelineConfig(
        name="Test Pipeline",
        initial_context={"user": "tester"},
        steps=[
            PipelineStep(
                agent_id="text_processor",
                inputs={"text": "hello world", "operation": "uppercase"},
                output_key="step1_result"
            ),
            PipelineStep(
                agent_id="text_processor",
                inputs={"text": "programming is fun", "operation": "count_words"},
                output_key="step2_result"
            )
        ]
    )
    
    pipeline = DynamicPipeline()
    try:
        result = await pipeline.run(config)
        print("\n✅ Pipeline Result:")
        print(f"Context keys: {result['context'].keys()}")
        print(f"Step 1 Result: {result['context'].get('step1_result')}")
        print(f"Step 2 Result: {result['context'].get('step2_result')}")
        
        ctx = result['context']
        if ctx['step1_result']['result'] == 'HELLO WORLD' and ctx['step2_result']['result'] == '3':
            print("✅ VERIFICATION SUCCESS")
        else:
            print("❌ VERIFICATION FAILED")
            
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
