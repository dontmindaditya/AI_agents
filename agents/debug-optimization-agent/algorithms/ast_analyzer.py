"""AST-based code analysis for detecting issues and patterns."""

import ast
from dataclasses import dataclass
from typing import Dict, List, Set, Any
from collections import defaultdict


@dataclass
class CodeIssue:
    """Represents a code issue found during analysis."""
    severity: str  # "critical", "high", "medium", "low"
    category: str
    message: str
    line_number: int
    suggestion: str


class ASTAnalyzer(ast.NodeVisitor):
    """Advanced AST analyzer for code quality and optimization opportunities."""
    
    def __init__(self, code: str):
        """
        Initialize AST analyzer.
        
        Args:
            code: Python code to analyze
        """
        self.code = code
        self.tree = ast.parse(code)
        self.issues: List[CodeIssue] = []
        self.metrics: Dict[str, Any] = {}
        
        # Analysis state
        self.current_function = None
        self.loop_depth = 0
        self.function_calls: Dict[str, int] = defaultdict(int)
        self.variable_assignments: Dict[str, List[int]] = defaultdict(list)
        self.imports: Set[str] = set()
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform complete AST analysis.
        
        Returns:
            Analysis results with issues and metrics
        """
        self.visit(self.tree)
        
        # Additional analyses
        self._detect_code_smells()
        self._analyze_complexity()
        self._check_best_practices()
        
        return {
            "issues": sorted(self.issues, key=lambda x: x.severity, reverse=True),
            "metrics": self.metrics,
            "function_calls": dict(self.function_calls),
            "imports": list(self.imports)
        }
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definition."""
        prev_function = self.current_function
        self.current_function = node.name
        
        # Check function length
        func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
        if func_lines > 50:
            self.issues.append(CodeIssue(
                severity="medium",
                category="maintainability",
                message=f"Function '{node.name}' is too long ({func_lines} lines)",
                line_number=node.lineno,
                suggestion="Consider breaking down into smaller functions"
            ))
        
        # Check parameter count
        if len(node.args.args) > 5:
            self.issues.append(CodeIssue(
                severity="medium",
                category="design",
                message=f"Function '{node.name}' has too many parameters ({len(node.args.args)})",
                line_number=node.lineno,
                suggestion="Consider using a configuration object or reducing parameters"
            ))
        
        # Check if function has docstring
        if not ast.get_docstring(node):
            self.issues.append(CodeIssue(
                severity="low",
                category="documentation",
                message=f"Function '{node.name}' lacks docstring",
                line_number=node.lineno,
                suggestion="Add docstring to explain function purpose and parameters"
            ))
        
        self.generic_visit(node)
        self.current_function = prev_function
    
    def visit_For(self, node: ast.For):
        """Visit for loop."""
        self.loop_depth += 1
        
        # Detect nested loops (potential O(n^2) or worse)
        if self.loop_depth > 2:
            self.issues.append(CodeIssue(
                severity="high",
                category="performance",
                message=f"Deeply nested loops detected (depth: {self.loop_depth})",
                line_number=node.lineno,
                suggestion="Consider algorithmic optimization or using vectorized operations"
            ))
        
        # Check for list modifications in loop
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr in ['append', 'extend', 'insert']:
                        self.issues.append(CodeIssue(
                            severity="medium",
                            category="performance",
                            message="List modification inside loop detected",
                            line_number=node.lineno,
                            suggestion="Consider list comprehension or pre-allocating list"
                        ))
        
        self.generic_visit(node)
        self.loop_depth -= 1
    
    def visit_While(self, node: ast.While):
        """Visit while loop."""
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1
    
    def visit_Call(self, node: ast.Call):
        """Visit function call."""
        func_name = self._get_call_name(node)
        if func_name:
            self.function_calls[func_name] += 1
            
            # Detect expensive operations
            if func_name in ['eval', 'exec']:
                self.issues.append(CodeIssue(
                    severity="critical",
                    category="security",
                    message=f"Dangerous function '{func_name}' detected",
                    line_number=node.lineno,
                    suggestion="Avoid using eval/exec - use safer alternatives"
                ))
            
            # Detect inefficient operations
            if func_name == 'list' and isinstance(node.args[0], ast.Call):
                arg_func = self._get_call_name(node.args[0])
                if arg_func == 'map':
                    self.issues.append(CodeIssue(
                        severity="low",
                        category="performance",
                        message="list(map(...)) can be replaced with list comprehension",
                        line_number=node.lineno,
                        suggestion="Use [x for x in ...] instead for better readability"
                    ))
        
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import):
        """Visit import statement."""
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Visit from-import statement."""
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign):
        """Visit assignment."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variable_assignments[target.id].append(node.lineno)
        
        self.generic_visit(node)
    
    def visit_Try(self, node: ast.Try):
        """Visit try-except block."""
        # Check for bare except
        for handler in node.handlers:
            if handler.type is None:
                self.issues.append(CodeIssue(
                    severity="medium",
                    category="error_handling",
                    message="Bare except clause detected",
                    line_number=handler.lineno,
                    suggestion="Catch specific exceptions instead of bare except"
                ))
        
        # Check for empty except blocks
        for handler in node.handlers:
            if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                self.issues.append(CodeIssue(
                    severity="high",
                    category="error_handling",
                    message="Empty except block (silently catching errors)",
                    line_number=handler.lineno,
                    suggestion="Handle the exception properly or at least log it"
                ))
        
        self.generic_visit(node)
    
    def visit_Compare(self, node: ast.Compare):
        """Visit comparison."""
        # Check for identity comparison with literals
        for op, comparator in zip(node.ops, node.comparators):
            if isinstance(op, (ast.Is, ast.IsNot)):
                if isinstance(comparator, (ast.Constant, ast.Num, ast.Str)):
                    self.issues.append(CodeIssue(
                        severity="medium",
                        category="correctness",
                        message="Identity comparison with literal detected",
                        line_number=node.lineno,
                        suggestion="Use == or != for value comparison, not 'is'"
                    ))
        
        self.generic_visit(node)
    
    def _detect_code_smells(self):
        """Detect various code smells."""
        # Detect variables assigned but never used
        # This is a simplified version
        pass
    
    def _analyze_complexity(self):
        """Calculate various complexity metrics."""
        self.metrics['total_functions'] = len([
            node for node in ast.walk(self.tree)
            if isinstance(node, ast.FunctionDef)
        ])
        
        self.metrics['total_classes'] = len([
            node for node in ast.walk(self.tree)
            if isinstance(node, ast.ClassDef)
        ])
        
        self.metrics['max_loop_depth'] = self.loop_depth
    
    def _check_best_practices(self):
        """Check for Python best practices violations."""
        # Check for global variables
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Global):
                self.issues.append(CodeIssue(
                    severity="medium",
                    category="design",
                    message="Global variable usage detected",
                    line_number=node.lineno,
                    suggestion="Minimize global state - use parameters and return values"
                ))
    
    def _get_call_name(self, node: ast.Call) -> str:
        """Extract function name from call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return ""