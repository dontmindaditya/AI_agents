"""Code parsing and manipulation utilities."""

import ast
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

import astor


@dataclass
class FunctionInfo:
    """Information about a function."""
    name: str
    line_number: int
    args: List[str]
    returns: Optional[str]
    docstring: Optional[str]
    complexity: int
    lines_of_code: int


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    line_number: int
    methods: List[str]
    base_classes: List[str]
    docstring: Optional[str]


@dataclass
class ImportInfo:
    """Information about imports."""
    module: str
    names: List[str]
    line_number: int
    is_from_import: bool


class CodeParser:
    """Parse and analyze Python code using AST."""
    
    def __init__(self, code: str):
        """
        Initialize code parser.
        
        Args:
            code: Python code to parse
        """
        self.code = code
        self.tree: Optional[ast.AST] = None
        self.parse_tree()
    
    def parse_tree(self) -> bool:
        """
        Parse code into AST.
        
        Returns:
            True if parsing successful, False otherwise
        """
        try:
            self.tree = ast.parse(self.code)
            return True
        except SyntaxError as e:
            print(f"Syntax error in code: {e}")
            return False
    
    def get_functions(self) -> List[FunctionInfo]:
        """
        Extract all function definitions.
        
        Returns:
            List of function information
        """
        if not self.tree:
            return []
        
        functions = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                func_info = FunctionInfo(
                    name=node.name,
                    line_number=node.lineno,
                    args=[arg.arg for arg in node.args.args],
                    returns=self._get_return_annotation(node),
                    docstring=ast.get_docstring(node),
                    complexity=self._calculate_complexity(node),
                    lines_of_code=self._count_lines(node)
                )
                functions.append(func_info)
        
        return functions
    
    def get_classes(self) -> List[ClassInfo]:
        """
        Extract all class definitions.
        
        Returns:
            List of class information
        """
        if not self.tree:
            return []
        
        classes = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                methods = [
                    n.name for n in node.body
                    if isinstance(n, ast.FunctionDef)
                ]
                
                base_classes = [
                    self._get_node_name(base)
                    for base in node.bases
                ]
                
                class_info = ClassInfo(
                    name=node.name,
                    line_number=node.lineno,
                    methods=methods,
                    base_classes=base_classes,
                    docstring=ast.get_docstring(node)
                )
                classes.append(class_info)
        
        return classes
    
    def get_imports(self) -> List[ImportInfo]:
        """
        Extract all import statements.
        
        Returns:
            List of import information
        """
        if not self.tree:
            return []
        
        imports = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_info = ImportInfo(
                        module=alias.name,
                        names=[alias.asname or alias.name],
                        line_number=node.lineno,
                        is_from_import=False
                    )
                    imports.append(import_info)
            
            elif isinstance(node, ast.ImportFrom):
                names = [alias.name for alias in node.names]
                import_info = ImportInfo(
                    module=node.module or "",
                    names=names,
                    line_number=node.lineno,
                    is_from_import=True
                )
                imports.append(import_info)
        
        return imports
    
    def get_variables(self) -> Dict[str, List[int]]:
        """
        Extract variable assignments and their line numbers.
        
        Returns:
            Dictionary mapping variable names to line numbers
        """
        if not self.tree:
            return {}
        
        variables: Dict[str, List[int]] = {}
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id not in variables:
                            variables[target.id] = []
                        variables[target.id].append(node.lineno)
        
        return variables
    
    def find_unused_imports(self) -> List[str]:
        """
        Find potentially unused imports.
        
        Returns:
            List of unused import names
        """
        if not self.tree:
            return []
        
        imports = self.get_imports()
        used_names = self._get_used_names()
        
        unused = []
        for import_info in imports:
            for name in import_info.names:
                base_name = name.split('.')[0]
                if base_name not in used_names:
                    unused.append(name)
        
        return unused
    
    def find_long_functions(self, threshold: int = 50) -> List[Tuple[str, int]]:
        """
        Find functions longer than threshold.
        
        Args:
            threshold: Maximum lines of code
            
        Returns:
            List of (function_name, lines_of_code) tuples
        """
        functions = self.get_functions()
        return [
            (func.name, func.lines_of_code)
            for func in functions
            if func.lines_of_code > threshold
        ]
    
    def get_code_structure(self) -> Dict:
        """
        Get overall code structure.
        
        Returns:
            Dictionary with code structure information
        """
        return {
            "functions": len(self.get_functions()),
            "classes": len(self.get_classes()),
            "imports": len(self.get_imports()),
            "lines_of_code": len(self.code.splitlines()),
            "blank_lines": len([line for line in self.code.splitlines() if not line.strip()]),
            "comment_lines": len([line for line in self.code.splitlines() if line.strip().startswith('#')])
        }
    
    def format_code(self) -> str:
        """
        Format code using astor.
        
        Returns:
            Formatted code
        """
        if not self.tree:
            return self.code
        
        try:
            return astor.to_source(self.tree)
        except Exception as e:
            print(f"Error formatting code: {e}")
            return self.code
    
    def _get_return_annotation(self, node: ast.FunctionDef) -> Optional[str]:
        """Get return type annotation."""
        if node.returns:
            try:
                return astor.to_source(node.returns).strip()
            except:
                return None
        return None
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _count_lines(self, node: ast.AST) -> int:
        """Count lines of code in node."""
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            return node.end_lineno - node.lineno + 1
        return 0
    
    def _get_node_name(self, node: ast.AST) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_node_name(node.value)}.{node.attr}"
        return ""
    
    def _get_used_names(self) -> Set[str]:
        """Get all names used in code."""
        if not self.tree:
            return set()
        
        used_names = set()
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # Get the base name
                while isinstance(node, ast.Attribute):
                    node = node.value
                if isinstance(node, ast.Name):
                    used_names.add(node.id)
        
        return used_names