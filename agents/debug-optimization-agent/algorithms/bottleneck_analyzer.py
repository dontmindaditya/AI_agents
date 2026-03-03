"""Analyze code for performance bottlenecks."""

import ast
from dataclasses import dataclass
from typing import List, Dict, Set
from collections import defaultdict


@dataclass
class Bottleneck:
    """Represents a performance bottleneck."""
    type: str
    severity: str  # "critical", "high", "medium", "low"
    line_number: int
    function_name: str
    description: str
    impact: str
    optimization_suggestion: str
    estimated_improvement: str


class BottleneckAnalyzer:
    """Analyze code for performance bottlenecks."""
    
    def __init__(self, code: str):
        """
        Initialize bottleneck analyzer.
        
        Args:
            code: Python code to analyze
        """
        self.code = code
        self.tree = ast.parse(code)
        self.bottlenecks: List[Bottleneck] = []
    
    def analyze(self) -> List[Bottleneck]:
        """
        Perform comprehensive bottleneck analysis.
        
        Returns:
            List of identified bottlenecks
        """
        self._detect_nested_loops()
        self._detect_list_operations_in_loops()
        self._detect_inefficient_data_structures()
        self._detect_repeated_computations()
        self._detect_unnecessary_function_calls()
        self._detect_io_in_loops()
        self._detect_algorithmic_inefficiencies()
        
        return sorted(self.bottlenecks, key=lambda b: self._severity_score(b.severity), reverse=True)
    
    def _detect_nested_loops(self):
        """Detect nested loops that might cause O(n^2) or worse complexity."""
        class LoopVisitor(ast.NodeVisitor):
            def __init__(self, analyzer):
                self.analyzer = analyzer
                self.loop_depth = 0
                self.current_function = "module"
            
            def visit_FunctionDef(self, node):
                prev_func = self.current_function
                self.current_function = node.name
                self.generic_visit(node)
                self.current_function = prev_func
            
            def visit_For(self, node):
                self.loop_depth += 1
                
                if self.loop_depth >= 2:
                    severity = "critical" if self.loop_depth >= 3 else "high"
                    impact = f"O(n^{self.loop_depth}) time complexity"
                    
                    self.analyzer.bottlenecks.append(Bottleneck(
                        type="nested_loops",
                        severity=severity,
                        line_number=node.lineno,
                        function_name=self.current_function,
                        description=f"Nested loop at depth {self.loop_depth}",
                        impact=impact,
                        optimization_suggestion="Consider using hash maps, sets, or algorithmic optimization",
                        estimated_improvement="Up to 100x for large datasets"
                    ))
                
                self.generic_visit(node)
                self.loop_depth -= 1
            
            def visit_While(self, node):
                self.loop_depth += 1
                
                if self.loop_depth >= 2:
                    severity = "critical" if self.loop_depth >= 3 else "high"
                    self.analyzer.bottlenecks.append(Bottleneck(
                        type="nested_loops",
                        severity=severity,
                        line_number=node.lineno,
                        function_name=self.current_function,
                        description=f"Nested while loop at depth {self.loop_depth}",
                        impact=f"O(n^{self.loop_depth}) time complexity",
                        optimization_suggestion="Consider algorithmic optimization or early termination",
                        estimated_improvement="Up to 100x for large datasets"
                    ))
                
                self.generic_visit(node)
                self.loop_depth -= 1
        
        visitor = LoopVisitor(self)
        visitor.visit(self.tree)
    
    def _detect_list_operations_in_loops(self):
        """Detect inefficient list operations inside loops."""
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute):
                            # Check for list.append, list.insert, list.extend
                            if child.func.attr in ['append', 'insert', 'extend']:
                                self.bottlenecks.append(Bottleneck(
                                    type="list_operation_in_loop",
                                    severity="medium",
                                    line_number=child.lineno,
                                    function_name=self._get_function_name(child),
                                    description=f"list.{child.func.attr}() called in loop",
                                    impact="Potential memory reallocation on each iteration",
                                    optimization_suggestion="Pre-allocate list or use list comprehension",
                                    estimated_improvement="10-30% performance gain"
                                ))
                            
                            # Check for string concatenation
                            elif child.func.attr in ['join', 'replace']:
                                pass  # These are actually good
    
    def _detect_inefficient_data_structures(self):
        """Detect inefficient data structure usage."""
        # Look for list membership tests
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Compare):
                for op, comparator in zip(node.ops, node.comparators):
                    if isinstance(op, (ast.In, ast.NotIn)):
                        # Check if comparing against a list literal or list variable
                        if isinstance(comparator, ast.List):
                            self.bottlenecks.append(Bottleneck(
                                type="inefficient_membership_test",
                                severity="medium",
                                line_number=node.lineno,
                                function_name=self._get_function_name(node),
                                description="Membership test on list (O(n) operation)",
                                impact="Linear time complexity for each lookup",
                                optimization_suggestion="Convert list to set for O(1) lookup",
                                estimated_improvement="Up to 1000x for large collections"
                            ))
    
    def _detect_repeated_computations(self):
        """Detect repeated expensive computations."""
        function_calls = defaultdict(list)
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                call_str = self._get_call_string(node)
                if call_str:
                    function_calls[call_str].append(node.lineno)
        
        # Find calls that appear multiple times
        for call_str, lines in function_calls.items():
            if len(lines) > 2:  # Repeated more than twice
                self.bottlenecks.append(Bottleneck(
                    type="repeated_computation",
                    severity="medium",
                    line_number=lines[0],
                    function_name=self._get_function_name_from_lines(lines[0]),
                    description=f"Repeated computation: {call_str} ({len(lines)} times)",
                    impact="Unnecessary CPU cycles",
                    optimization_suggestion="Cache result or compute once",
                    estimated_improvement="Proportional to number of repetitions"
                ))
    
    def _detect_unnecessary_function_calls(self):
        """Detect function calls that could be optimized."""
        expensive_functions = {
            'eval': ('critical', 'eval() is slow and dangerous'),
            'exec': ('critical', 'exec() is slow and dangerous'),
            'compile': ('medium', 'compile() is expensive'),
            'sorted': ('low', 'Consider if sort is necessary'),
            'list': ('low', 'Check if conversion is needed'),
        }
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in expensive_functions:
                        severity, reason = expensive_functions[func_name]
                        self.bottlenecks.append(Bottleneck(
                            type="expensive_function_call",
                            severity=severity,
                            line_number=node.lineno,
                            function_name=self._get_function_name(node),
                            description=f"Use of {func_name}(): {reason}",
                            impact="High CPU cost",
                            optimization_suggestion=self._get_alternative(func_name),
                            estimated_improvement="10-1000x depending on usage"
                        ))
    
    def _detect_io_in_loops(self):
        """Detect I/O operations inside loops."""
        io_operations = ['open', 'read', 'write', 'print', 'input']
        
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            if child.func.id in io_operations:
                                self.bottlenecks.append(Bottleneck(
                                    type="io_in_loop",
                                    severity="high",
                                    line_number=child.lineno,
                                    function_name=self._get_function_name(child),
                                    description=f"I/O operation {child.func.id}() inside loop",
                                    impact="Each I/O operation is very slow",
                                    optimization_suggestion="Batch I/O operations outside loop",
                                    estimated_improvement="10-100x performance gain"
                                ))
    
    def _detect_algorithmic_inefficiencies(self):
        """Detect common algorithmic inefficiencies."""
        # Detect bubble sort-like patterns
        for node in ast.walk(self.tree):
            if isinstance(node, ast.For):
                # Look for nested for with swap pattern
                for_bodies = [n for n in ast.walk(node) if isinstance(n, ast.For)]
                if len(for_bodies) >= 2:
                    # Check for swap operations
                    has_swap = any(
                        isinstance(n, ast.Assign) and len(n.targets) == 1
                        for n in ast.walk(node)
                    )
                    if has_swap:
                        self.bottlenecks.append(Bottleneck(
                            type="inefficient_algorithm",
                            severity="high",
                            line_number=node.lineno,
                            function_name=self._get_function_name(node),
                            description="Potential O(n²) sorting algorithm detected",
                            impact="Quadratic time complexity",
                            optimization_suggestion="Use built-in sorted() or list.sort() (O(n log n))",
                            estimated_improvement="100x for large datasets"
                        ))
    
    def _get_function_name(self, node: ast.AST) -> str:
        """Get the name of the function containing this node."""
        # Walk up the tree to find parent function
        for parent in ast.walk(self.tree):
            if isinstance(parent, ast.FunctionDef):
                if any(child is node for child in ast.walk(parent)):
                    return parent.name
        return "module"
    
    def _get_function_name_from_lines(self, line: int) -> str:
        """Get function name from line number."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    if node.lineno <= line <= node.end_lineno:
                        return node.name
        return "module"
    
    def _get_call_string(self, node: ast.Call) -> str:
        """Convert call node to string representation."""
        try:
            if isinstance(node.func, ast.Name):
                return node.func.id
            elif isinstance(node.func, ast.Attribute):
                return f"{node.func.attr}"
            return ""
        except:
            return ""
    
    def _get_alternative(self, func_name: str) -> str:
        """Get optimization alternative for function."""
        alternatives = {
            'eval': 'Use ast.literal_eval() for literals or proper parsing',
            'exec': 'Restructure code to avoid dynamic execution',
            'compile': 'Pre-compile if possible or avoid if not necessary',
            'sorted': 'Sort once and maintain order, or use bisect for insertions',
            'list': 'Use generator expressions or avoid conversion',
        }
        return alternatives.get(func_name, 'Optimize or avoid if possible')
    
    def _severity_score(self, severity: str) -> int:
        """Convert severity to numeric score for sorting."""
        scores = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        return scores.get(severity, 0)