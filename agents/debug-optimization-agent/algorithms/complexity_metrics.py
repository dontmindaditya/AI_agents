"""Complexity metrics calculation using radon and custom algorithms."""

import ast
from dataclasses import dataclass
from typing import Dict, List
from radon.complexity import cc_visit, average_complexity
from radon.metrics import mi_visit, h_visit
from radon.raw import analyze


@dataclass
class FunctionComplexity:
    """Complexity metrics for a function."""
    name: str
    lineno: int
    complexity: int
    rank: str  # A, B, C, D, E, F
    cognitive_complexity: int


@dataclass
class ModuleMetrics:
    """Module-level metrics."""
    loc: int  # Lines of code
    lloc: int  # Logical lines of code
    sloc: int  # Source lines of code
    comments: int
    multi: int  # Multi-line strings
    blank: int
    single_comments: int


class ComplexityAnalyzer:
    """Analyze code complexity using multiple metrics."""
    
    def __init__(self, code: str):
        """
        Initialize complexity analyzer.
        
        Args:
            code: Python code to analyze
        """
        self.code = code
        self.tree = ast.parse(code)
    
    def analyze_all(self) -> Dict:
        """
        Perform complete complexity analysis.
        
        Returns:
            Dictionary with all complexity metrics
        """
        return {
            "cyclomatic": self.get_cyclomatic_complexity(),
            "cognitive": self.get_cognitive_complexity(),
            "maintainability_index": self.get_maintainability_index(),
            "halstead": self.get_halstead_metrics(),
            "raw_metrics": self.get_raw_metrics(),
            "function_complexities": self.get_function_complexities()
        }
    
    def get_cyclomatic_complexity(self) -> Dict:
        """
        Calculate cyclomatic complexity for all functions.
        
        Returns:
            Dictionary with complexity scores
        """
        try:
            results = cc_visit(self.code)
            avg = average_complexity(results) if results else 0
            
            return {
                "average": round(avg, 2),
                "max": max([r.complexity for r in results], default=0),
                "functions": [
                    {
                        "name": r.name,
                        "complexity": r.complexity,
                        "rank": r.rank,
                        "lineno": r.lineno
                    }
                    for r in results
                ]
            }
        except Exception as e:
            return {"error": str(e), "average": 0, "max": 0, "functions": []}
    
    def get_cognitive_complexity(self) -> Dict:
        """
        Calculate cognitive complexity (how hard code is to understand).
        
        Returns:
            Dictionary with cognitive complexity scores
        """
        functions = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_cognitive_complexity(node)
                functions.append({
                    "name": node.name,
                    "cognitive_complexity": complexity,
                    "lineno": node.lineno
                })
        
        avg = sum(f["cognitive_complexity"] for f in functions) / len(functions) if functions else 0
        
        return {
            "average": round(avg, 2),
            "max": max([f["cognitive_complexity"] for f in functions], default=0),
            "functions": functions
        }
    
    def get_maintainability_index(self) -> float:
        """
        Calculate maintainability index (0-100 scale).
        
        Returns:
            Maintainability index score
        """
        try:
            mi = mi_visit(self.code, multi=True)
            # mi_visit returns average MI for all blocks
            return round(mi, 2)
        except Exception as e:
            print(f"Error calculating MI: {e}")
            return 0.0
    
    def get_halstead_metrics(self) -> Dict:
        """
        Calculate Halstead complexity metrics.
        
        Returns:
            Dictionary with Halstead metrics
        """
        try:
            halstead = h_visit(self.code)
            
            return {
                "h1": halstead.total.h1,  # Unique operators
                "h2": halstead.total.h2,  # Unique operands
                "N1": halstead.total.N1,  # Total operators
                "N2": halstead.total.N2,  # Total operands
                "vocabulary": halstead.total.vocabulary,
                "length": halstead.total.length,
                "calculated_length": round(halstead.total.calculated_length, 2),
                "volume": round(halstead.total.volume, 2),
                "difficulty": round(halstead.total.difficulty, 2),
                "effort": round(halstead.total.effort, 2),
                "time": round(halstead.total.time, 2),
                "bugs": round(halstead.total.bugs, 4)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_raw_metrics(self) -> ModuleMetrics:
        """
        Get raw code metrics (LOC, comments, etc.).
        
        Returns:
            Module metrics
        """
        try:
            analysis = analyze(self.code)
            
            return ModuleMetrics(
                loc=analysis.loc,
                lloc=analysis.lloc,
                sloc=analysis.sloc,
                comments=analysis.comments,
                multi=analysis.multi,
                blank=analysis.blank,
                single_comments=analysis.single_comments
            )
        except Exception as e:
            print(f"Error analyzing raw metrics: {e}")
            return ModuleMetrics(0, 0, 0, 0, 0, 0, 0)
    
    def get_function_complexities(self) -> List[FunctionComplexity]:
        """
        Get combined complexity metrics for all functions.
        
        Returns:
            List of function complexity metrics
        """
        cyclomatic = self.get_cyclomatic_complexity()
        cognitive = self.get_cognitive_complexity()
        
        # Merge metrics
        functions = []
        cyc_dict = {f["name"]: f for f in cyclomatic.get("functions", [])}
        cog_dict = {f["name"]: f for f in cognitive.get("functions", [])}
        
        all_names = set(cyc_dict.keys()) | set(cog_dict.keys())
        
        for name in all_names:
            cyc = cyc_dict.get(name, {})
            cog = cog_dict.get(name, {})
            
            functions.append(FunctionComplexity(
                name=name,
                lineno=cyc.get("lineno", cog.get("lineno", 0)),
                complexity=cyc.get("complexity", 0),
                rank=cyc.get("rank", "U"),
                cognitive_complexity=cog.get("cognitive_complexity", 0)
            ))
        
        return functions
    
    def _calculate_cognitive_complexity(self, node: ast.FunctionDef) -> int:
        """
        Calculate cognitive complexity for a function.
        
        Cognitive complexity measures how difficult code is to understand.
        It penalizes nested structures more heavily than cyclomatic complexity.
        
        Args:
            node: Function AST node
            
        Returns:
            Cognitive complexity score
        """
        complexity = 0
        nesting_level = 0
        
        for child in ast.walk(node):
            # Increment for control flow breaks
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1 + nesting_level
            
            # Binary logical operators add to complexity
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            
            # Exception handlers
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1 + nesting_level
            
            # Recursion adds complexity
            elif isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id == node.name:
                        complexity += 1
        
        return complexity
    
    def get_complexity_rank(self, complexity: int) -> str:
        """
        Convert complexity score to rank (A-F).
        
        Args:
            complexity: Complexity score
            
        Returns:
            Rank letter
        """
        if complexity <= 5:
            return "A"
        elif complexity <= 10:
            return "B"
        elif complexity <= 20:
            return "C"
        elif complexity <= 30:
            return "D"
        elif complexity <= 40:
            return "E"
        else:
            return "F"
    
    def identify_complex_functions(self, threshold: int = 10) -> List[str]:
        """
        Identify functions exceeding complexity threshold.
        
        Args:
            threshold: Maximum acceptable complexity
            
        Returns:
            List of complex function names
        """
        cyclomatic = self.get_cyclomatic_complexity()
        
        return [
            f["name"]
            for f in cyclomatic.get("functions", [])
            if f["complexity"] > threshold
        ]