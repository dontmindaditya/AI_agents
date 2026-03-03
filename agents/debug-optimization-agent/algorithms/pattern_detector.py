"""Detect anti-patterns and code smells in Python code."""

import ast
import re
from dataclasses import dataclass
from typing import List, Dict, Set
from collections import defaultdict


@dataclass
class Pattern:
    """Detected pattern or anti-pattern."""
    name: str
    severity: str  # "critical", "high", "medium", "low"
    line_number: int
    description: str
    recommendation: str
    code_snippet: str


class PatternDetector:
    """Detect anti-patterns and suggest improvements."""
    
    # Anti-patterns to detect
    ANTI_PATTERNS = {
        "god_class": {
            "description": "Class with too many responsibilities",
            "severity": "high"
        },
        "long_parameter_list": {
            "description": "Function with too many parameters",
            "severity": "medium"
        },
        "deep_nesting": {
            "description": "Deeply nested code blocks",
            "severity": "medium"
        },
        "string_concatenation_in_loop": {
            "description": "String concatenation in loop (inefficient)",
            "severity": "high"
        },
        "mutable_default_argument": {
            "description": "Mutable default argument (dangerous)",
            "severity": "critical"
        },
        "bare_except": {
            "description": "Bare except clause (catches all exceptions)",
            "severity": "medium"
        },
        "unused_variable": {
            "description": "Variable assigned but never used",
            "severity": "low"
        },
        "duplicate_code": {
            "description": "Duplicate or similar code blocks",
            "severity": "medium"
        }
    }
    
    def __init__(self, code: str):
        """
        Initialize pattern detector.
        
        Args:
            code: Python code to analyze
        """
        self.code = code
        self.lines = code.split('\n')
        self.tree = ast.parse(code)
        self.patterns: List[Pattern] = []
    
    def detect_all(self) -> List[Pattern]:
        """
        Detect all patterns and anti-patterns.
        
        Returns:
            List of detected patterns
        """
        self._detect_god_class()
        self._detect_long_parameter_list()
        self._detect_deep_nesting()
        self._detect_string_concatenation_in_loop()
        self._detect_mutable_default_arguments()
        self._detect_bare_except()
        self._detect_unused_variables()
        self._detect_code_duplication()
        self._detect_inefficient_loops()
        self._detect_missing_type_hints()
        self._detect_magic_numbers()
        
        return sorted(self.patterns, key=lambda p: p.severity, reverse=True)
    
    def _detect_god_class(self):
        """Detect classes with too many methods/attributes."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                
                if len(methods) > 15:
                    self.patterns.append(Pattern(
                        name="god_class",
                        severity="high",
                        line_number=node.lineno,
                        description=f"Class '{node.name}' has {len(methods)} methods",
                        recommendation="Split into multiple smaller classes with single responsibilities",
                        code_snippet=self._get_code_snippet(node.lineno, 3)
                    ))
    
    def _detect_long_parameter_list(self):
        """Detect functions with too many parameters."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                param_count = len(node.args.args)
                
                if param_count > 5:
                    self.patterns.append(Pattern(
                        name="long_parameter_list",
                        severity="medium",
                        line_number=node.lineno,
                        description=f"Function '{node.name}' has {param_count} parameters",
                        recommendation="Use a configuration object or dataclass to group related parameters",
                        code_snippet=self._get_code_snippet(node.lineno, 2)
                    ))
    
    def _detect_deep_nesting(self):
        """Detect deeply nested code blocks."""
        class NestingVisitor(ast.NodeVisitor):
            def __init__(self):
                self.max_depth = 0
                self.current_depth = 0
                self.deep_locations = []
            
            def visit_If(self, node):
                self.current_depth += 1
                if self.current_depth > 3:
                    self.deep_locations.append((node.lineno, self.current_depth))
                self.max_depth = max(self.max_depth, self.current_depth)
                self.generic_visit(node)
                self.current_depth -= 1
            
            def visit_For(self, node):
                self.current_depth += 1
                if self.current_depth > 3:
                    self.deep_locations.append((node.lineno, self.current_depth))
                self.max_depth = max(self.max_depth, self.current_depth)
                self.generic_visit(node)
                self.current_depth -= 1
            
            def visit_While(self, node):
                self.current_depth += 1
                if self.current_depth > 3:
                    self.deep_locations.append((node.lineno, self.current_depth))
                self.max_depth = max(self.max_depth, self.current_depth)
                self.generic_visit(node)
                self.current_depth -= 1
        
        visitor = NestingVisitor()
        visitor.visit(self.tree)
        
        for lineno, depth in visitor.deep_locations:
            self.patterns.append(Pattern(
                name="deep_nesting",
                severity="medium",
                line_number=lineno,
                description=f"Nesting depth of {depth} detected",
                recommendation="Extract nested logic into separate functions or use early returns",
                code_snippet=self._get_code_snippet(lineno, 2)
            ))
    
    def _detect_string_concatenation_in_loop(self):
        """Detect string concatenation in loops."""
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign):
                        if isinstance(child.op, ast.Add):
                            if isinstance(child.target, ast.Name):
                                self.patterns.append(Pattern(
                                    name="string_concatenation_in_loop",
                                    severity="high",
                                    line_number=child.lineno,
                                    description="String concatenation using += in loop",
                                    recommendation="Use list.append() and ''.join() for better performance",
                                    code_snippet=self._get_code_snippet(child.lineno, 3)
                                ))
    
    def _detect_mutable_default_arguments(self):
        """Detect mutable default arguments in functions."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        self.patterns.append(Pattern(
                            name="mutable_default_argument",
                            severity="critical",
                            line_number=node.lineno,
                            description=f"Function '{node.name}' uses mutable default argument",
                            recommendation="Use None as default and initialize inside function",
                            code_snippet=self._get_code_snippet(node.lineno, 2)
                        ))
    
    def _detect_bare_except(self):
        """Detect bare except clauses."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    self.patterns.append(Pattern(
                        name="bare_except",
                        severity="medium",
                        line_number=node.lineno,
                        description="Bare except clause catches all exceptions",
                        recommendation="Catch specific exception types instead",
                        code_snippet=self._get_code_snippet(node.lineno, 3)
                    ))
    
    def _detect_unused_variables(self):
        """Detect variables that are assigned but never used."""
        assigned_vars = set()
        used_vars = set()
        var_lines = {}
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assigned_vars.add(target.id)
                        var_lines[target.id] = node.lineno
            
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Load):
                    used_vars.add(node.id)
        
        unused = assigned_vars - used_vars
        for var in unused:
            if not var.startswith('_'):  # Skip private variables
                self.patterns.append(Pattern(
                    name="unused_variable",
                    severity="low",
                    line_number=var_lines.get(var, 0),
                    description=f"Variable '{var}' is assigned but never used",
                    recommendation="Remove unused variable or prefix with _ if intentionally unused",
                    code_snippet=self._get_code_snippet(var_lines.get(var, 0), 1)
                ))
    
    def _detect_code_duplication(self):
        """Detect duplicate code blocks (simplified)."""
        # Simple hash-based duplicate detection
        code_hashes = defaultdict(list)
        
        for i, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if len(stripped) > 20 and not stripped.startswith('#'):
                code_hashes[stripped].append(i)
        
        for code, lines in code_hashes.items():
            if len(lines) > 1:
                self.patterns.append(Pattern(
                    name="duplicate_code",
                    severity="medium",
                    line_number=lines[0],
                    description=f"Duplicate code found on lines: {', '.join(map(str, lines))}",
                    recommendation="Extract duplicate code into a reusable function",
                    code_snippet=code[:100]
                ))
    
    def _detect_inefficient_loops(self):
        """Detect inefficient loop patterns."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.For):
                # Check for range(len(list)) pattern
                if isinstance(node.iter, ast.Call):
                    if isinstance(node.iter.func, ast.Name):
                        if node.iter.func.id == 'range':
                            if len(node.iter.args) > 0:
                                arg = node.iter.args[0]
                                if isinstance(arg, ast.Call):
                                    if isinstance(arg.func, ast.Name):
                                        if arg.func.id == 'len':
                                            self.patterns.append(Pattern(
                                                name="inefficient_loop",
                                                severity="low",
                                                line_number=node.lineno,
                                                description="Using range(len(list)) instead of iterating directly",
                                                recommendation="Use 'for item in list' or 'for i, item in enumerate(list)'",
                                                code_snippet=self._get_code_snippet(node.lineno, 2)
                                            ))
    
    def _detect_missing_type_hints(self):
        """Detect functions without type hints."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                has_hints = any(arg.annotation for arg in node.args.args)
                has_return = node.returns is not None
                
                if not has_hints and not has_return:
                    self.patterns.append(Pattern(
                        name="missing_type_hints",
                        severity="low",
                        line_number=node.lineno,
                        description=f"Function '{node.name}' lacks type hints",
                        recommendation="Add type hints to improve code clarity and catch errors early",
                        code_snippet=self._get_code_snippet(node.lineno, 1)
                    ))
    
    def _detect_magic_numbers(self):
        """Detect magic numbers in code."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    # Skip common values
                    if node.value not in [0, 1, -1, 2, 10, 100]:
                        self.patterns.append(Pattern(
                            name="magic_number",
                            severity="low",
                            line_number=node.lineno,
                            description=f"Magic number {node.value} found",
                            recommendation="Extract to a named constant with descriptive name",
                            code_snippet=self._get_code_snippet(node.lineno, 1)
                        ))
    
    def _get_code_snippet(self, line_number: int, context: int = 2) -> str:
        """
        Get code snippet around line number.
        
        Args:
            line_number: Central line number
            context: Number of lines before/after to include
            
        Returns:
            Code snippet
        """
        start = max(0, line_number - context - 1)
        end = min(len(self.lines), line_number + context)
        
        return '\n'.join(self.lines[start:end])