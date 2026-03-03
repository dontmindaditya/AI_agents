from typing import List, Dict, Tuple
import re


class ComponentValidator:
    """
    Utility class for validating frontend components.
    """
    
    @staticmethod
    def validate_syntax(code: str, framework: str) -> Tuple[bool, List[str]]:
        """Basic syntax validation"""
        errors = []
        
        # Check for balanced braces
        if code.count("{") != code.count("}"):
            errors.append("Unbalanced curly braces")
        
        # Check for balanced parentheses
        if code.count("(") != code.count(")"):
            errors.append("Unbalanced parentheses")
        
        # Check for balanced brackets
        if code.count("[") != code.count("]"):
            errors.append("Unbalanced square brackets")
        
        # Framework-specific checks
        if framework == "react":
            # Check for JSX closing tags
            jsx_opens = len(re.findall(r"<([A-Z][a-zA-Z0-9]*)", code))
            jsx_closes = len(re.findall(r"</([A-Z][a-zA-Z0-9]*)", code))
            self_closing = len(re.findall(r"<[A-Z][a-zA-Z0-9]*[^>]*/>", code))
            
            if jsx_opens != (jsx_closes + self_closing):
                errors.append("Potentially unmatched JSX tags")
        
        elif framework == "vue":
            # Check for template structure
            if "<template>" in code and "</template>" not in code:
                errors.append("Unclosed <template> tag")
            if "<script>" in code and "</script>" not in code:
                errors.append("Unclosed <script> tag")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_structure(code: str, framework: str) -> Tuple[bool, List[str]]:
        """Validate component structure"""
        warnings = []
        
        if framework == "react":
            # Check for export
            if "export" not in code:
                warnings.append("No export statement found")
            
            # Check for component definition
            if not re.search(r"(?:function|const)\s+[A-Z]", code):
                warnings.append("No component definition found")
        
        elif framework == "vue":
            # Check for template
            if "<template>" not in code:
                warnings.append("No template section found")
            
            # Check for script
            if "<script" not in code:
                warnings.append("No script section found")
        
        elif framework == "vanilla":
            # Check for class or function
            if "class " not in code and "function " not in code:
                warnings.append("No class or function definition found")
        
        return len(warnings) == 0, warnings
    
    @staticmethod
    def validate_props(code: str, framework: str) -> Tuple[bool, List[str]]:
        """Validate prop definitions"""
        issues = []
        
        if framework == "react":
            # Check if props are used but not typed
            if "props." in code and "PropTypes" not in code and "interface" not in code:
                issues.append("Props used but not typed")
        
        elif framework == "vue":
            # Check for prop definitions
            if "props." in code and "props:" not in code and "defineProps" not in code:
                issues.append("Props used but not defined")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_accessibility(code: str) -> Tuple[int, List[str]]:
        """Check accessibility features (score 0-100)"""
        score = 0
        suggestions = []
        
        # Check for ARIA labels
        if "aria-label" in code or "aria-labelledby" in code:
            score += 25
        else:
            suggestions.append("Consider adding ARIA labels")
        
        # Check for semantic HTML
        semantic_tags = ["nav", "main", "header", "footer", "article", "section"]
        if any(f"<{tag}" in code for tag in semantic_tags):
            score += 25
        else:
            suggestions.append("Use semantic HTML elements")
        
        # Check for alt text on images
        if "<img" in code:
            if "alt=" in code:
                score += 25
            else:
                suggestions.append("Add alt text to images")
        else:
            score += 25  # No images, no issue
        
        # Check for keyboard navigation
        if "onKeyDown" in code or "onKeyPress" in code or "tabIndex" in code:
            score += 25
        else:
            suggestions.append("Consider keyboard navigation")
        
        return score, suggestions
    
    @staticmethod
    def validate_performance(code: str, framework: str) -> Tuple[int, List[str]]:
        """Check for performance considerations (score 0-100)"""
        score = 100
        issues = []
        
        if framework == "react":
            # Check for unnecessary re-renders
            if "useState" in code and "useCallback" not in code and "useMemo" not in code:
                score -= 20
                issues.append("Consider using useCallback/useMemo for optimization")
            
            # Check for key props in lists
            if ".map(" in code and 'key=' not in code:
                score -= 30
                issues.append("Add key props to list items")
        
        elif framework == "vue":
            # Check for v-for key
            if "v-for" in code and ":key" not in code:
                score -= 30
                issues.append("Add :key to v-for directives")
        
        # Check for large inline functions
        inline_functions = len(re.findall(r"=>\s*{[^}]{100,}", code))
        if inline_functions > 3:
            score -= 15
            issues.append(f"Consider extracting {inline_functions} large inline functions")
        
        return max(0, score), issues
    
    @staticmethod
    def comprehensive_validation(code: str, framework: str) -> Dict:
        """Run all validations and return comprehensive report"""
        syntax_valid, syntax_errors = ComponentValidator.validate_syntax(code, framework)
        structure_valid, structure_warnings = ComponentValidator.validate_structure(code, framework)
        props_valid, props_issues = ComponentValidator.validate_props(code, framework)
        accessibility_score, accessibility_suggestions = ComponentValidator.validate_accessibility(code)
        performance_score, performance_issues = ComponentValidator.validate_performance(code, framework)
        
        overall_valid = syntax_valid and structure_valid and props_valid
        
        return {
            "is_valid": overall_valid,
            "syntax": {
                "valid": syntax_valid,
                "errors": syntax_errors
            },
            "structure": {
                "valid": structure_valid,
                "warnings": structure_warnings
            },
            "props": {
                "valid": props_valid,
                "issues": props_issues
            },
            "accessibility": {
                "score": accessibility_score,
                "suggestions": accessibility_suggestions
            },
            "performance": {
                "score": performance_score,
                "issues": performance_issues
            }
        }