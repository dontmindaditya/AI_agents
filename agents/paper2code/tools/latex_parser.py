"""
LaTeX and mathematical formula parser
"""
import re
from typing import List, Dict, Optional, Tuple
import sympy
from sympy.parsing.latex import parse_latex
from utils.logger import logger


class LatexParser:
    """Parse and process LaTeX mathematical formulas"""
    
    def __init__(self):
        """Initialize LaTeX parser"""
        self.equations = []
        
    def extract_latex_equations(self, text: str) -> List[Dict[str, str]]:
        """
        Extract LaTeX equations from text
        
        Args:
            text: Text containing LaTeX equations
            
        Returns:
            List of dictionaries with equation info
        """
        equations = []
        
        # Patterns for different LaTeX equation formats
        patterns = [
            (r'\$\$(.*?)\$\$', 'display'),  # Display equations
            (r'\$(.*?)\$', 'inline'),        # Inline equations
            (r'\\begin\{equation\}(.*?)\\end\{equation\}', 'equation'),
            (r'\\begin\{align\}(.*?)\\end\{align\}', 'align'),
            (r'\\begin\{align\*\}(.*?)\\end\{align\*\}', 'align*'),
            (r'\\begin\{eqnarray\}(.*?)\\end\{eqnarray\}', 'eqnarray'),
            (r'\\[(.*?)\\]', 'bracket_display'),
        ]
        
        for pattern, eq_type in patterns:
            matches = re.finditer(pattern, text, re.DOTALL)
            for match in matches:
                latex_str = match.group(1).strip()
                if latex_str:
                    equations.append({
                        'latex': latex_str,
                        'type': eq_type,
                        'position': match.start(),
                        'raw': match.group(0)
                    })
        
        # Sort by position in text
        equations.sort(key=lambda x: x['position'])
        
        self.equations = equations
        return equations
    
    def parse_to_sympy(self, latex_str: str) -> Optional[sympy.Expr]:
        """
        Parse LaTeX string to SymPy expression
        
        Args:
            latex_str: LaTeX equation string
            
        Returns:
            SymPy expression or None if parsing fails
        """
        try:
            # Clean up LaTeX string
            latex_str = self._clean_latex(latex_str)
            
            # Parse to SymPy
            expr = parse_latex(latex_str)
            return expr
        
        except Exception as e:
            logger.warning(f"Could not parse LaTeX '{latex_str[:50]}...': {str(e)}")
            return None
    
    def _clean_latex(self, latex_str: str) -> str:
        """Clean and normalize LaTeX string"""
        # Remove labels and refs
        latex_str = re.sub(r'\\label\{.*?\}', '', latex_str)
        latex_str = re.sub(r'\\ref\{.*?\}', '', latex_str)
        
        # Remove alignment characters
        latex_str = latex_str.replace('&', '')
        latex_str = latex_str.replace('\\\\', '')
        
        # Remove text mode
        latex_str = re.sub(r'\\text\{(.*?)\}', r'\1', latex_str)
        
        return latex_str.strip()
    
    def extract_variables(self, latex_str: str) -> List[str]:
        """
        Extract variable names from LaTeX equation
        
        Args:
            latex_str: LaTeX equation
            
        Returns:
            List of variable names
        """
        # Parse to SymPy
        expr = self.parse_to_sympy(latex_str)
        
        if expr:
            # Get free symbols
            variables = [str(var) for var in expr.free_symbols]
            return sorted(variables)
        
        # Fallback: simple regex extraction
        variables = re.findall(r'\\?([a-zA-Z](?:_\{[^}]+\})?)', latex_str)
        return list(set(variables))
    
    def extract_functions(self, latex_str: str) -> List[str]:
        """
        Extract function names from LaTeX equation
        
        Args:
            latex_str: LaTeX equation
            
        Returns:
            List of function names
        """
        functions = []
        
        # Common function patterns
        function_patterns = [
            r'\\(sin|cos|tan|log|ln|exp|sqrt|sum|prod|int)',
            r'([a-zA-Z]+)\(',  # Custom functions
        ]
        
        for pattern in function_patterns:
            matches = re.findall(pattern, latex_str)
            functions.extend(matches)
        
        return list(set(functions))
    
    def equation_to_python(self, latex_str: str) -> Optional[str]:
        """
        Convert LaTeX equation to Python code
        
        Args:
            latex_str: LaTeX equation
            
        Returns:
            Python code string or None
        """
        try:
            expr = self.parse_to_sympy(latex_str)
            if expr:
                # Convert to Python using SymPy's lambdify
                variables = sorted(expr.free_symbols, key=str)
                
                # Generate Python function
                python_code = f"def equation({', '.join(str(v) for v in variables)}):\n"
                python_code += f"    return {expr}\n"
                
                return python_code
        
        except Exception as e:
            logger.warning(f"Could not convert to Python: {str(e)}")
        
        return None
    
    def describe_equation(self, latex_str: str) -> Dict[str, any]:
        """
        Analyze and describe an equation
        
        Args:
            latex_str: LaTeX equation
            
        Returns:
            Dictionary with equation analysis
        """
        analysis = {
            'latex': latex_str,
            'variables': [],
            'functions': [],
            'complexity': 'unknown',
            'type': 'unknown',
            'python_code': None
        }
        
        try:
            # Extract components
            analysis['variables'] = self.extract_variables(latex_str)
            analysis['functions'] = self.extract_functions(latex_str)
            
            # Parse to SymPy
            expr = self.parse_to_sympy(latex_str)
            
            if expr:
                # Analyze complexity
                analysis['complexity'] = self._estimate_complexity(expr)
                
                # Determine equation type
                analysis['type'] = self._classify_equation(expr)
                
                # Generate Python code
                analysis['python_code'] = self.equation_to_python(latex_str)
        
        except Exception as e:
            logger.warning(f"Error analyzing equation: {str(e)}")
        
        return analysis
    
    def _estimate_complexity(self, expr: sympy.Expr) -> str:
        """Estimate computational complexity of expression"""
        # Count operations
        op_count = len(expr.atoms())
        
        if op_count < 5:
            return "simple"
        elif op_count < 15:
            return "moderate"
        else:
            return "complex"
    
    def _classify_equation(self, expr: sympy.Expr) -> str:
        """Classify the type of equation"""
        # Check for common equation types
        if expr.is_polynomial():
            return "polynomial"
        elif any(f in str(expr) for f in ['sin', 'cos', 'tan']):
            return "trigonometric"
        elif 'exp' in str(expr) or 'log' in str(expr):
            return "exponential/logarithmic"
        elif expr.has(sympy.Derivative):
            return "differential"
        elif expr.has(sympy.Integral):
            return "integral"
        else:
            return "algebraic"
    
    def batch_parse(self, text: str) -> List[Dict]:
        """
        Extract and parse all equations from text
        
        Args:
            text: Text containing LaTeX equations
            
        Returns:
            List of parsed equation analyses
        """
        equations = self.extract_latex_equations(text)
        
        results = []
        for eq in equations:
            analysis = self.describe_equation(eq['latex'])
            analysis['original_type'] = eq['type']
            analysis['position'] = eq['position']
            results.append(analysis)
        
        return results


def parse_latex(text: str) -> List[Dict]:
    """
    Convenience function to parse LaTeX from text
    
    Args:
        text: Text containing LaTeX equations
        
    Returns:
        List of parsed equations
    """
    parser = LatexParser()
    return parser.batch_parse(text)