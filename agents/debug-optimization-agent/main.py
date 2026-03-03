"""Main entry point for Debug Optimization Agent."""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from graph.debug_graph import DebugOptimizationGraph
from utils.logger import setup_logger
from config.settings import get_settings

# Setup logger
logger = setup_logger()


def analyze_file(filepath: str, run_profiling: bool = True, output_file: Optional[str] = None):
    """
    Analyze a Python file.
    
    Args:
        filepath: Path to Python file
        run_profiling: Whether to run actual profiling
        output_file: Optional output file for results
    """
    logger.info(f"Analyzing file: {filepath}")
    
    # Read code
    try:
        code = Path(filepath).read_text()
    except Exception as e:
        logger.error(f"Failed to read file: {str(e)}")
        return
    
    # Run analysis
    graph = DebugOptimizationGraph()
    results = graph.run(code, run_profiling=run_profiling)
    
    # Display results
    print_results(results)
    
    # Save to file if requested
    if output_file:
        save_results(results, output_file)


def analyze_code(code: str, run_profiling: bool = True):
    """
    Analyze code string directly.
    
    Args:
        code: Python code to analyze
        run_profiling: Whether to run actual profiling
        
    Returns:
        Analysis results
    """
    logger.info("Analyzing code")
    
    graph = DebugOptimizationGraph()
    results = graph.run(code, run_profiling=run_profiling)
    
    return results


def print_results(results: dict):
    """Print analysis results in a readable format."""
    print("\n" + "="*80)
    print("DEBUG OPTIMIZATION AGENT - ANALYSIS RESULTS")
    print("="*80 + "\n")
    
    # Summary
    summary = results.get("summary", {})
    print("📊 SUMMARY")
    print("-" * 80)
    print(f"Total Issues: {summary.get('total_issues', 0)}")
    print(f"Performance Bottlenecks: {summary.get('total_bottlenecks', 0)}")
    print(f"Memory Issues: {summary.get('total_memory_issues', 0)}")
    print(f"Optimization Opportunities: {summary.get('total_optimizations', 0)}")
    print(f"Quick Wins Available: {summary.get('quick_wins', 0)}")
    print()
    
    # Code Quality
    code_quality = results.get("code_quality", {})
    print("📈 CODE QUALITY")
    print("-" * 80)
    print(f"Maintainability Index: {code_quality.get('maintainability_index', 0):.2f}/100")
    print(f"Average Complexity: {code_quality.get('average_complexity', 0):.2f}")
    
    severity = code_quality.get("severity_breakdown", {})
    if severity:
        print(f"Critical Issues: {severity.get('critical', 0)}")
        print(f"High Priority: {severity.get('high', 0)}")
        print(f"Medium Priority: {severity.get('medium', 0)}")
        print(f"Low Priority: {severity.get('low', 0)}")
    print()
    
    # Top Recommendations
    recommendations = results.get("recommendations", [])
    if recommendations:
        print("💡 TOP RECOMMENDATIONS")
        print("-" * 80)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        print()
    
    # Quick Wins
    quick_wins = results.get("optimizations", {}).get("quick_wins", [])
    if quick_wins:
        print("✨ QUICK WINS (High Impact, Low Effort)")
        print("-" * 80)
        for i, win in enumerate(quick_wins[:5], 1):
            print(f"{i}. {win.get('title', 'N/A')}")
            print(f"   Impact: {win.get('impact', 'N/A')} | Effort: {win.get('effort', 'N/A')}")
            print(f"   Line: {win.get('line_number', 'N/A')}")
            print(f"   Improvement: {win.get('estimated_improvement', 'N/A')}")
            print()
    
    # Errors
    errors = results.get("errors", [])
    if errors:
        print("⚠️  ERRORS")
        print("-" * 80)
        for error in errors:
            print(f"• {error}")
        print()
    
    print("="*80 + "\n")


def save_results(results: dict, output_file: str):
    """Save results to JSON file."""
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results saved to: {output_file}")
        print(f"✅ Results saved to: {output_file}")
    except Exception as e:
        logger.error(f"Failed to save results: {str(e)}")
        print(f"❌ Failed to save results: {str(e)}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Debug Optimization Agent - AI-powered code analysis and optimization"
    )
    
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Path to Python file to analyze"
    )
    
    parser.add_argument(
        "--code", "-c",
        type=str,
        help="Python code string to analyze"
    )
    
    parser.add_argument(
        "--no-profiling",
        action="store_true",
        help="Disable runtime profiling (only static analysis)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for results (JSON)"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="Debug Optimization Agent 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.file and not args.code:
        parser.print_help()
        print("\n❌ Error: Either --file or --code must be provided")
        sys.exit(1)
    
    run_profiling = not args.no_profiling
    
    # Run analysis
    if args.file:
        analyze_file(args.file, run_profiling, args.output)
    elif args.code:
        results = analyze_code(args.code, run_profiling)
        print_results(results)
        if args.output:
            save_results(results, args.output)


if __name__ == "__main__":
    main()