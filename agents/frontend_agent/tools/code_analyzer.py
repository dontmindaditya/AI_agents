import re
from typing import Dict, List, Tuple


class CodeAnalyzer:
    """
    Utility class for analyzing frontend code.
    """
    
    @staticmethod
    def count_lines(code: str) -> int:
        """Count non-empty lines of code"""
        return len([line for line in code.split("\n") if line.strip()])
    
    @staticmethod
    def extract_components(code: str, framework: str) -> List[str]:
        """Extract component names from code"""
        components = []
        
        if framework == "react":
            # Match function components
            pattern = r"(?:function|const)\s+([A-Z][a-zA-Z0-9]*)\s*(?:=|\()"
            components.extend(re.findall(pattern, code))
        
        elif framework == "vue":
            # Match Vue component names
            pattern = r"name:\s*['\"]([A-Za-z0-9]+)['\"]"
            components.extend(re.findall(pattern, code))
        
        elif framework == "vanilla":
            # Match class definitions
            pattern = r"class\s+([A-Z][a-zA-Z0-9]*)"
            components.extend(re.findall(pattern, code))
        
        return list(set(components))
    
    @staticmethod
    def detect_state_management(code: str, framework: str) -> List[str]:
        """Detect state management patterns in code"""
        patterns = []
        
        if framework == "react":
            if "useState" in code:
                patterns.append("useState")
            if "useReducer" in code:
                patterns.append("useReducer")
            if "useContext" in code or "createContext" in code:
                patterns.append("Context API")
            if "Redux" in code or "useSelector" in code:
                patterns.append("Redux")
        
        elif framework == "vue":
            if "ref(" in code:
                patterns.append("ref")
            if "reactive(" in code:
                patterns.append("reactive")
            if "provide(" in code or "inject(" in code:
                patterns.append("provide/inject")
            if "usePinia" in code or "defineStore" in code:
                patterns.append("Pinia")
        
        elif framework == "vanilla":
            if "class" in code and "this." in code:
                patterns.append("Class-based state")
            if "addEventListener" in code:
                patterns.append("Event-driven")
        
        return patterns
    
    @staticmethod
    def check_best_practices(code: str, framework: str) -> Dict[str, bool]:
        """Check for common best practices"""
        checks = {
            "has_error_handling": False,
            "has_comments": False,
            "has_prop_types": False,
            "has_accessibility": False,
            "has_async_handling": False
        }
        
        # Error handling
        if "try" in code and "catch" in code:
            checks["has_error_handling"] = True
        
        # Comments
        if "//" in code or "/*" in code:
            checks["has_comments"] = True
        
        # Prop types
        if framework == "react":
            if "PropTypes" in code or "interface" in code and "Props" in code:
                checks["has_prop_types"] = True
        elif framework == "vue":
            if "props:" in code or "defineProps" in code:
                checks["has_prop_types"] = True
        
        # Accessibility
        if any(aria in code for aria in ["aria-", "role=", "alt="]):
            checks["has_accessibility"] = True
        
        # Async handling
        if "async" in code or "await" in code or ".then(" in code:
            checks["has_async_handling"] = True
        
        return checks
    
    @staticmethod
    def extract_imports(code: str) -> List[str]:
        """Extract import statements"""
        import_pattern = r"import\s+.*?from\s+['\"]([^'\"]+)['\"]"
        return re.findall(import_pattern, code)
    
    @staticmethod
    def calculate_complexity_score(code: str) -> Tuple[int, str]:
        """Calculate a simple complexity score"""
        score = 0
        
        # Count decision points
        score += code.count("if ")
        score += code.count("else ")
        score += code.count("switch ")
        score += code.count("for ")
        score += code.count("while ")
        score += code.count("? ") * 0.5  # Ternary operators
        
        # Determine complexity level
        if score < 5:
            level = "Low"
        elif score < 15:
            level = "Medium"
        else:
            level = "High"
        
        return int(score), level