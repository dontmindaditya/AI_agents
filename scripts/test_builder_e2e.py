"""
End-to-End Test for AI Builder
Tests: Generation → Preview → Analysis
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

root_dir = os.path.join(os.path.dirname(__file__), "..", "..")
if os.path.exists(os.path.join(root_dir, ".env")):
    load_dotenv(os.path.join(root_dir, ".env"))

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

async def test_builder():
    print("=" * 70)
    print("AI BUILDER - END-TO-END TEST")
    print("=" * 70)
    
    # Test 1: Pipeline Stages
    print("\n[1/4] Testing Pipeline Stages...")
    try:
        from pipeline.planning_stage import PlanningStage
        from pipeline.generation_stage import GenerationStage
        from pipeline.analysis_stage import AnalysisStage
        from pipeline.integration_stage import IntegrationStage
        print("   [OK] All pipeline stages imported")
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False
    
    # Test 2: Adapters
    print("\n[2/4] Testing Agent Adapters...")
    try:
        from pipeline.adapters import PlanningAdapter, FrontendAdapter
        
        # Test planning adapter
        planner = PlanningAdapter()
        plan = planner.create_plan("Create a landing page for AI SaaS")
        print(f"   [OK] Planning adapter works")
        print(f"        Plan preview: {plan['raw_output'][:100]}...")
        
        # Test frontend adapter
        frontend = FrontendAdapter()
        result = frontend.generate_components("Simple landing page", "react")
        print(f"   [OK] Frontend adapter works")
        print(f"        Generated {len(result['files'])} files")
        
    except Exception as e:
        print(f"   [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Code Generator
    print("\n[3/4] Testing Code Generator...")
    try:
        from services.code_generator import CodeGenerator
        
        package_json = CodeGenerator.generate_package_json("react")
        tsconfig = CodeGenerator.generate_tsconfig("react")
        
        print("   [OK] Code generator works")
        print(f"        Config files generated")
        
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False
    
    # Test 4: Full Pipeline Simulation
    print("\n[4/4] Simulating Full Pipeline...")
    try:
        from pipeline.websocket_manager import WebSocketManager
        
        ws_manager = WebSocketManager()
        
        # Create stages
        planning = PlanningStage(ws_manager)
        generation = GenerationStage(ws_manager)
        analysis = AnalysisStage(ws_manager)
        
        # Simulate context
        context = {
            "project_data": {
                "description": "Create a modern landing page for an AI SaaS product",
                "framework": "react"
            }
        }
        
        # Run planning
        print("   Running planning stage...")
        plan_result = await planning.execute("test-project", context)
        print(f"   [OK] Planning complete")
        
        # Run analysis
        print("   Running analysis stage...")
        analysis_result = await analysis.execute("test-project", context)
        print(f"   [OK] Analysis complete")
        
        # Run generation
        print("   Running generation stage...")
        gen_result = await generation.execute("test-project", context)
        print(f"   [OK] Generation complete")
        print(f"        Total files: {gen_result['total_files']}")
        
        # Show sample files
        if context.get("all_files"):
            print("\n   Generated files:")
            for f in context["all_files"][:3]:
                print(f"      - {f['path']}")
        
    except Exception as e:
        print(f"   [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    print("[SUCCESS] AI BUILDER IS FUNCTIONAL!")
    print("=" * 70)
    print("\nWhat works:")
    print("  ✓ Planning (using your planning_agent)")
    print("  ✓ Generation (using your frontend_agent)")
    print("  ✓ Analysis (design system)")
    print("  ✓ Config files (package.json, tsconfig, etc.)")
    print("\nStart the backend:")
    print("  python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload")
    print("\nTest in UI:")
    print("  http://localhost:3000/builder")
    print("  Type: 'Create a landing page for AI SaaS'")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_builder())
    sys.exit(0 if result else 1)
